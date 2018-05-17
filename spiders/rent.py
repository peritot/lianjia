# -*- coding: utf-8 -*-
import scrapy
import re

from lianjia.items import RentItem

disPattern = re.compile('<p>.*?<a.*?>(.*?)</a>.*?</p>', re.S)
zipPattern = re.compile('<script>.*?cityId:\'(.*?)\'.*?</script>', re.S)
llPattern = re.compile('<script>.*?resblockPosition:\'(.*?)\',.*?</script>', re.S)

class RentSpider(scrapy.Spider):
    name = 'rent'
    allowed_domains = ['lianjia.com']

    def start_requests(self):
        for i in range(1, 2):
            url = 'https://wh.lianjia.com/zufang/pg{pg}'.format(pg=i)
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        for li in response.css('#house-lst li'):
            item = RentItem()
            item['title'] = li.css('.info-panel h2 a::text').extract()[0].strip()
            item['community'] = li.css('.region::text').extract()[0].strip()
            item['zone'] = li.css('.zone span::text').extract()[0].strip()
            item['area'] = li.css('.meters::text').extract()[0].strip()
            item['price'] = li.css('.price .num::text').extract()[0].strip()
            item['time'] = li.css('.price-pre::text').extract()[0].strip()
            item['link'] = li.css('.info-panel h2 a::attr(href)').extract()[0].strip()

            yield scrapy.Request(item['link'], callback=self.parse_detail, meta={'item': item})

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
