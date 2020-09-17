import scrapy
from scrapy.loader import ItemLoader
import pandas as pd
from Levenshtein import distance

from gsmarena_crawler.items import Device


class PhonesSpider(scrapy.Spider):
    name = "phones"

    def __init__(self, csv_file='', **kwargs):
        self.csv_file = csv_file
        super().__init__(**kwargs)

    def start_requests(self):
        urls = self.get_start_urls()
        for name, url in urls:
            yield scrapy.Request(url=url, callback=self.search, meta={'name': name})

    def search(self, response):
        search_name = response.meta.get('name')
        min_dist = None
        next_url = ''
        device_name = ''
        for device in response.xpath("//div[@class='makers']/ul/li/a"):
            name = ' '.join(device.css("strong").xpath("span/text()").getall())
            dist = distance(name.lower(), search_name.lower())
            if not min_dist or dist < min_dist:
                min_dist = dist
                next_url = device.xpath("@href").get()
                device_name = name
        if next_url and device_name:
            yield response.follow(next_url, callback=self.parse, meta={'device_name': device_name,
                                                                       'name': search_name})

    def parse(self, response, **kwargs):
        device_loader = ItemLoader(item=Device(), response=response)
        device_loader.add_value('name', response.meta.get('device_name'))
        device_loader.add_xpath('size', "//table/tbody/tr/td/a[text()='Size']/../../td[@class='nfo']")
        device_loader.add_xpath('resolution', "//table/tbody/tr/td/a[text()='Resolution']/../../"
                                              "td[@class='nfo']/text()")
        item = device_loader.load_item()
        print('Item')
        print(item)
        return item

    def get_start_urls(self):
        df = pd.read_csv(self.csv_file)
        device_names = df['name'].str.strip('"').tolist()
        return [(name, f'https://www.gsmarena.com/res.php3?sSearch={name}') for name in device_names]
