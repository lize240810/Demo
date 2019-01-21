# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import csv
import codecs
import json
import pymongo
from scrapy.conf import settings

# class HousingPricePipeline(object):
    # def process_item(self, item, spider):
    #     return item
    # HousingPriceItem_file = codecs.open('HousingPriceItem.json', 'w+', encoding='utf-8')
    # HousingTypeItem_file = codecs.open('HousingTypeItem.json', 'w+', encoding='utf-8')
    # HousingPhotoItem_file = codecs.open('HousingPhotoItem.json', 'w+', encoding='utf-8')
    # HousingCommentItem_file = codecs.open('HousingCommentItem.json', 'w+', encoding='utf-8')
    
    # def process_item(self, item, spider):
    #     # import ipdb; ipdb.set_trace()
    #     item_name = item.__class__.__name__
        
    #     if item_name:
    #         if item_name == 'HousingPriceItem':
    #             line = json.dumps(dict(item), ensure_ascii=False, indent=4, sort_keys=True) + "\n"
    #             self.HousingPriceItem_file.write(line)
    #             return item
            
    #         elif item_name == 'HousingTypeItem':
    #             line = json.dumps(dict(item), ensure_ascii=False, indent=4, sort_keys=True) + "\n"
    #             self.HousingTypeItem_file.write(line)
    #             return item
            
    #         elif item_name == 'HousingPhotoItem':
    #             line = json.dumps(dict(item), ensure_ascii=False, indent=4, sort_keys=True) + "\n"
    #             self.HousingPhotoItem_file.write(line)
    #             return item
            
    #         elif item_name == 'HousingCommentItem':
    #             line = json.dumps(dict(item), ensure_ascii=False, indent=4, sort_keys=True) + "\n"
    #             self.HousingCommentItem_file.write(line)
    #             return item

            # else:
            #     self.'{0}_file'.format(item_name).close()
            #     return item

    

class HousingPricePipeline(object):
    host = settings["MONGODB_HOST"]
    port = settings["MONGODB_PORT"]
    dbname = settings["MONGODB_DBNAME"]

    # 创建MONGODB数据库链接
    client = pymongo.MongoClient(host=host, port=port)
    # 指定数据库
    mydb = client[dbname]


    def process_item(self, item, spider):
        item_name = item.__class__.__name__
        # import ipdb; ipdb.set_trace()
        self.post = self.mydb[item_name]

        data = dict(item)
        self.post.insert(data)
        return item
