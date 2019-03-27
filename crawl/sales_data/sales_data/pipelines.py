# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import datetime
from .items import SalesDataItem
import psycopg2

class SalesDataPipeline(object):

    def process_item(self, item, spider):
        print('pipelines for scrapy----saved item: ')
        print(item)
        item.save()
        print(dill.pickles(item))
        return item
