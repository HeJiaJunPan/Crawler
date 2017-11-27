#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import csv
import requests
from io import TextIOWrapper,BytesIO
from zipfile import ZipFile

class AlexaCallback(object):
    def __init__(self,max_urls=500):
        self.max_urls = max_urls
        self.seed_url = 'http://s3.amazonaws.com/alexa-static/top-1m.csv.zip'
        self.urls = []

    def __call__(self):
        resp = requests.get(self.seed_url,stream=True)
        with ZipFile(BytesIO(resp.content)) as zf:
            csv_filename = zf.namelist()[0]
            with zf.open(csv_filename) as csv_file:
                for _,website in csv.reader(TextIOWrapper(csv_file)):
                    self.urls.append('http://www.' + website)
                    if len(self.urls) >= self.max_urls:
                        break


if __name__ == '__main__':
    alexa = AlexaCallback(6)
    alexa()
    for url in alexa.urls:
        print(url)
