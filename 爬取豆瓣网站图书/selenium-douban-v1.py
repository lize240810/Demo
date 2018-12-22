# -*- coding: utf-8 -*-
import os

from pyquery import PyQuery as pq
from selenium import webdriver

# 实例化浏览器驱动
_vars = globals()
if '__file__' not in _vars:
    __file__ = 'selenium-douban.py'
driver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), r'chromedriver.exe')
browser = webdriver.Chrome(executable_path=driver_path)
# 打开指定URL
browser.get('https://book.douban.com/subject_search?search_text=python&cat=1001&start=15')

doc = pq(browser.page_source)
books = doc.find('.sc-dnqmqq').children('.sc-bxivhb')
'''
for book in books.items():                                        
    print(book)                                        
    break
'''
# 书籍
book = books.eq(2).find('.item-root')
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
