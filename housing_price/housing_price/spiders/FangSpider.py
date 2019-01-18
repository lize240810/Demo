# -*- coding: utf-8 -*-
import re

import scrapy
import redis
from furl import furl
from housing_price.items import HousingPriceItem, HousingTypeItem,HousingPhotoItem, HousingCommentItem


class FangspiderSpider(scrapy.Spider):
    name = 'FangSpider'
    allowed_domains = ['cq.fang.com']
    start_urls = ['https://cq.newhouse.fang.com/house/s/']
    pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)

    def parse(self, response):
        # 获取全部区域
        Quyu_dict = self.parse_district(response)
        for key in Quyu_dict:
            # 获取区链接
            yield scrapy.Request(response.urljoin(Quyu_dict[key]), callback=self.parse_houses_url, dont_filter=True)    
        
    def parse_district(self, response):
        '''
            区域存储
        '''
        quyu = response.css('li#quyu_name a')
        Quyu_Name = quyu.css('::text').extract()
        Quyu_Url = quyu.css('::attr(href)').extract()
        # 创建redis 数据库客户端
        client = redis.Redis(connection_pool=self.pool)
        # 获取
        Quyu_dict = dict(zip(Quyu_Name, Quyu_Url))
        # import ipdb as pdb; pdb.set_trace()
        Quyu_dict.pop('异地')
        Quyu_dict.pop('不限')
        # 获取重庆区字典
        for item in Quyu_dict:
            # 存储到数据库中
            client.set(item, Quyu_dict[item])
        # 获得所有的区的链接
        return Quyu_dict
        
    def parse_houses_url(self, response):
        '''
            解析楼盘链接
        '''
        # 查看总条数
        try:
            total_int = int(response.css('li.fl b::text').extract_first().strip())
        except Exception as e:
            total_int = 1
            # import ipdb as pdb; pdb.set_trace()

        total_int = int(total_int/20)+1 if total_int%20 > 0 else total_int/20
        # 构建数据路径
        page_url = 'https://cq.newhouse.fang.com/house/s/yuzhong/b9{0}/'

        for page_num in range(1, total_int+1):
            url = page_url.format(page_num)
            houses_src = list(map(lambda item: response.urljoin(item), response.css('.nlcd_name a::attr(href)').extract()))
            # import ipdb as pdb; pdb.set_trace()
            # houses_name = list(map(lambda item: item.strip(), response.css('.nlcd_name a::text').extract()))
            # 遍历请求
            for houses_item in houses_src:
                yield scrapy.Request(url=houses_item, callback=self.parse_houses_dict, dont_filter=True)

    def parse_houses_dict(self, response):
        '''
            解析楼盘链接 获得一个楼盘的不同网页
        '''

        text_template = '//div[@class="navleft tf"]/a[text()[contains(.,"{0}")]]/@href'
            # 获得楼盘的子链接
        houses = {
            'houses_describe': response.xpath(text_template.format('楼盘详情')).extract_first(), #描述
            'houses_type': response.xpath(text_template.format('户型')).extract_first(), # 类型
            'houses_photo': response.xpath(text_template.format('楼盘相册')).extract_first(), # 相册
            'houses_comment': response.xpath(text_template.format('楼盘点评')).extract_first(), # 评论
        }
        # 读取制定网页的数据
        for item in houses:
            if houses[item]:
                if item == 'houses_describe':
                    house = self.parse_housing_describe
                elif item == 'houses_type':
                    house = self.parse_housing_type
                if item == 'houses_photo':
                    house = self.parse_housing_photo
                if item == 'houses_comment':
                    house = self.parse_housing_comment
                yield scrapy.Request(response.urljoin(houses[item]), callback=house, dont_filter=True)
            else:
                print('office写字楼')

    # 楼盘详细信息
    def parse_housing_describe(self, response):
        Housing_item = HousingPriceItem()

        text_template = '//div[text()[contains(., "{0}")]]/following-sibling::div[1]'
        # 建筑名称
        Housing_item['architecture_name'] = response.css('a.ts_linear::text').extract_first().strip()
        # 楼盘链接
        Housing_item['housing_url'] = response.url

        # 物业类型
        Housing_item['tenement_class'] = response.xpath(text_template.format('物业类别')+'/text()').extract_first().strip()
        
        # 均价
        Housing_item['avg_price'] = response.css('span.tit+em::text').extract_first().strip()



        # 项目特色
        Housing_item['feature'] = '，'.join(response.xpath(text_template.format('项目特色')+'/span/text()').extract())
        # 建筑类别
        
        try:
            Building = re.sub(r'\s+', ',', response.xpath(text_template.format('建筑类别')+'/span/text()').extract_first().strip())
        except Exception as e:
            Building = response.xpath(text_template.format('写字楼级别')+'/span/text()').extract_first().strip()
        Housing_item['Building'] = Building
        # 产权年限
        try:
            period_int = response.xpath(text_template.format('产权年限')+'/div/p/text()').extract_first().strip()
        except Exception as e:
            period_int = response.xpath(text_template.format('产权年限')+'/text()').extract_first().strip()
        else:
            period_int = period_int[period_int.find(':')+1:-1]        
        Housing_item['period_int'] = period_int
        # 换线位置
        Housing_item['location'] = response.xpath(text_template.format('环线位置')+'/text()').extract_first().strip()
        # 开发商
        try:
            developers = response.xpath(text_template.format('商')+'/a/text()').extract_first().strip()
        except Exception as e:
            developers = "暂无资料"
        else:
            Housing_item['developers'] = developers
        # 楼盘地址
        Housing_item['house_address'] = response.xpath(text_template.format('楼盘地址')+'/text()').extract_first().strip()
        
        # 销售状态
        Housing_item['sales_status'] = response.xpath(text_template.format('销售状态')+'/text()').extract_first().strip()
        # 开盘时间
        Housing_item['start_time'] = response.xpath(text_template.format('开盘时间')+'/text()').extract_first().strip()
        # 交房时间
        try:
            end_time = response.xpath(text_template.format('交房时间')+'/text()').extract_first().strip()
        except Exception as e:
            end_time = None
        Housing_item['end_time'] = end_time
        # 售楼地址
        Housing_item['sales_address'] = response.xpath(text_template.format('售楼地址')+'/text()').extract_first().strip()
        # 咨询电话
        try:
            hotline = response.xpath(text_template.format('咨询电话')+'/text()').extract_first().strip()
        except Exception as e:
            hotline = None
        Housing_item['hotline'] = 'hotline'
        # 助理户型
        Housing_item['hot_sale_class'] = list(map(lambda item: item.strip(), response.xpath(text_template.format('主力户型')+'/a/text()').extract()))
        
        # 交通
        per_temp = '//li/span[text()[contains(.,"{0}")]]/../text()'
        Housing_item['traffic'] = ''.join(response.css('li.jiaotong_color::text').extract()).strip()
        # 幼儿园
        try:
            nursery = response.xpath(per_temp.format("幼儿园")).extract_first().strip()
        except Exception as e:
            nursery = "暂无资料"
        Housing_item['nursery'] = nursery
        # 中小学 
        try:
            middle_primary_school = response.xpath(per_temp.format("中小学")).extract_first().strip()
        except Exception as e:
            middle_primary_school = "暂无资料"
        Housing_item['middle_primary_school'] = middle_primary_school
        # 大学
        try:
            college = response.xpath(per_temp.format("大学")).extract_first().strip()
        except Exception as e:
            college = "暂无资料"
        Housing_item['college'] = college
        # 综合商场
        try:
            shop = response.xpath(per_temp.format("综合商场")).extract_first().strip()
        except Exception as e:
            shop = "暂无资料"
        Housing_item['shop'] = shop
        # 医院
        try:
            hospital = response.xpath(per_temp.format("医院")).extract_first().strip()
        except Exception as e:
            hospital = "暂无资料"
        Housing_item['hospital'] = hospital
        # 银行
        try:
            bank = response.xpath(per_temp.format("银行")).extract_first().strip()
        except Exception as e:
            bank = "暂无资料"
        Housing_item['bank'] = bank
        # 其他
        try:
            rest = response.xpath(per_temp.format("其他")).extract_first().strip()
        except Exception as e:
            rest = "暂无资料"
        Housing_item['rest'] = rest
        
        # 小区内部配套
        try:
            facility = response.xpath(per_temp.format("小区内部配套")).extract_first().strip()
        except Exception as e:
            facility = "暂无资料"
        Housing_item['facility'] = facility

        # 小区规划
        # 占地面积
        floor_space = response.xpath(text_template.format('占地面积')+'/text()').extract_first().strip()
        Housing_item['floor_space'] = floor_space
        # 建筑面积
        Housing_item['structure_space']  = response.xpath(text_template.format('建筑面积')+'/text()').extract_first().strip()
        # 容积率
        plot_ratio = response.xpath(text_template.format('率')+'/text()').extract_first().strip()
        Housing_item['plot_ratio'] = plot_ratio
        # 停车位
        parking_spot = response.xpath(text_template.format('车')+'/text()').extract_first().strip()
        Housing_item['parking_spot'] = parking_spot
        # 总户数
        total_population = response.xpath(text_template.format("总")+'/text()').extract()[1].strip()
        Housing_item['total_population'] = total_population
        # 楼栋总数
        total_building = response.xpath(text_template.format("楼栋总数")+'/text()').extract_first().strip()
        Housing_item['total_building'] = total_building
        # 物业费
        Housing_item['tenement_fee'] = response.xpath(text_template.format("费")+'/text()').extract_first().strip()
        
        # 物业费描述
        Housing_item['tenement_fee_describe'] = response.xpath(text_template.format("物业费描述")+'/text()').extract_first().strip()

        # 楼层状况
        try:
            condition_status = response.xpath(text_template.format("楼层状况")+'/text()').extract_first().strip()
        except Exception as e:
            condition_status = '暂无资料'
        Housing_item['condition_status'] = condition_status
        # 物业公司
        try:
            tenement_company = response.xpath(text_template.format("物业公司")+'/a/text()').extract_first().strip()
        except Exception as e:
            tenement_company = '暂无资料'
        Housing_item['tenement_company'] = tenement_company
        print(Housing_item.get('architecture_name'))
        yield Housing_item

    def parse_housing_type(self, response):
        '''
            住房户型
        '''
        HousingType = HousingTypeItem()
        # 楼盘名称
        HousingType['architecture_name'] = response.css('a.ts_linear::text').extract_first().strip()

        HousingType['housing_type_url'] = response.url
        # 户型
        HousingType['house_class'] = response.css('ul#ListModel>li>p.tiaojian span.fl::text').extract()
        # 面积
        HousingType['house_area'] = response.css('ul#ListModel>li>p.tiaojian span.fr::text').extract()
        # 户型链接
        HousingType['house_link'] = list(map(
            lambda item:response.urljoin(item), response.css('ul#ListModel>li>a ::attr("href")'
        ).extract()))

        # 户型图片
        HousingType['house_type_photos'] = list(
            map(
                lambda item: response.urljoin(
                    item.replace('220x150','748x600')
                ),response.css('ul#ListModel>li>a img::attr("src")').extract()
                )
            )
        # 户型介绍
        HousingType['house_describe'] = response.css('ul#ListModel>li>a img::attr("alt")').extract()
        yield HousingType
        print(HousingType.get('architecture_name'))

    def parse_housing_photo(self, response):
        '''
            楼盘相册
        '''
        photoitem = HousingPhotoItem()
        # 楼盘名称
        photoitem['architecture_name'] = response.css('a.ts_linear::text').extract_first().strip()
        photoitem['housing_photo_url'] = response.url

        photoitem['photos'] = list(
            zip(
                response.css('ul#gaoqinglist>li a p::text').extract(), map(
                    lambda item: response.urljoin(item.replace('124x82','748x600')
                ),response.css('ul#gaoqinglist>li a img::attr("src")').extract())
            )
        )
        print(photoitem.get('architecture_name'))
        yield photoitem

    def parse_housing_comment(self, response):
        '''
            楼盘点评
        '''
        commentitem = HousingCommentItem()
        # 楼盘名称
        commentitem['architecture_name'] = response.css('a.ts_linear::text').extract_first().strip()
        commentitem['housing_comment_url'] = response.url
        data = list(map(lambda item: item.strip(), response.css(".Comprehensive_score span::text").extract()))
        commentitem['grade'] = ''.join(list(filter(None, data)))
        print(commentitem.get('architecture_name'))
        yield commentitem
 