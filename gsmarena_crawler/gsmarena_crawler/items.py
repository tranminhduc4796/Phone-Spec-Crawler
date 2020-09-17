# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst
from w3lib.html import remove_tags
import re


def parse_size(value):
    pattern = r'(\d*\.?\d*) inches'
    candidates = re.findall(pattern, value)
    if candidates:
        return float(candidates[0])


def parse_resolution(value):
    pattern = r'(\d*) x (\d*) pixels'
    candidates = re.findall(pattern, value)
    if candidates:
        width, height = candidates[0]
        return {
            'width': int(width),
            'height': int(height)
        }


class Device(scrapy.Item):
    # define the fields for your item here:
    name = scrapy.Field(output_processor=TakeFirst())
    resolution = scrapy.Field(input_processor=MapCompose(remove_tags, parse_resolution),
                              output_processor=TakeFirst())
    size = scrapy.Field(input_processor=MapCompose(remove_tags, parse_size),
                        output_processor=TakeFirst())
