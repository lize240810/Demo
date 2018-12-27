# -*- coding: utf-8 -*-
import os
import re
import json
import time
from pprint import pprint

import scrapy
from selenium import webdriver
# 元素查找的模块
from selenium.webdriver.common.by import By
# 驱动
from selenium.webdriver.support.ui import WebDriverWait
# 引发异常
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, # 延时异常
    WebDriverException, # 驱动异常
    NoSuchElementException, # 无法抛出的异常
    StaleElementReferenceException
)
from baidu.items import BaiduItem


def gen_browser(driver_path):
    '''实例化一个driver'''
    options = webdriver.ChromeOptions()
    # 无头浏览器
    # options.add_argument("--headless") 
    # 不在沙箱中操作
    options.add_argument('--no-sandbox')
    # 禁止gpu的渲染
    options.add_argument('--disable-gpu')
    # 忽略证书错误
    options.add_argument('--ignore-certificate-errors')
    # 
    options.add_argument('disable-infobars')
    # 禁止插件
    options.add_argument("--disable-plugins-discovery")
    # 设置浏览器头
    user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36"
    options.add_argument('user-agent="{0}"'.format(user_agent))
    # ############### 专业造假 ***************************
    def send(driver, cmd, params={}):
        '''
        向调试工具发送指令
        from: https://stackoverflow.com/questions/47297877/to-set-mutationobserver-how-to-inject-javascript-before-page-loading-using-sele/47298910#47298910
        '''
        resource = "/session/%s/chromium/send_command_and_get_result" % driver.session_id
        url = driver.command_executor._url + resource
        body = json.dumps({'cmd': cmd, 'params': params})
        response = driver.command_executor._request('POST', url, body)
        if response['status']:
            raise Exception(response.get('value'))
        return response.get('value')
    def add_script(driver, script):
        '''在页面加载前执行js'''
        send(driver, "Page.addScriptToEvaluateOnNewDocument", {"source": script})
    # 给 webdriver.Chrome 添加一个名为 add_script 的方法
    webdriver.Chrome.add_script = add_script # 这里（webdriver.Chrome）可能需要改，当调用不同的驱动时
    # *************** 专业造假 ###################
    browser = webdriver.Chrome(
        executable_path=driver_path,
        chrome_options=options
    )
    # ################## 辅助调试 *********************
    existed = {
        'executor_url': browser.command_executor._url,  # 浏览器可被远程连接调用的地址
        'session_id': browser.session_id  # 浏览器会话ID
    }
    # pprint(existed)
    # ********************* 辅助调试 ##################
    # ############### 专业造假 ***************************
    browser.add_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false,
        });
        window.navigator.chrome = {
            runtime: {},
        };
        Object.defineProperty(navigator, 'languages', {
            get: () => ['zh-CN', 'zh']
        });
        Object.defineProperty(navigator, 'plugins', {
            get: () => [0, 1, 2],
        });
        """)
    # *************** 专业造假 ###################
    # 返回一个浏览器
    return browser

class StarspiderSpider(scrapy.Spider):
    name = 'StarSpider'
    allowed_domains = ['index.baidu.com']
    start_urls = ['http://index.baidu.com/v2/rank/index.html#/industryrank/star']
    title_name = 'None'

    def parse(self, response):
        # 从settings.py文件中获得浏览器驱动
        driver_path = self.settings.get('DRIVER_PATH')
        # 生成一个浏览器对象
        # import ipdb; ipdb.set_trace()
        browser = gen_browser(driver_path)
        # 打开页面
        browser.get(response.url)
        # 等待页面加载到可以找到元素
        try:
            # 查找标签最多等待5秒 超过5秒则抛出异常
            _element = WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".tab-content"))
            )
        except TimeoutException:
            # import traceback; traceback.print_exc()
            import ipdb; ipdb.set_trace()
            # 退出浏览器
            browser.quit()
        # 从主页中点击进入
        # time.sleep(1)
        # 多个排行榜
        ranking = [ran.text for ran in browser.find_elements_by_css_selector('div.desc > div:nth-child(2)')]
        titles = browser.find_elements_by_css_selector('p.more-rank')
        results = []
        for idx, title in enumerate(titles):
            # import ipdb; ipdb.set_trace()
            # 回到所有排行棒页面
            if idx > 0:
                # browser.find_element_by_xpath("//div[@class='nav-horizontal-container']//span[text()[contains(.,'行业排行')]]/..").click()
                browser.execute_script('history.go(-1)')
                titles = browser.find_elements_by_css_selector('p.more-rank')
                title = titles[idx]
            # 点击不同的排行榜进入数据
            self.title_name = ranking[idx]
            # 点击进入详细页面
            title.click()

            # browser.find_element_by_xpath('//p[@class="more-rank"]/span[text()[contains(.,"娱乐人物")]]').click()

            # 根据头部标签选择
            border_none = browser.find_elements_by_css_selector('.border-none .tab-nav .tab-item')

            # 根据头部标签进行循环 
            for border in border_none:
                # 获取每个头部标签来进行分别选择
                border.click()
                results.extend(self.parse_main(browser, border.text))
                
            # 便利返回值
            for result in results:
                yield result
        # 关闭浏览器
        # browser.quit()
        

    def parse_main(self, browser, nav_name):
        '''
            核心内容
        '''
        item_count = 0
        # 选择点击可以下拉的标签的
        icon_up = browser.find_elements_by_css_selector('.date-icon-up')
        # 查询是否存在
        if len(icon_up) > 0:
            # 点击展开下拉列表框（用于获取总的周数）
            icon_up[0].click()
            time.sleep(0.5)
            # 获取到所有的周的总数
            item_count = len(browser.find_elements_by_css_selector('.date-item'))
        
        # 获取下拉列表框中的所有元素（从指定期中获取到数据）
        results = []
        for week in range(0, item_count):
            if week > 0:
                # 循环点击展开下拉列表框（多个周）
                browser.find_element_by_css_selector('.date-icon-up').click()
                time.sleep(0.3)
            # 循环选择周
            css_selector = '.date-item:nth-of-type({0})'.format(week + 1)
            # 选择某一周
            someweek = browser.find_elements_by_css_selector(css_selector)[0]
            someweek_text = someweek.text
            # 点击某一周
            someweek.click()
            # 等一会儿(1.5秒)，等待页面更新
            time.sleep(1)
            # 爬每一个周 调用数据获取的方法
            # 指数
            exponent = browser.find_elements_by_css_selector('.border-bottom .tab-nav .tab-item')
            # 根据同一个页面的指数来进行分类获取页面
            for res in exponent:
                # 点击不同的指数标签
                res.click()
                time.sleep(0.1)
                # 调用指数查询方法
                result = self.parse_week(browser, nav_name, someweek_text, res.text)
                results.extend(result)

        return results
        # import traceback; traceback.print_exc()

    def parse_week(self, browser, nav_name, someweek, exponent):
        '''
            搜素指数
        '''
        # 定义变量，收集结果
        # import ipdb; ipdb.set_trace()
        result = []
        try:
            # 获取每一页的每一行的数据
            items = browser.find_elements_by_css_selector('.tab-content .list > .list-item')
            # 分别便利获取每个娱乐圈人的数据
            for item in items:
                baidu = BaiduItem()
                # 排名
                baidu['rank'] = item.find_element_by_css_selector('.content .rank').text.strip()
                # 姓名
                baidu['name'] = item.find_element_by_css_selector('.content .name').text.strip()
                if nav_name == '周上升榜':
                    # 趋势
                    # import ipdb; ipdb.set_trace()
                    trend = item.find_element_by_xpath('//div[@class="trend"]/span').text
                    baidu['trend'] = trend
                else:
                    # 趋势
                    trend = item.find_element_by_xpath('//span[@class="trend-icon"]/i').get_attribute('class')
                    baidu['trend'] = re.sub('icon trend-', '', trend)
                # 行指数
                line = item.find_element_by_css_selector('.content .line-light')
                # 行指数-真实值
                real_value = float(line.value_of_css_property('width').replace('px', ''))
                # 行指数-最大值元素
                line_max = line.find_element_by_xpath('..')
                # 最大值
                max_value = float(line_max.value_of_css_property('width').replace('px', ''))
                # 指数值
                index = round(100 * real_value / max_value, 2)
                # 指数字符串
                index_str = str(index).rstrip('0').rstrip('.') + '%'
                # 指数比例
                baidu['index_str'] = index_str
                # 棒单名
                baidu['nav_name'] = nav_name
                # 搜索指数 和资讯指数
                baidu['exponent'] = exponent
                # 日期
                baidu['week'] = someweek
                result.append(baidu)
                print(nav_name, '--->', exponent, '--->', someweek, '--->', index_str)
                print('-' * 30)
                # import ipdb; ipdb.set_trace()
        except (NoSuchElementException, StaleElementReferenceException):
            import ipdb; ipdb.set_trace()
        # 返回结果
        return result
