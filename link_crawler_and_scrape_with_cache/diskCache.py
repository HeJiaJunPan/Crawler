#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
磁盘缓存类
我们期望这个类实现下列行为：
    1.URL和文件名映射，以类似dict方式读取和保存缓存
    2.添加时间戳，以便更新缓存
    3.压缩数据，减少磁盘占用
'''

import logging
import os
import re
import json
import zlib
from urllib.parse import urlsplit
from datetime import datetime,timedelta

class DiskCache(object):
    def __init__(self,cache_dir='./data/cache',max_length=255,compress=True,encoding='utf-8',expires=timedelta(days=30)):
        self.cache_dir = cache_dir   #cache dir
        self.max_length = max_length #max filename length
        self.compress = compress     #default use compress
        self.encoding = encoding     #encode format
        self.expires = expires       #live date of cache

    def url_to_path(self,url):
        '''
        map URL to file path
        '''
        components = urlsplit(url)
        path = components.path

        if not path:
            #such as 'http://www.example.com',path is empty string
            path = 'index.html'
        elif path.endswith('/'):
            #such as 'http://www.example.com/route/'
            path += 'index.html'

        #extract netloc,path and query of url and name file
        filename = components.netloc + path + components.query
        #replace invalid characters
        filename = re.sub(r'[^/0-9a-zA-Z\-.,;_]','_',filename)
        #limit length of dirname or filename
        filename = '/'.join(seg[:self.max_length] for seg in filename.split('/'))
        #return route of cache file
        return os.path.join(self.cache_dir,filename)

    def __setitem__(self,url,result):
        '''
        save cache like dict object
        '''
        #map url to path
        path = self.url_to_path(url)
        #dir of cache file
        folder = os.path.dirname(path)
        if not os.path.exists(folder):
            #create dir and father dir
            os.path.makedirs(folder)

        mode = 'wb' if self.compress else 'w'
        #add expires time for cache
        result[expires] = (datetime.utcnow() + self.expires).isoformat(timespec='seconds')
        with open(path,mode) as f:
            if self.compress:
                data = bytes(json.dumps(result),encoding=self.encoding)
                f.write(data)
            else:
                json.dump(result,f)

    def __getitem__(self,url):
        '''
        read cache like dict object
        '''
        path = self.url_to_path(url)

        if os.path.exists(path):
            #cache file exists
            mode = 'rb' if self.compress else 'r'
            with open(path,mode) as f:
                if self.compress:
                    #decompress file
                    data = zlib.decompress(f.read()).decode(self.encoding)
                    data = json.loads(data)
                else:
                    data = json.load(f)

            #get cache expires time
            exp_date = data['expires']
            if exp_date and datetime.strptime(exp_date,'%Y-%m-%dT%H:%M:%S') <= datetime.utcnow():
                logging.info('Cache expired!',exp_date)
                raise KeyError(url + 'does not exists')
            return data
        else:
            raise KeyError(url + 'does not exists')
