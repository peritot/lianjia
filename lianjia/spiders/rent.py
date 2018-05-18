# -*- coding: utf-8 -*-
import scrapy
import requests
import time
import re
from scrapy import log

from lianjia import properties
from lianjia.items import RentItem

numPattern = re.compile(r'[1-9]\d*')
disPattern = re.compile('<p>.*?<a.*?>(.*?)</a>.*?</p>', re.S)
zipPattern = re.compile('<script>.*?cityId:\'(.*?)\'.*?</script>', re.S)
llPattern = re.compile('<script>.*?resblockPosition:\'(.*?)\',.*?</script>', re.S)

PROXY_ENABLE = properties.PROXY_ENABLE
PROXY_POOL_URL = properties.PROXY_POOL_URL


class RentSpider(scrapy.Spider):
    name = 'rent'
    allowed_domains = ['lianjia.com']
    start_urls = ['https://wh.lianjia.com/zufang']

    def get_proxy(self):
        if PROXY_ENABLE != True:
            return ''

        try:
            response = requests.get(PROXY_POOL_URL)
            if response.status_code == 200:
                log('Using proxy: ' + str(response.text))
                return response.text
        except ConnectionError:
            return ''

    def parse(self, response):
        for href in response.css('#filter-options dd[data-index="0"] .option-list a[class!="on"]::attr(href)').extract():
            try:
                href = 'https://wh.lianjia.com' + href
                proxy = self.get_proxy()
                yield scrapy.Request(href, callback=self.parse_district, meta={'proxy': proxy})
            except Exception as error:
                log(error)

    def parse_district(self, response):
        for href in response.css('#filter-options dd[data-index="0"] .sub-option-list a[class!="on"]::attr(href)').extract():
            try:
                href = 'https://wh.lianjia.com' + href
                proxy = response.meta['proxy']
                yield scrapy.Request(href, callback=self.parse_street, meta={'proxy': proxy})
            except Exception as error:
                log(error)

    def parse_street(self, response):
        try:
            url = 'https://wh.lianjia.com' + response.css('.house-lst-page-box::attr(page-url)').extract()[0].strip()
            pgdata = response.css('.house-lst-page-box::attr(page-data)').extract()[0].strip()
            pgdict = eval(pgdata)
            total = pgdict['totalPage']
            for pg in range(1, total):
                href = url.replace('{page}', str(pg))
                proxy = self.get_proxy()
                yield scrapy.Request(href, callback=self.parse_pg, meta={'proxy': proxy})
        except Exception as error:
            log(error)

    def parse_pg(self, response):
        for li in response.css('#house-lst li'):
            try:
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

                proxy = response.meta['proxy']
                yield scrapy.Request(link, callback=self.parse_detail, meta={'proxy': proxy, 'item': item})
            except Exception as error:
                log(error)

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

            return item
        except Exception:
            return item
