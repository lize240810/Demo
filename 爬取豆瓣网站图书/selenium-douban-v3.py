# -*- coding: utf-8 -*-
import os
from pprint import pprint

from pyquery import PyQuery as pq
from selenium import webdriver
from furl import furl


# 实例化浏览器驱动
_vars = globals()  # 获取当前环境下的全局变量字典
if '__file__' not in _vars:
    # 如果__file__不存在，就定义一个(目的: 便于直接复制代码都REPL中执行)
    __file__ = 'selenium-douban.py'
# 拼接出完整的chromedriver路径
driver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), r'chromedriver.exe')
# 打开浏览器
browser = webdriver.Chrome(executable_path=driver_path)

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
        # 按页爬取
        for page_num in page_nums:
            # 页面分页参数（需要跳过的书籍条数）
            start = page_size * page_num
            # 构造需要爬取的页面URL
            page_url = furl(init_url).add({'start': start})
            # TODO: 去爬
            print('爬第 {0} 页： [{1}]'.format(page_num + 1, page_url))
