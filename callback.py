#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import csv
from lxml.html import fromstring

class csvCallback(object):
    def __init__(self):
        self.writer = csv.writer(open('./countries.csv','w'))
        self.fields = ('area', 'population', 'iso', 'country', 'capital',
            'continent', 'tld', 'currency_code', 'currency_name',
            'phone', 'postal_code_format', 'postal_code_regex',
            'languages', 'neighbours'
        )

        self.writer.writerow(self.fields)

    def __call__(self,url,html):
        if re.match(r'http://example.webscraping.com/places/default/view/',url):
            print('Saving %s...' % url)
            tree = fromstring(html)
            all_rows = [
                tree.xpath('//tr[@id="places_%s__row"]/td[@class="w2p_fw"]' % field)[0].text_content() for field in self.fields]
        
            self.writer.writerow(all_rows)
            print('Save successful')
