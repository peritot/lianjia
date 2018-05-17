# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
from scrapy import log

from lianjia import properties
from lianjia.items import RentItem


class LianjiaPipeline(object):
    def __init__(self):
        self.connect = pymysql.connect(
            host=properties.MYSQL_HOST,
            port=properties.MYSQL_PORT,
            user=properties.MYSQL_USER,
            password=properties.MYSQL_PASSWORD,
            db=properties.MYSQL_DB,
            use_unicode=True,
            charset='utf8'
        )
        self.cursor = self.connect.cursor()

    def process_item(self, item, spider):
        try:
            table = 'lianjia_rent'
            keys = ', '.join(item.keys())
            values = ', '.join(['%s'] * len(item))
            sql = 'INSERT INTO {table}({keys}) VALUES ({values}) ON DUPLICATE KEY UPDATE'.format(table=table, keys=keys, values=values)
            sql += ','.join([" {key} = %s".format(key=key) for key in item])

            cursor = self.connect.cursor()
            if cursor.execute(sql, tuple(item.values()) * 2):
                self.connect.commit()
        except Exception as error:
            log(error)
            self.connect.rollback()
        return item
