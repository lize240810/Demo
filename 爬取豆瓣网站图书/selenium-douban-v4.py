# -*- coding: utf-8 -*-
import os
import json
from pprint import pprint
from collections import OrderedDict

from pyquery import PyQuery as pq
from selenium import webdriver
from furl import furl


def process_page(doc):
    '''处理页数据(含有书籍列表)'''
    # 查找所有书籍
    books = doc.find('.sc-dnqmqq').children('.sc-bxivhb')
    # 用于存放解析的书籍列表
    book_list = OrderedDict()
    # 遍历书籍
    for book in books.items():
        # 左边的图片部分
        cover = book.find('.cover-link')
        # 封面图片
        book_cover = cover.find('.cover').attr('src')
        # 右边的的详细介绍
        detail = book.find('.detail')
        # 标题下的a标签
        title_tag = detail.find('.title').find('.title-text')
        # 书籍名称
        book_name = title_tag.text().strip()
        # 书籍详细介绍地址
        book_detail = title_tag.attr('href')
        # 解析后的书籍数据
        book_item = {
            'name': book_name,
            'cover': book_cover,
            'detail': book_detail
        }
        # 将解析的单个书籍添加到书籍列表
        book_list[book_detail] = book_item
    # 显示书籍列表
    # pprint(book_list)
    return book_list

# 实例化浏览器驱动
_vars = globals()  # 获取当前环境下的全局变量字典
if '__file__' not in _vars:
    # 如果__file__不存在，就定义一个(目的: 便于直接复制代码都REPL中执行)
    __file__ = 'selenium-douban.py'
# 拼接出完整的chromedriver路径
driver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), r'chromedriver.exe')
# 打开浏览器
browser = webdriver.Chrome(executable_path=driver_path)

# 存储书籍详细信息列表的json文件
detail_list_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), r'detail-list.json')
# 初始URL
init_url = 'https://book.douban.com/subject_search?search_text=python&cat=1001'
# 打开指定URL
browser.get(init_url)

# 获取当前页面源码，基于此构造PyQuery对象
doc = pq(browser.page_source)

# 查找书籍分页信息
paginator = doc.find('.sc-dnqmqq').children('.paginator')
# 所有的分页数字链接
max_num = paginator.children('.num').eq(-1).text()
# 处理最大页码(判断有效)
if max_num.isdigit():
    # 将获取到的字符串页码转为数字
    max_num = int(max_num)
    # 判断是否有数据
    if max_num > 0:
        # 可能的页码
        page_nums = range(0, max_num)
        # 每页书籍条数
        page_size = 15
        # 存储书籍详细信息
        detail_list = OrderedDict()
        # 按页爬取
        for page_num in page_nums:
            # 页面分页参数（需要跳过的书籍条数）
            start = page_size * page_num
            # 构造需要爬取的页面URL
            page_url = furl(init_url).add({'start': start}).url
            if page_num > 0:
                # 爬书籍列表页
                # 打开书籍列表URL
                browser.get(page_url)
                # 获取当前页面源码，基于此构造PyQuery对象
                doc = pq(browser.page_source)
            # 处理当前页数据
            book_list = process_page(doc)
            # 将当前页里面的书籍放到总列表中
            detail_list.update(book_list)
            print('爬 [{0}/{1}] 页： [{2}]'.format(page_num + 1, max_num, page_url))
            if page_num > 1:
                break
        # 存储书籍详细信息列表到文件
        with open(detail_list_file, 'wt', encoding='utf-8') as f:
            json.dump(detail_list, f, ensure_ascii=False)
