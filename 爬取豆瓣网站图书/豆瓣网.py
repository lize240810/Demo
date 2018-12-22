import os
from pprint import pprint
from collections import OrderedDict
import json
import sys
import re

from furl import furl
from pyquery import PyQuery as pq
from selenium import webdriver
import chardet
from tinydb import TinyDB, Query


# 获取自动化软件的位置
driver_path = os.path.join(os.getcwd(), r'chromedriver.exe')
# 存储json文件的位置
detail_list_file = os.path.join(os.getcwd(), r'detail-list.json')
# 设置浏览器
browser = webdriver.Chrome(executable_path=driver_path)
# 打开指定网页
init_url = r'https://book.douban.com/subject_search?search_text=python&cat=1001&start=0'
browser.get(init_url)
# 获取网页源码
doc = pq(browser.page_source)
# 临时存储书籍数据结果的json文件
task_result_file = os.path.join(os.getcwd(), r'task-result.json')
# 存储最终结果的json文件
store_file = os.path.join(os.getcwd(), r'store.json')
# 创建Tiny数据库
db = TinyDB(store_file)
# 查询
Q = Query()


def process_page(doc):
    '''
        解析网页 获取图书的概括内容
    '''
    # 获取图书
    books = doc('.sc-dnqmqq').children('.sc-bxivhb')
    # 图书列表
    book_list = OrderedDict()
    # 便利当前页中的所有图书
    for book in books.items():
        # 图书的详细信息
        book_detail = book.find('.cover-link').attr('href')
        # 图书图片链接
        book_cover = book.find('.cover').attr('src')
        # 图书书名
        book_name = book.find('.detail').find('.title-text').text()
        book_item = {
            'name': book_name,
            'cover': book_cover,
            'detail': book_detail,
        }
        book_list[book_detail] = book_item
    return book_list


def page_write(doc):
    '''
         图书存储
    '''
    max_page = doc.find('.paginator').find('.num').eq(-1).text()
    # 判断页码是否是数字
    if max_page.isdigit():
        max_page = int(max_page)
        # 判断是否有爬取的必要
        if max_page > 0:
            page_nums = range(0, max_page)
            # 设置每页的条数
            page_size = 15
            # 详细图书列表
            detail_list = OrderedDict()
            # 循环所有页数
            for page_num in page_nums:
                # 页面分页参数
                start = page_size * page_num
                # 构造网页的URL
                page_url = furl(init_url)
                page_url.args['start'] = start
                if page_num > 0:
                    # 打开书籍列表URL
                    browser.get(page_url.url)
                    # 获取当前页面源码，基于此构造PyQuery对象
                    doc = pq(browser.page_source)
                # 处理当前页数据
                book_list = process_page(doc)
                # 存储图书详细内容的列表
                detail_list.update(book_list)
                print('爬取【{0}/{1}】页: ===> {2}'.format(
                    page_num + 1, max_page, page_url
                ))
                if page_num > 1:
                    break
                # 存储书籍详细信息列表到文件
            with open(detail_list_file, 'wt', encoding='utf-8') as f:
                json.dump(detail_list, f, ensure_ascii=False)


def book_detail():
    '''
        获取书籍详细信息
    '''
    task_list = None
    # 读取书籍信息
    with open(detail_list_file, 'rb') as f:
        bytes_data = f.read()
        encoding = chardet.detect(bytes_data)['encoding']
        if bool(encoding):
            # 添加任务列表
            task_list = json.loads(bytes_data.decode(encoding))

    # 判断任务是否存在
    if not bool(task_list):
        # 引发异常 跳出任务
        pprint('任务不存在....')
        sys.exit(1)

    for idx, task in enumerate(task_list):
        # 爬取具体页面数据
        browser.get(task)
        # 获取详细书籍
        doc = pq(browser.page_source)
        # TODO: 解析详细信息
        data_str = doc('.subject').text()
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
        print('第{0}条数据存储完成'.format(idx+1))
    # 显示最终结果
    with open(task_result_file, 'wt', encoding='utf-8') as f:
        json.dump(task_list, f, ensure_ascii=False)


def tinydb_write():
    '''
        存储写入数据库
    '''
    # 读取临时数据
    task_result = None
    with open(task_result_file, 'rb') as f:
        bytes_data = f.read()
        encoding = chardet.detect(bytes_data)['encoding']
        if bool(encoding):
            task_result = json.loads(bytes_data.decode(encoding))

    for book_url in task_result:
        book_item = task_result[book_url]
        db.insert(book_item)


if __name__ == '__main__':
    page_write(doc)
    print('爬取图书列表完成。。。。\n\n开始爬取详细信息。。。。')
    book_detail()
    print('爬取完成..........\n\n开始存储数据库中。。。。')
    tinydb_write()
    print('存储完成..........')
    pprint(db.search(Q.ISBN.exists()))
    pprint(db.search(Q.作者.exists()))
    pprint(db.search(Q['作者'].exists()))
