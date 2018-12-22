# -*- coding: utf-8 -*-
from pyquery import PyQuery as pq
import requests as rq
import chardet


# 请求数据
resp = rq.get('https://blog.gsw945.com/python/pandas/index.html')

# 检测编码
encoding = chardet.detect(resp.content)['encoding']
# 设置编码
resp.encoding = encoding

# 取得页面源码
doc = pq(resp.text)
# 用于存放(收集)每一段代码块
htmls = []
# 筛选出Python代码元素
# pre_codes = doc.find('pre').find('code')  # 方式一: 1.先找出代码块
# py_codes = pre_codes.filter('.language-python')  # 方式一: 2. 筛选出代码
py_codes = doc.find('code').filter('.language-python')  # 方式二: 直接筛选出Python代码
# 遍历每一块页面代码元素
for item in py_codes.items():
    # 获取文本（去掉了HTML标签，是可以直接粘贴执行的Python代码）
    # text()方法默认的 squash_space 参数为 True, 会去掉换行
    # squash_space 参考: https://github.com/gawel/pyquery/issues/99#issuecomment-194122347
    htmls.append(item.text(squash_space=False))

# 拼接每一段代码
print('\n'.join(htmls))
