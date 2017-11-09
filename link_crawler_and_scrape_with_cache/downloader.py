#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
下载类
我们期望在这个类中实现以下功能：
    1.设置用户代理
    2.切换代理
    3.设定链接超时
    4.服务器5xx错误重下载
    5.配置缓存
    6.下载限速，避免IP被禁
'''

import logging
import requests
from throttle import Throttle
from random import choice

class Downloader(object):
    def __init__(self,user_agent='wswp',proxies=None,delay=5,cache={},timeout=60):
        self.user_agent = user_agent
        self.proxies = proxies
        self.cache = cache
        self.throttle = Throttle(delay)
        self.timeout = timeout

    def download(self,url,headers,proxies,num_retries=2):
        logging.info('Downloading %s' % url)
        try:
            resp = requests.get(url,headers=headers,proxies=proxies,timeout=self.timeout)
            html = resp.text

            if resp.status_code >= 400:
                logging.info('Download error:%s' % url)
                html = None

                if num_retries and resp.status_code >= 500 and resp.status_code < 600:
                    return self.download(url,headers,proxies,num_retries - 1)
        except requests.exceptions.RequestException as e:
            logging.info('Download error:%s' % e)
            return {'html':None,'code':500}

        return {'html':html,'code':resp.status_code}

    def __call__(self,url,num_retries=2):
        #read cache
        try:
            result = self.cache[url]
            logging.info('Loaded from cache:%s' % url)
        except KeyError:
            result = None

        if result and result['code'] >= 500 and result['code'] < 600:
            result = None

        if result is None:
            self.throttle.wait(url)
            headers = {'User-Agent':self.user_agent}
            proxies = choice(self.proxies) if self.proxies else None
            result = self.download(url,headers,proxies,num_retries=num_retries)
            self.cache[url] = result
        
        return result['html']
