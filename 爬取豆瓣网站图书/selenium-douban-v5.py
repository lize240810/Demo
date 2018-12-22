# -*- coding: utf-8 -*-
import os
import sys
import json
import re
from pprint import pprint
from collections import OrderedDict

from pyquery import PyQuery as pq
from selenium import webdriver
from furl import furl
import chardet


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

# 读取任务列表
task_list = None
with open(detail_list_file, 'rb') as f:
    bytes_data = f.read()
    encoding = chardet.detect(bytes_data)['encoding']
    if bool(encoding):
        task_list = json.loads(bytes_data.decode(encoding))

if not bool(task_list):
    print('没有数据哟')
    sys.exit(1)

for task in task_list:
    # 爬取具体页面数据
    browser.get(task)
    doc = pq(browser.page_source)
    # TODO: 解析详细信息
    data_str = doc('.subject').text()
    print(repr(data_str))
    print()

    # 分割行
    # (?<!\:) 匹配捕捉\n前面的`:` 
    # (?!\:) 匹配捕捉\n后面的`:`
    split_result = re.split(r'(?<!\:)\n(?!\:)', data_str)
    pprint(split_result)

    # 处理特殊行，一致化
    split_result = list(map(
        # \n(?=\:)匹配\n前面的位置
        lambda item: re.sub(r'\n(?=\:)', '', item),
        split_result
    ))
    pprint(split_result)

    # 分割每一行的名称值数据
    split_result = dict(map(
        lambda item: re.split(r'\:\n', item),
        split_result
    ))
    pprint(split_result)
    break
