# -*- coding:utf-8 -*- 
import json
import os
import random
import re
import numpy as np
import pandas as pd
from os import path

from PIL import Image
# 用于显示图像的库
import matplotlib.pyplot as plt
# 用于中文显示处理
import matplotlib
# 配置为中文显示
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['font.fantasy']= 'sans-serif'

# 词云所需要的库
try:
    from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
except Exception as e:
    os.system("pip install wordcloud")
    from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
# 微信相关的库
try:
    import itchat
except:
    os.system('pip install itchat')
    import itchat

# 登录微信
itchat.login()
# 返回所有微信好友
friends = itchat.get_friends(update=True)[0:]
# 写成json文件
with open('test.json','w+', encoding='utf-8') as fw:
    for item in friends:
        fw.write(json.dumps(item['Signature'],ensure_ascii=False)+'\n')
    print("写入完成")

dicts ={
    'male':0,
    'female':0,
    'other':0
}

def wx_sex_Bar():
    '''
        微信好友信息提取
    '''
    global dicts
    for i  in friends[1:]:
        sex = i['Sex']
        if sex == 1:
            dicts['male'] = dicts.get('male', 0)+1
        elif sex == 2:
            dicts['female'] = dicts.get('female', 0)+1
        else:
            dicts['other'] = dicts.get('other', 0)+1
    df2 = pd.DataFrame(list(dicts.items()),columns=['A','B'])
    labels = ['男','女','其他']
    explode=[0.1,0.1,0]    
    plt.pie(x=df2.B, labels=labels, autopct='%.2f%%', explode=explode, shadow=True, counterclock=False)
    plt.title('微信好友的男女比例')
    plt.show()


# 文件位置
paths = path.dirname(os.path.abspath(__file__)) if "__file__" else os.getcwd()
# 字体位置
font = path.join(paths, 'FZSTK.TTF')
# 读取的文本
text = open(path.join(paths, 'test.json'),encoding='utf-8').read()
# 词云的背景图片
# backgroud_Image = plt.imread(path.join(paths, 'timg.jpg'))
backgroud_Image = np.array(Image.open(path.join(paths, 'timg.jpg')))

def parse_signature(text):
    # 匹配文本
    res = re.compile(r'""|<span.*?>.*?</span>|(\\n)|(\n)',re.S)
    # 清洗数据
    text = res.sub('', text)
    # 配置词云
    my_word = WordCloud(
        background_color='white', # 设置背景颜色
        mask=backgroud_Image,# 设置背景图片
        font_path=font,# 若是有中文的话，这句代码必须添加，不然会出现方框，不出现汉字
        max_words=2000, # 设置最大现实的字数
        stopwords=STOPWORDS, # 设置停用词
        max_font_size=200, # 设置字体最大值
        min_font_size=1,
        contour_color = 'steelblue',
        # 边框线
        # contour_width = 0.3,
        # color_func = lambda *args, **kwargs: "black"
        # color_func= lambda *args, **kwargs: (255,60,0)
        random_state=1, # 设置有多少种随机生成状态，即有多少种配色方案

    ).generate(text)

    # #改变字体颜色
    # img_colors = ImageColorGenerator(backgroud_Image)
    # #字体颜色为背景图片的颜色
    # my_word.recolor(color_func=img_colors)
    plt.imshow(my_word, interpolation="bilinear")
    # 图片存储
    my_word.to_file(path.join(paths, 'python.jpg'))
    plt.title("朋友个性签名词云")
    
    # 是否显示x轴、y轴下标
    plt.axis("off")
    plt.show()
    print('生成词云成功!')

if __name__ == '__main__':
    wx_sex_Bar()
    parse_signature(text)