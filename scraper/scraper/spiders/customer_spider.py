import scrapy
from ..items import SalesDataItem, CustomerItem
import datetime
from inventorymanager.models import Sku, Customer


class SalesSpider(scrapy.Spider):
    name = "customer"
    start_urls  = [
        'http://hypomeals-sales.colab.duke.edu:8080/customers'
    ]

    def parse(self, response):
        all_row_data = response.xpath('//td/text()').getall()
        num_row = int(len(all_row_data) / 2)
        for row_idx in range(num_row):
            row_data = all_row_data[row_idx*2:(row_idx+1)*2]
            cust_id = row_data[0].rstrip()
            cust_name = row_data[1].rstrip()
            if Customer.objects.filter(id=cust_id, name=cust_name).exists():
                continue
            customer_item = CustomerItem(
                id = cust_id,
                name = cust_name
            )
            customer_item.save()
            yield customer_item
    