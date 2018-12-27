# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
import pymongo
import time

class BaiduPipeline(object):
    def process_item(self, item, spider):
        return item

class MongoPipeline(object):
    collection_name = 'rate_item'
    def __init__(self, mongp_url, mongo_db):
        self.mongp_url = mongp_url
        self.mongo_db = mongo_db


    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongp_url = crawler.settings.get('MONGP_URL'),
            mongo_db = crawler.settings.get('MONGO_DATABASE', 'items')
        )


    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongp_url)
        self.db = self.client[self.mongo_db]


    def close_spider(self, spider):
        self.client.close()


    def process_item(self, item, spider):
        # time.sleep(1)
        # import ipdb as pdb; pdb.set_trace()
        title_name = spider.title_name
        print(title_name)
        self.db[title_name].insert(dict(item))
        return item
        
        
        
