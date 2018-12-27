# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BaiduItem(scrapy.Item):
    rank = scrapy.Field()
    name = scrapy.Field()
    trend = scrapy.Field()
    index_str = scrapy.Field()
    nav_name = scrapy.Field()
    exponent = scrapy.Field()
    week = scrapy.Field()
    # title = scrapy.Field()
