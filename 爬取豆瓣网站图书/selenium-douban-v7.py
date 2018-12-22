# -*- coding: utf-8 -*-
import os
import re
import sys
import json
from pprint import pprint
from collections import OrderedDict

import chardet
from tinydb import TinyDB, Query


# 实例化浏览器驱动
_vars = globals()  # 获取当前环境下的全局变量字典
if '__file__' not in _vars:
    # 如果__file__不存在，就定义一个(目的: 便于直接复制代码都REPL中执行)
    __file__ = 'selenium-douban.py'
# 临时存储书籍数据结果的json文件
task_result_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), r'task-result.json')

# 存储最终结果的json文件
store_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), r'store.json')
db = TinyDB(store_file)
Q = Query()
# 读取临时数据
task_result = None
with open(task_result_file, 'rb') as f:
    bytes_data = f.read()
    encoding = chardet.detect(bytes_data)['encoding']
    if bool(encoding):
        task_result = json.loads(bytes_data.decode(encoding))

if not bool(task_result):
    print('没有数据哟')
    sys.exit(1)

for book_url in task_result:
    book_item = task_result[book_url]
    db.insert(book_item)

pprint(db.search(Q.ISBN.exists()))
pprint(db.search(Q.作者.exists()))
pprint(db.search(Q['作者'].exists()))
