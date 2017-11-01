#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
Throttling downloads
If we crawl a website too quickly,we risk being blocked or overloading the server.
To minimize these risks,we can add a delay between downloads to the same domain.
'''

from urllib.parse import urlparse
import time

class throttle(object):
    def __init__(self,delay):
        self.delay = delay
        #save last accessed time for domain
        self.domain = {}

    def wait(self,url):
        #get domain
        domain = urlparse(url).netloc
        lastAccessed = self.domain.get(domain,None)

        if self.delay > 0 and lastAccessed:
            sleepTime = self.delay - (time.time() - lastAccessed)
            if sleepTime > 0:
                time.sleep(sleepTime)

        #update last accessed time
        self.domain[domain] = time.time()
