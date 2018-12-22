import os
import re
import io

from pyquery import PyQuery as pq
from selenium import webdriver
from bs4 import BeautifulSoup
from PIL import Image
from furl import furl
import requests



# 设置驱动软件位置
driver_path = os.path.join(os.getcwd(), r'chromedriver.exe')
# 浏览器设置
chrome_options = webdriver.ChromeOptions()
# 设置不加载图片
# prefs = {"profile.managed_default_content_settings.images": 2}
# chrome_options.add_experimental_option("prefs", prefs)
# 初始化
browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_options)
init_url = r'http://jandan.net/ooxx/page-55#comments'
browser.get(init_url)
# 获得网页源码
# soup = BeautifulSoup(browser.page_source, 'lxml')
doc = pq(browser.page_source)
doc.remove_namespaces()

file_path = os.path.join(os.getcwd(), '煎蛋妹子')
# 文件夹不存在就创建
if not os.path.isdir(file_path):
    os.mkdir(file_path)

# 获得最大网页
docs = doc.find('.current-comment-page').eq(1).text()
max_page = int(re.search(r'\d{2,}', docs).group())

for page_num in range(max_page, 0, -1):
    f = furl(init_url)
    f.path.segments[-1] = 'page-{0}'.format(page_num)
    paths = os.path.join(file_path, str(page_num))
    if not os.path.isdir(paths):
        os.mkdir(paths)

    if page_num < max_page:
        browser.get(f.url)
        doc = pq(browser.page_source)
        doc.remove_namespaces()

    # 定位获取标签
    doc_text = doc.find('.commentlist').find('.text')
    # 迭代获取图片路径
    for item in doc_text.items():
        f1 = furl(item('.view_img_link').attr('href'))
        f1.scheme = f.scheme
        resp = requests.get(f1.url)
        #构建io对象
        img = Image.open(io.BytesIO(resp.content))
        path_name = '煎蛋妹子/{0}/{1}'.format(page_num, f1.path.segments[-1])
        # 保存
        img.save('{0}'.format(path_name))
        print('成功.......')
    print('第{0}/{1}页完成'.format(page_num, max_page))
    if page_num == 50:
        break
        
