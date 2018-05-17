# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LianjiaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class RentItem(scrapy.Item):
    # 标识 标签 城区 小区 户型 面积 价格 链接 时间 链接 经纬度
    id = scrapy.Field()
    title = scrapy.Field()
    district = scrapy.Field()
    community = scrapy.Field()
    zone = scrapy.Field()
    area = scrapy.Field()
    price = scrapy.Field()
    time = scrapy.Field()
    link = scrapy.Field()
    zip = scrapy.Field()
    longitude = scrapy.Field()
    latitude = scrapy.Field()
