# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class HousingPriceItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 小区名
    architecture_name = scrapy.Field()
    # 房屋类型
    tenement_class = scrapy.Field()
    # 平均价格
    avg_price = scrapy.Field()
    # 特色
    feature = scrapy.Field()
    # 建筑类别
    Building = scrapy.Field()
    # 产权年限
    period_int = scrapy.Field()
    # 环线位置
    location = scrapy.Field()
    # 开发商
    developers = scrapy.Field()
    # 楼盘地址
    house_address = scrapy.Field()
    # 销售状态
    sales_status = scrapy.Field()
    # 开盘时间
    start_time = scrapy.Field()
    # 交房时间
    end_time = scrapy.Field()
    # 销售地址
    sales_address = scrapy.Field()
    # 咨询电话
    hotline = scrapy.Field()
    # 助理户型
    hot_sale_class = scrapy.Field()
    # 交通
    traffic = scrapy.Field()
    # 幼儿园
    nursery = scrapy.Field()
    # 中小学 
    middle_primary_school = scrapy.Field()
    # 大学
    college = scrapy.Field()
    # 综合商场
    shop = scrapy.Field()
    # 医院
    hospital = scrapy.Field()
    # 银行
    bank = scrapy.Field()
    # 其他
    rest = scrapy.Field()
    # # 小区内部配套
    facility = scrapy.Field()
    # 占地面积
    floor_space = scrapy.Field()
    # 建筑面积
    structure_space = scrapy.Field()
    # 容积率
    plot_ratio = scrapy.Field()
    # 停车位
    parking_spot = scrapy.Field()
    # 总户数
    total_population = scrapy.Field()
    # 楼栋总数
    total_building = scrapy.Field()
    # 物业费
    tenement_fee = scrapy.Field()
    # 物业费描述
    tenement_fee_describe = scrapy.Field()
    # 楼层状况
    condition_status = scrapy.Field()
    # 物业公司
    tenement_company = scrapy.Field()

class HousingTypeItem(scrapy.Item):
    architecture_name = scrapy.Field()
    house_class = scrapy.Field()
    house_area = scrapy.Field()
    house_link = scrapy.Field()
    house_type_photos = scrapy.Field()
    house_describe = scrapy.Field()

class HousingPhotoItem(scrapy.Item):
    architecture_name = scrapy.Field()
    photos = scrapy.Field()

class HousingCommentItem(scrapy.Item):
    architecture_name = scrapy.Field()
    grade = scrapy.Field()
    

