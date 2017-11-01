#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import urllib.request
from urllib import robotparser
from urllib.parse import urljoin
from urllib.error import URLError,HTTPError,ContentTooShortError
from throttle import throttle

def download(url,numRetries=2,userAgent='wswp',charset='utf-8',proxy=None):
    '''
    1.retrying downloads
    2.setting a user agent
    3.support proxy
    '''

    print('Downloading %s...' % url)
    #create request object
    request = urllib.request.Request(url)
    #set user agent
    request.add_header('User-agent',userAgent)

    try:
        #support proxy
        if proxy:
            proxySupport = urllib.request.ProxyHandler({'http':proxy})
            #create a opener
            opener = urllib.request.bulid_opener(proxySupport)
            #all urllin.request.urlopen throuth the opener
            urllib.request.install_opener(opener)

        resp = urllib.request.urlopen(request)
        #get html content charset
        cs = resp.headers.get_content_charset()
        if not cs:
            cs = charset
        html = resp.read().decode(cs)

    except (URLError,HTTPError,ContentTooShortError) as e:
        print('Download error:%s' % e.reason)
        html = None

        #retrying download
        if numRetries > 0:
            if hasattr(e,'code') and e.code >= 500 and e.code < 600:
                return download(url,numRetries - 1,userAgent,charset,proxy)

    return html

def get_robots_parser(robotsURL):
    rp = robotparser.RobotFileParser()
    rp.set_url(robotsURL)
    rp.read()
    return rp

def get_links(html):
    webpage_regex = re.compile("""<a[^>]+href=["'](.*?)["']""", re.IGNORECASE)
    return webpage_regex.findall(html)

def link_crawler(startURL,linkRegex,robotsURL=None,userAgent='wswp',proxy=None,delay=3,maxDepth=4):
    #download queue
    crawlQueue = [startURL]
    #save url depth and avoid download same url
    seen = {}

    #get robots.txt
    if not robotsURL:
        robotsURL = '{}/robots.txt'.format(startURL)
    rp = get_robots_parser(robotsURL)

    Throttle = throttle(delay)

    #begin to crawl
    while crawlQueue:
        url = crawlQueue.pop()
        #check url
        if rp.can_fetch(userAgent,url):
            depth = seen.get(url,0)
            if depth == maxDepth:
                print('Skipping %s due depth' % url)
                continue
            Throttle.wait(url)
            html = download(url,userAgent=userAgent,proxy=proxy)
            
            if not html:
                continue
            
            #add link to crawl queue
            for link in get_links(html):
                #filter link
                if re.match(linkRegex,link):
                    absLink = urljoin(startURL,link)
                    
                    #filter already crawled link
                    if absLink not in seen:
                        seen[absLink] = depth + 1
                        crawlQueue.append(absLink)
        else:
            print('Blocked by robots.txt:%s' % url)

if __name__ == '__main__':
    startURL = 'http://example.webscraping.com/index'
    linkRegex = r'/places/default/(index|view)'
    robotsURL = 'https://webscraping.com/robots.txt'
    link_crawler(startURL,linkRegex,robotsURL=robotsURL,maxDepth=3)
