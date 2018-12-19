import requests
import os
import io

from multiprocessing.pool import Pool
# 路径分析
from furl import furl
from PIL import Image

import hashlib


GROUP_START = 1
GROUP_END = 5

# 1.请求这个url可以看到他是以xhr（ajax）的方法请求的
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
}

f = furl('https://www.toutiao.com/search_content/?offset=90&format=json&keyword=%E8%A1%97%E6%8B%8D&autoload=true&count=20')


def get_page(offset, keyword):
    '''
        获取页面
    '''
    # 构建新的url
    f.args['offset'] = offset
    f.args['keyword'] = keyword

    try:
        respone = requests.get(f.url, headers)
        # 判断返回状态
        if respone.status_code == requests.codes.ok:
            return respone.json()
    except requests.ConnectionError:
        return respone.json()


def get_images(json):
    '''
        数据处理
    '''
    data = json.get('data')
    # 数据关键字
    if data:
        for item in data:
            # 数据
            describe = item.get('abstract')
            source = item.get('source')
            title = item.get('title')
            keyword = item.get('keyword')
            img_list = item.get('image_list')
            try:
                # 获得图片路径
                for image in img_list:
                    # 返回一个迭代器
                    yield{
                        'image': image.get('url'),
                        'title': title,
                        'keyword': keyword,
                        'describe': describe,
                        'source': source
                    }
            except Exception as e:
                pass


def save_image(item):
    '''
        图片保存
    '''
    files = '{0}/{1}'.format(item.get('keyword'), item.get('title'))
    if not os.path.exists(item.get('keyword')):
        os.mkdir(item.get('keyword'))
    # 判断文件夹是否存在
    if not os.path.exists(files):
        # import ipdb as pdb; pdb.set_trace()
        # 创建文件夹
        os.mkdir(files)
    try:
        # 获取当前的图片路径
        f_img = furl(item.get('image'))
        # 添加协议
        f_img.scheme = f.scheme
        # 新图片的路径
        # list 为缩略图  large 为原始大图 我们获取大图
        # new_image_url = local_image_url.replace('list', 'large')
        f_img.asdict()['path']['segments'][0] = 'large'
        # 请求图片路径
        # respone = requests.get('http:' + f.url)
        resp = requests.get(f_img.url, headers=headers)

        # 请求成功
        if resp.status_code == 200:
            # 例如 :{image}/{title}/{a1}.{jpg}
            file_path = '{0}/{1}/{2}.{3}'.format(
                item.get('keyword'),
                item.get('title'),
                # md5可以保证图片唯一
                hashlib.md5(resp.content).hexdigest(),
                # 使用时间的无法保存图片唯一但是可以保证文件名唯一
                # datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f'),  # 文件名
                'jpg'
            )
            # 保存文件
            if not os.path.exists(file_path):
                # with open(file_path, 'wb') as f:
                #     f.write(respone.content)
                # print('{0}.png'.format(file_base))
                # 构建io对象
                img = Image.open(io.BytesIO(resp.content))
                # 保存
                img.save('{0}.png'.format(file_path), 'PNG')
                print('下载成功', file_path)
            else:
                print('已经下载过了', file_path)
    except requests.ConnectionError:
        print('保存图片失败')


def main(offset):
    for item in get_images(get_page(offset, '街拍')):
        save_image(item)


if __name__ == '__main__':
    pool = Pool()
    groups = ([x * 20 for x in range(GROUP_START, GROUP_END + 1)])
    pool.map(main, groups)
    pool.close()
    pool.join()
