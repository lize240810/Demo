# -*- coding: utf-8 -*-
import os
from pprint import pprint

from pyquery import PyQuery as pq
from selenium import webdriver


# 实例化浏览器驱动
_vars = globals()  # 获取当前环境下的全局变量字典
if '__file__' not in _vars:
    # 如果__file__不存在，就定义一个(目的: 便于直接复制代码都REPL中执行)
    __file__ = 'selenium-douban.py'
# 拼接出完整的chromedriver路径
driver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), r'chromedriver.exe')
# 打开浏览器
browser = webdriver.Chrome(executable_path=driver_path)
# 打开指定URL
browser.get('https://book.douban.com/subject_search?search_text=python&cat=1001&start=15')

# 获取当前页面源码，基于此构造PyQuery对象
doc = pq(browser.page_source)
# 查找所有书籍
books = doc.find('.sc-dnqmqq').children('.sc-bxivhb')
# 用于存放解析的书籍列表
book_list = []
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
    book_list.append(book_item)
# 显示书籍列表
pprint(book_list)
