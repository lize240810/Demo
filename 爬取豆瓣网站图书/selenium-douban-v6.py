# -*- coding: utf-8 -*-
import os
import re
import sys
import json
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

for idx, task in enumerate(task_list):
    # 爬取具体页面数据
    browser.get(task)
    doc = pq(browser.page_source)
    # 选出书籍信息块元素
    info = doc.find('#info')
    data_str = info.text()
    # 分割行
    split_result = re.split(r'(?<![\:\/])\n(?![\:\/])', data_str)
    # 处理特殊行，一致化
    split_result = list(map(
        lambda item: re.sub(r'\n(?=\:)', '', item),
        split_result
    ))
    # 分割每一行的名称值数据
    split_result = dict(map(
        lambda item: re.split(r'\:\n', item),
        split_result
    ))
    # 将每一项值中的\n去掉
    for key in split_result:
        split_result[key] = split_result[key].replace('\n', '')
    # 合并信息(偷懒方式)
    task_list[task].update(split_result)
    # 将所有字段改为英文模式（便于最终存储）
    # task_list[task]['author'] = split_result['作者']
    # task_list[task]['isbn'] = split_result['ISBN']
    # TODO： 更多的split_result项存到task_list[task]
    # 调试过程中，收敛(低调)一点儿，防止被封IP
    if idx > 2:
        break
# 显示最终结果
pprint(task_list)
# 临时存储书籍数据结果的json文件
task_result_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), r'task-result.json')
with open(task_result_file, 'wt', encoding='utf-8') as f:
    json.dump(task_list, f, ensure_ascii=False)
