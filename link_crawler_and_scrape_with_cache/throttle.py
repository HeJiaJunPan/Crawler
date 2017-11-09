#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
我们期望在这个类中实现下列功能：
    对于同一域名，链接限速
'''

import time
from urllib.parse import urlparse

class Throttle(object):
    def __init__(self,delay):
        self.delay = delay
        self.domains = {}

    def wait(self,url):
        #get domain of url
        domain = urlparse(url).netloc
        if domain in self.domains:
            lasttime = self.domains.get(domain,0)
            if (time.time() - lasttime) < self.delay:
                time.sleep(self.delay)

        self.domains[domain] = time.time()
