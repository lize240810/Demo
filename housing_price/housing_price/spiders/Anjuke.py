# -*- coding: utf-8 -*-
import scrapy

import redis
from furl import furl
from housing_price.items import HousingPriceItem

class AnjukeSpider(scrapy.Spider):
    name = 'Anjuke'
    allowed_domains = ['https://cq.fang.anjuke.com']
    start_urls = ['https://cq.fang.anjuke.com/']
    HTTPERROR_ALLOWED_CODES = [403, 404]
    pool_county = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
    pool_houses = redis.ConnectionPool(host='127.0.0.1', port=6379, db=1)
    Bridal_Houses_Dict = {}

    def parse(self, response):
        # 总数据
        import ipdb as pdb; pdb.set_trace()
        data_sum = response.css('.total>em::text').extract_first().strip()
        # 总页数
        page_sum = int(int(data_sum) / 60) + 1
        # 初始化url
        url = 'https://cq.fang.anjuke.com/loupan/all/p{0}/'
        # 获得区县拼音
        self.area_save(response)
        # 所有新房的链接
        for page_num in range(1, page_sum + 1):
            print('获取{0}/{1}'.format(page_num, page_sum))
            yield scrapy.Request(url=url.format(page_num), callback=self.parse_dict, dont_filter=True)

    def parse_dict(self, response):
        '''
            数据连接数据
        '''
        print(response.url)
        import ipdb as pdb; pdb.set_trace()
        # 所有区的区名
        infos = response.xpath('//div[@class="infos"]/a')
        Bridal_Houses_Href = infos.xpath('./@href').extract()
        Bridal_Houses_Name = infos.xpath('.//span[@class="items-name"]/text()').extract()
        # 添加到新房链接集合中中
        self.Bridal_Houses_Dict.update(dict(zip(Bridal_Houses_Name, Bridal_Houses_Href)))
        for href in Bridal_Houses_Href:
            scrapy.Request(url=href, )
        # yield dict(zip(Bridal_Houses_Name, Bridal_Houses_Href))
        # print(self.Bridal_Houses_Dict)

    def parse_item(self, response):
        '''
            获得数据
        '''
        # 建筑名
        Name = response.css('.basic-info>h2::text').extract_first().strip()
        # 别名
        Alias = response.css('.basic-info>h2+p::text').extract_first().strip()
        # 标签
        Tags = ','.join(map(lambda item: item.strip(), response.css('.basic-info div.tags>a::text').extract()))
        # 等级
        Rank = response.css('div.basic-info>div.rank-wrap>span::text').extract_first()
        # 开盘日期
        Start_Time = response.xpath('//dt[text()[contains(.,"开盘")]]/following-sibling::dd/span/text()').extract_first()
        # 交房
        Check_Out = response.xpath('//dt[text()[contains(.,"交房")]]/following-sibling::dd/span/text()').extract_first()
        # 户型
        House_Type = ','.join(map(lambda item: item.strip(), response.xpath('//dt[text()[contains(.,"户型")]]/following-sibling::dd/div/a/text()').extract()))
        # 地址
        Location = response.css('dd.g-overflow>a.lpAddr-text::text').extract_first().strip()
        # 售楼部电话
        Phone = response.css('strong.last-strong::text').extract_first().strip()

        Houses_Details_href = response.xpath('//ul/li/a[text()[contains(.,  "楼盘详情")]]/@href').extract_first()

    def houses_details(self, response):
        text_temp = '//ul[@class="list"]/li/div[text()[contains(.,"{0}")]]/following-sibling::div/a'
        # 参考价格 元/㎡起
        Min_price, Max_price = response.css('div.des>span.can-spe::text').extract_first().strip().split('-')
        # 总价
        Sum_Price = response.css('div.des>span.can-spe::text').extract()[1].strip().split('-')
        # 最大总价与最小总价
        Min_Sum_price, Max_Sum_price = list(map(lambda item: int(item)*10**4, Sum_Price))
        # 开发商
        Developers = response.xpath(text_temp.format('开发商') + '/text()').extract_first().strip()
        # 开发商连接
        Developers_Href = response.xpath(text_temp.format('开发商') + '/@href').extract_first()
        # 销售信息模板
        text_temp1 = '//ul[@class="list"]/li/div[text()[contains(.,"{0}")]]/following-sibling::div'
        # 最低首付
        Min_Down_Payment = response.xpath(text_temp1.format('最低首付') + '/text()').extract_first().strip()
        # 月供
        Monthly_Price = response.xpath(text_temp1.format('月供') + '/text()').extract_first().strip()
        # 小区情况
        Community_status = response.xpath(text_temp1.format('建筑类型') + '/text()').extract_first().strip()
        # 产权 年限
        Houses_Period = response.xpath(text_temp1.format('产权年限') + '/text()').extract_first().strip().replace('\u3000',',')
        # 容积率
        Plot_Ratio = response.xpath(text_temp1.format('容积率') + '/text()').extract_first().strip()
        # 绿化绿
        Green_Ratio = response.xpath(text_temp1.format('绿化绿') + '/text()').extract_first().strip()
        # 规划户数
        Population = response.xpath(text_temp1.format('规划户数') + '/text()').extract_first().strip()
        # 楼层状况
        Floor_Condition = response.xpath(text_temp1.format('楼层状况') + '/text()').extract_first().strip()
        # 工程进度
        Project_Progress = response.xpath(text_temp1.format('工程进度') + '/text()').extract_first().strip()
        # 物业管理费
        property_Fee = response.xpath(text_temp1.format('物业管理费') + '/text()').extract_first().strip()
        # 物业公司
        property_Company = response.xpath(text_temp1.format('物业公司') + '/text()').extract_first().strip()
        # 车位数 
        Parking_Num = response.xpath(text_temp1.format('车位数') + '/text()').extract_first().strip()
        


    def area_save(self, response):
        '''
            区域数据持久化
        '''
        # 数据库链接
        client_county = redis.Redis(connection_pool=self.pool_county)
        client_houses = redis.Redis(connection_pool=self.pool_houses)
        # 区分类
        county_name = response.xpath('//span[@class="curr-area"]/following-sibling::a/text()').extract()
        county_pinyin = response.xpath('//span[@class="curr-area"]/following-sibling::a/@data-pinyin').extract()
        # 区县的字典
        county_dict = dict(zip(county_pinyin,county_name))
        # 添加到数据库中
        for cou in county_dict:
            client_county.set(cou, county_dict[cou])
        houses_dict = {}

        # 根据区县分楼盘
        for key_pinyin in county_dict.keys():
            # 所有的楼盘
            houses = response.xpath('//div[@class="filter-sub"]/a[@data-pinyin="{0}"]'.format(key_pinyin))
            # 楼盘名称
            houses_name = houses.xpath('./@alt').extract()
            # 楼盘链接
            houses_link = houses.xpath('./@href').extract()
            # import ipdb as pdb; pdb.set_trace()  
            # 根据拼音存储
            houses_ = dict(zip(houses_name, houses_link))
            # 持久化到字典用于操作
            houses_dict[key_pinyin] = houses_
            # 持久化到数据库
            client_houses.set(key_pinyin, str(houses_))

        return county_dict
