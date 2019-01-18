# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import csv
import codecs
import json

class HousingPricePipeline(object):
    # def process_item(self, item, spider):
    #     return item

    def process_item(self, item, spider):
        # import ipdb; ipdb.set_trace()
        item_name = item.__class__.__name__
        
        if item_name:
            if item_name == 'HousingPriceItem':
                file = codecs.open('HousingPriceItem.json', 'a+', encoding='utf-8')
                line = json.dumps(dict(item), ensure_ascii=False, indent=4, sort_keys=True) + "\n"
                file.write(line)
                return item
            
            elif item_name == 'HousingTypeItem':
                file = codecs.open('HousingTypeItem.json', 'a+', encoding='utf-8')
                line = json.dumps(dict(item), ensure_ascii=False, indent=4, sort_keys=True) + "\n"
                file.write(line)
                return item
            
            elif item_name == 'HousingPhotoItem':
                file = codecs.open('HousingPhotoItem.json', 'a+', encoding='utf-8')
                line = json.dumps(dict(item), ensure_ascii=False, indent=4, sort_keys=True) + "\n"
                file.write(line)
                return item
            
            elif item_name == 'HousingCommentItem':
                file = codecs.open('HousingCommentItem.json', 'a+', encoding='utf-8')
                line = json.dumps(dict(item), ensure_ascii=False, indent=4, sort_keys=True) + "\n"
                file.write(line)
                return item

            else:
                file.close()
                return item

    