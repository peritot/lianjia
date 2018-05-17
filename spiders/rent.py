# -*- coding: utf-8 -*-
import scrapy
import requests
import time
import re

from lianjia import settings
from lianjia.items import RentItem

numPattern = re.compile(r'[1-9]\d*')
disPattern = re.compile('<p>.*?<a.*?>(.*?)</a>.*?</p>', re.S)
zipPattern = re.compile('<script>.*?cityId:\'(.*?)\'.*?</script>', re.S)
llPattern = re.compile('<script>.*?resblockPosition:\'(.*?)\',.*?</script>', re.S)

PROXY_POOL_URL = settings.PROXY_POOL_URL
MAX_PAGE = settings.MAX_PAGE
proxy = ''


class RentSpider(scrapy.Spider):
    name = 'rent'
    allowed_domains = ['lianjia.com']

    def get_proxy(self):
        try:
            response = requests.get(PROXY_POOL_URL)
            if response.status_code == 200:
                return response.text
        except ConnectionError:
            return None

    def start_requests(self):
        for i in range(1, MAX_PAGE + 1):
            if i == MAX_PAGE:
                time.sleep(60 * 60)
                i = 1

            url = 'https://wh.lianjia.com/zufang/pg{pg}'.format(pg=i)
            proxy = self.get_proxy()
            print('Using proxy: ' + proxy)

            yield scrapy.Request(url, callback=self.parse, meta={'proxy': proxy})

    def parse(self, response):
        for li in response.css('#house-lst li'):
            item = RentItem()
            item['title'] = li.css('.info-panel h2 a::text').extract()[0].strip()
            item['community'] = li.css('.region::text').extract()[0].strip()
            item['zone'] = li.css('.zone span::text').extract()[0].strip()
            item['price'] = li.css('.price .num::text').extract()[0].strip()

            # area
            area = li.css('.meters::text').extract()[0].strip()
            area = re.findall(numPattern, area)[0]
            item['area'] = area

            # time
            time = li.css('.price-pre::text').extract()[0].strip()
            time = time.replace(' 更新', '').replace('.', '-')
            item['time'] = time

            # link
            link = li.css('.info-panel h2 a::attr(href)').extract()[0].strip()
            item['link'] = link
            item['id'] = re.findall(numPattern, link)[0]

            yield scrapy.Request(link, callback=self.parse_detail, meta={'proxy': proxy, 'item': item})

    def parse_detail(self, response):
        item = response.meta['item']
        try:
            res = response.css('.zf-room p').extract()[6]
            item['district'] = re.findall(disPattern, res)[0]

            res = response.text
            item['zip'] = re.findall(zipPattern, res)[0]

            ll = re.findall(llPattern, res)[0].split(',')
            item['longitude'] = ll[0]
            item['latitude'] = ll[1]
            print(item)

            return item
        except Exception:
            return item
