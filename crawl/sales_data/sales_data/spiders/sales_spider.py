import scrapy
from ..items import SalesDataItem
import datetime
from inventorymanager.models import Sku, Customer
import dill


class SalesSpider(scrapy.Spider):
    name = "sales"
    start_urls  = [
        'http://hypomeals-sales.colab.duke.edu:8080/'
    ]
    year_sku = []
    years = list(range(2010, 2020))
    skus = Sku.objects.all().values_list('id', flat=True)
    for sku in skus:
        for year in years:
            year_sku.append((str(year), str(sku)))  

    def parse(self, response):
        if len(self.year_sku) == 0:
            return
        year, sku = self.year_sku.pop()
        return scrapy.FormRequest.from_response(
            response,
            formdata={'sku': sku, 'year': year},
            callback=self.parse_sales
        )
    
    def parse_sales(self, response):
        attr_names = ['year', 'sku', 'week', 'cust_id', 'cust_name', 'sales', 'price_per_case']
        all_row_data = response.xpath('//td/text()').getall()
        num_row = int(len(all_row_data) / len(attr_names))
        for row_idx in range(num_row):
            row_data = all_row_data[row_idx*len(attr_names):(row_idx+1)*len(attr_names)]
            data = {}
            for i in range(len(attr_names)):
                data[attr_names[i]] = row_data[i].rstrip()
            # print('crawled data: ')
            # print(data)
            d = data['year'] + "-W" + data['week']
            date = datetime.datetime.strptime(d + '-1', "%Y-W%W-%w")
            # if sku does not exist, skip 
            if not Sku.objects.filter(id=data['sku']).exists():
                continue
            sku = Sku.objects.get(id=data['sku'])
            # if customer does not exist, skip 
            if not Customer.objects.filter(id=data['cust_id']).exists():
                continue
            customer = Customer.objects.get(id=data['cust_id'])
            sale_item = SalesDataItem(
                sku=sku, 
                sale_date=date, 
                customer_id=customer, 
                customer_name=data['cust_name'], 
                sales=data['sales'],
                price_per_case=data['price_per_case'])
            yield sale_item
        
        if not len(self.year_sku) == 0:
            yield scrapy.Request(self.start_urls[0], callback=self.parse, dont_filter=True)