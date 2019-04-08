# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from inventorymanager.models import Sale_Record, Customer
from scrapy_djangoitem import DjangoItem

class SalesDataItem(DjangoItem):
    django_model = Sale_Record

class CustomerItem(DjangoItem):
    django_model = Customer