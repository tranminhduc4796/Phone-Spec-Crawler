import scrapy
from scrapy.loader import ItemLoader
import pandas as pd
from Levenshtein import distance

from gsmarena_crawler.items import Device


class PhonesSpider(scrapy.Spider):
    name = "phones"

    def __init__(self, csv_file='', **kwargs):
        self.csv_file = csv_file
        self.brand_names = {'AMAZON', 'ASUS', 'ESSENTIAL PRODUCTS', 'GOOGLE',
                            'HMD GLOBAL', 'HONEYWELL', 'HTC', 'HUAWEI', 'APPLE',
                            'LGE', 'LG ELECTRONICS', 'MICROSOFT',
                            'MOTOROLA', 'ONEPLUS', 'ROCKCHIP',
                            'SAMSUNG', 'SHARP', 'SONIMTECH',
                            'SONY', 'TINNO', 'XIAOMI', 'ZDMID',
                            'ZEBRA TECHNOLOGIES', 'ZTE'}
        super().__init__(**kwargs)

    def start_requests(self):
        urls = self.get_start_urls()
        for name, model_url, name_url in urls:
            yield scrapy.Request(url=model_url, callback=self.search, meta={'name': name,
                                                                            'name_url': name_url})

    def search(self, response):
        search_name = response.meta.get('name')
        std_search_name = self.standardize_device_name(search_name)
        print('Search', search_name)
        min_dist = None
        next_url = ''
        device_name = ''
        for device in response.xpath("//div[@class='makers']/ul/li/a"):
            name = ' '.join(device.css("strong").xpath("span/text()").getall())
            std_name = self.standardize_device_name(name)
            print(std_name)
            dist = distance(std_name, std_search_name)
            if min_dist is None or dist < min_dist:
                min_dist = dist
                next_url = device.xpath("@href").get()
                device_name = name
        if min_dist == 0:
            confidence = 'GOOD'
        else:
            confidence = 'NO'
        print('Result', device_name, min_dist)

        if next_url and device_name:
            yield response.follow(next_url, callback=self.parse, meta={'device_name': device_name,
                                                                       'name': search_name,
                                                                       'confidence': confidence
                                                                       })
        else:
            name_url = response.meta.get('name_url')
            if name_url:
                yield response.follow(name_url, callback=self.search,
                                      meta={'device_name': device_name,
                                            'name': search_name,
                                            'confidence': confidence}
                                      )

    def parse(self, response, **kwargs):
        device_loader = ItemLoader(item=Device(), response=response)
        device_loader.add_value('name', response.meta.get('name'))
        device_loader.add_value('device_name', response.meta.get('device_name'))
        device_loader.add_value('confidence', response.meta.get('confidence'))
        device_loader.add_xpath('size', "//a[text()='Size']/../../td[@class='nfo']")
        device_loader.add_xpath('resolution', "//a[text()='Resolution']/../../td[@class='nfo']/text()")
        yield device_loader.load_item()

    def get_start_urls(self):
        df = pd.read_csv(self.csv_file)
        device_names = df['name'].str.strip('"').tolist()
        device_models = df['model'].str.strip('"').tolist()
        return [(name,
                 f'https://www.gsmarena.com/res.php3?sSearch={model}',
                 f'https://www.gsmarena.com/res.php3?sSearch={name}')
                for name, model in zip(device_names, device_models)]

    def standardize_device_name(self, name):
        name = name.upper()
        brand_name = name.split()[0]
        if brand_name in self.brand_names:
            name = name[len(brand_name) + 1:]

        parse_words = name.split('(')
        if len(parse_words) == 2:
            model_name = parse_words[0]
            if not model_name.endswith(' '):
                return model_name + ' (' + parse_words[1]
        return name
