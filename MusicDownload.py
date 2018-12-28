import re
import os

import requests
from bs4 import BeautifulSoup
from furl import furl

url = None
def gethtml(url):
    '''提取页面html代码'''
    # 加入浏览器头信息
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }
    # 实用代理ip , 在 www.xicidaili.com
    proxy_addr ={'http':'125.70.13.77'}
    # headers 头部信息  proxies 代理
    html = requests.get(url, headers=headers, proxies=proxy_addr) # 请求

    return html

def getid():
    '''获取通过关键字搜索音频专辑ID列表'''
    keyword = input('请输入你要查找的音频的关键字:\n') # 输入需要下载的关键字
    albumId = 'https://www.ximalaya.com/search/{}'.format(keyword) # 输入关键字,凭借链接
    global url
    url = furl(albumId)
    html = gethtml(albumId) # 获取关键字查找到的页面
    # 创建soup对象
    soup = BeautifulSoup(html.text, 'lxml')
    # 获取存储歌曲id的a标签
    info = soup.select("div.xm-album-cover__wrapper > a")
    # 先获取到href属性在根据正则提起专辑中的id
    hrefs = [re.search(r'\d+', infoid['href']).group() for infoid in info]
    # 获取到标题内容
    titleinfo = soup.select("div.xm-album > p")
    # 获取专辑中标题信息
    titles = [title['title'] for title in titleinfo]

    # print(titles, hrefs)
    dicts = {
        'titles': titles,
        'hrefs': hrefs
    }
    return dicts


def mkdir(title, url):
    '''把下载的音频文件保存到相应的文件夹中'''
    # 获取音乐的二进制文件
    title = title.replace('/', '-')
    print(title, '开始下载........')
    music = requests.get(url)
    # 获取音乐的存储路径
    if not os.path.isdir('music'):
        os.mkdir('music')
    file_path = os.path.abspath('music')
    # 音乐存储的绝对路径
    music_path = os.path.join(file_path, '{}.mp3'.format(title))
    # 保存音乐
    with open(music_path, 'wb') as f:
        f.write(music.content)
    print(title, '存储完成......')
    

def main():
    '''下载对应的转件ID下的音频文件'''
    # 获取到对应的href链接
    dictsmp3_url = r'https://www.ximalaya.com/revision/play/album?albumId={0}&pageNum=1&pageSize=30'
    dicts =  getid()
    music = {}
    for href in dicts['hrefs']:
        html = gethtml(dictsmp3_url.format(href)).json()
        music_name = html['data']['tracksAudioPlay'][0]['trackName']
        music_href = html['data']['tracksAudioPlay'][0]['src']
        mkdir(music_name, music_href)

if __name__ == '__main__':
    main()