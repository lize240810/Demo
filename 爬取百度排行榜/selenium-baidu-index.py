import os
import json
import time
from pprint import pprint

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException


if os.path.exists('existed.json'):
    existed = None
    # 从文件 existed.json 中加载已经存在了的浏览器信息
    with open('existed.json', 'rt', encoding='utf-8') as f:
        existed = json.load(f)
    # 从字典取得数据，注入到全局变量
    globals().update(existed)
    # 连接远程的已经存在
    browser = webdriver.Remote(
        command_executor=executor_url,  #_url为上面的_url
        desired_capabilities={}
    )
    browser.close()  # 这时会打开一个全新的浏览器对象, 先把新的关掉
    browser.session_id = session_id  #session_id为上面的session_id
else:
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('disable-infobars')
    options.add_argument("--disable-plugins-discovery")
    user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36"
    options.add_argument('user-agent="{0}"'.format(user_agent))

    driver_path = os.path.join(os.getcwd(), r'chromedriver.exe')

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
    pprint(existed)
    with open('existed.json', 'wt', encoding='utf-8') as f:
        json.dump(existed, f, ensure_ascii=False, indent=4)
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

# browser.get('http://192.168.6.254/')
browser.get('http://index.baidu.com/v2/rank/index.html#/industryrank/star')

# 等待页面加载到可以找到元素
try:
    # 最多等待5秒
    element = WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".tab-content"))
    )
except TimeoutException:
    # import traceback; traceback.print_exc()
    browser.quit()

'''
len(browser.find_elements_by_css_selector('.date-item'))
len(browser.find_elements_by_css_selector('.date-icon-up'))
browser.find_element_by_css_selector('.date-icon-up').click()
browser.find_element_by_css_selector('.date-item')
browser.find_element_by_css_selector('.date-item:nth-of-type(3)')
browser.find_elements_by_css_selector('.date-item:nth-of-type(3)')[0].text
browser.find_elements_by_css_selector('.date-item:nth-of-type(2)')[0].click()
'''
# browser.refresh()

items = browser.find_elements_by_css_selector('.tab-content .list > .list-item')
for item in items:
    # 排名
    rank = item.find_element_by_css_selector('.content .rank').text.strip()
    # 姓名
    name = item.find_element_by_css_selector('.content .name').text.strip()
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
    print(index_str)
    print('-' * 30)

'''
find_elements_by_css_selector()      document.querySelectorAll()
find_element_by_css_selector()       document.querySelector()
'''