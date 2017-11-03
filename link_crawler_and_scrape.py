#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import requests
from urllib import robotparser
from urllib.parse import urljoin
from lxml.html import fromstring,tostring
from throttle import throttle
from callback import csvCallback

def download(url,num_retries=2,user_agent='wswp',proxies=None):
    headers = {'User-Agent':user_agent}
    
    print('Downloading %s...' % url)
    try:
        resp = requests.get(url,headers=headers,proxies=proxies)
        html = resp.text

        if resp.status_code >= 400:
            html = None
            print('Download error:%s' % url)

            if num_retries and resp.status_code >= 500 and resp.status_code < 600:
                return download(url,num_retries - 1,user_agent,proxies)

    except requests.exceptions.RequestException as e:
        print('Download error:%s' % e)
        html = None

    return html

def get_robots_parser(robots_url):
    rp = robotparser.RobotFileParser()
    rp.set_url(robots_url)
    rp.read()
    return rp

def get_links(html):
    webpage_regex = re.compile("""<a[^>]+href=["'](.*?)["']""")
    return webpage_regex.findall(html)

def crawl_queue(start_url,link_regex,robots_url=None,user_agent='wswp',proxies=None,delay=3,max_depth=4,scrape_callback=None):
    crawl_queue = [start_url]
    seen = {}

    if not robots_url:
        robots_url = '{}/robots.txt'.format(start_url)

    rp = get_robots_parser(robots_url)
    Throttle = throttle(delay)

    while crawl_queue:
        url = crawl_queue.pop()

        if rp.can_fetch(user_agent,url):
            depth = seen.get(url,0)
            if depth == max_depth:
                print('Skipping %s due to depth' % url)
                continue
            Throttle.wait(url)
            html = download(url,user_agent=user_agent,proxies=proxies)

            if not html:
                continue

            #scrape data from html page
            if scrape_callback:
                scrape_callback(url,html)

            #check links from html page
            for link in get_links(html):
                if re.match(link_regex,link):
                    abs_link = urljoin(start_url,link)
                    if abs_link not in seen:
                        seen[abs_link] = depth + 1
                        crawl_queue.append(abs_link)

        else:
            print('Blocked by robots.txt:%s' % url)

if __name__ == '__main__':
    start_url = 'http://example.webscraping.com/index'
    link_regex = r'/places/default/(index|view)'
    robots_url = 'https://webscraping.com/robots.txt'
    crawl_queue(start_url,link_regex,robots_url=robots_url,scrape_callback=csvCallback())
