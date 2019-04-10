import scrapy
from ..items import SalesDataItem
import datetime
from inventorymanager.models import Sku, Customer, Sale_Record


class SalesSpider(scrapy.Spider):
    name = "sales"
    start_urls  = [
        'http://hypomeals-sales.colab.duke.edu:8080/'
    ]
    
    def up_to_date(self, sku):
        unique_years = set()
        sale_dates = Sale_Record.objects.filter(sku=sku).values_list('sale_date', flat=True)
        for sale_date in sale_dates:
            unique_years.add(sale_date.year)
        # 2010-2019 have 10 unique years
        return len(unique_years) == 10


    def parse(self, response):
        year_sku = []
        years = list(range(2010, 2020))
        skus = Sku.objects.all().values_list('id', flat=True)
        for sku in skus:
            # Heuristic: if SalesData contains record for this sku for years 2010-2019, then the sku is up-to-date
            if self.up_to_date(sku):
                continue
            # otherwise, scrape all years for this sku 
            for year in years:
                year_sku.append((str(year), str(sku))) 
        for year, sku in year_sku:
            yield scrapy.FormRequest.from_response(
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
            # if the exact same sale record already exist, skip 
            if Sale_Record.objects.filter(
                sku=sku, 
                sale_date=date, 
                customer_id=customer, 
                customer_name=data['cust_name'], 
                sales=data['sales'],
                price_per_case=data['price_per_case']
            ).exists():
                continue
            sale_item = SalesDataItem(
                sku=sku, 
                sale_date=date, 
                customer_id=customer, 
                customer_name=data['cust_name'], 
                sales=data['sales'],
                price_per_case=data['price_per_case'])
            sale_item.save()
            yield sale_item