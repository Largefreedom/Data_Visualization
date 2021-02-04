import requests
from bs4 import BeautifulSoup
import jieba
import cv2
import os
import numpy as np
import base64
from aip import AipBodyAnalysis
from wordcloud import WordCloud,ImageColorGenerator,STOPWORDS
import collections
from PIL import Image
import re
import random

'''
该脚本包含功能，
0,you-get 下载指定链接视频
1，B站弹幕采集,
2, 视频切帧，
3，人像分割；
4，多序列图片合成视频；
'''

def download(video_url,save_path,video_name):
    '''
    youget 下载视频
    :param video_url:视频链接
    :param save_path: 保存路径
    :param video_name: 视频命名
    :return:
    '''

    cmd = 'you-get -o {} -O {} {}'.format(save_path,video_name,video_url)
    res = os.popen(cmd,)
    res.encoding = 'utf-8'
    print(res.read())# 打印输出


# 读取图片，转化为二进制格式
def get_file_content(filePath):
    with open(filePath,'rb') as fp:
        return fp.read()

def Seg_img(jpg_path,crop_path,save_path):
    '''
    调用API 分割人像图片
    :param jpg_path: 原图像
    :param crop_path: 裁剪之后图像
    :param save_path: 生成 mask 存放路径
    :return:
    '''

    # 通过百度控制台申请得到的 AK 和 SK；
    APP_ID = "23633750"
    API_KEY = 'uqnHjMZfChbDHvPqWgjeZHCR'
    SECRET_KEY = 'KIKTgD5Dh0EGyqn74Zqq8wHWB39uKaS3'

    client = AipBodyAnalysis(APP_ID, API_KEY, SECRET_KEY)
    # 文件夹
    jpg_file = os.listdir(jpg_path)
    # 要保存的文件夹
    for i in jpg_file:
        open_file = os.path.join(jpg_path,i)
        save_file = os.path.join(save_path,i)
        if not os.path.exists(save_file):#文件不存在时，进行下步操作
            img = cv2.imread(open_file)  # 获取图像尺寸
            height, width, _ = img.shape
            if crop_path:# 若Crop_path 不为 None,则不进行裁剪
                crop_file = os.path.join(crop_path,i)
                img = img[100:-1,300:-400] #图片太大，对图像进行裁剪
                cv2.imwrite(crop_file,img)
                image= get_file_content(crop_file)
            else:

                image = get_file_content(open_file)

            res = client.bodySeg(image)#调用百度API 对人像进行分割
            labelmap = base64.b64decode(res['labelmap'])
            labelimg = np.frombuffer(labelmap,np.uint8)# 转化为np数组 0-255
            labelimg = cv2.imdecode(labelimg,1)
            labelimg = cv2.resize(labelimg,(width,height),interpolation=cv2.INTER_NEAREST)
            img_new = np.where(labelimg==1,255,labelimg)# 将 1 转化为 255
            cv2.imwrite(save_file,img_new)
            print(save_file,'save successfully')



def video_jpg(video_path,Pic_path):
    '''视频切帧
    video_path:视频路径；
    pic_path，保存图片路径
    '''
    vc = cv2.VideoCapture(video_path)
    c =0
    if vc.isOpened():
        rval,frame = vc.read()# 读取视频帧
    else:
        rval=False

    while rval:
        rval,frame = vc.read()# 读取每一视频帧，并保存至图片中

        cv2.imwrite(os.path.join(Pic_path,'{}.jpg'.format(c)),frame)
        c += 1
        print('第 {} 张图片存放成功！'.format(c))




def download_danmu():
    '''弹幕下载并存储'''
    cid = '141367679'# video_id
    url = 'http://comment.bilibili.com/{}.xml'.format(cid)

    f = open('danmu.txt','w+',encoding='utf-8') #打开 txt 文件
    res = requests.get(url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text,'lxml')
    items = soup.find_all('d')# 找到 d 标签

    for item in items:
        text = item.text
        print('---------------------------------'*10)
        print(text)

        seg_list = jieba.cut(text,cut_all =True)# 对字符串进行分词处理，方便后面制作词云图
        for j in seg_list:
            print(j)
            f.write(j)
            f.write('\n')
    f.close()




def Gen_wordart(mask_path,cloud_path):
    '''
    生成词云图
    :param mask_path:二值化图像存放路径
    :param cloud_path: 词云图保存文件路径
    :return:
    '''
    word_list = []
    with open('danmu.txt',encoding='utf-8') as f:
        con = f.read().split('\n')# 读取txt文本词云文本
        for i in con:
            if re.findall('[\u4e00-\u9fa5]+', str(i), re.S): #去除无中文的词频
                word_list.append(i)

    for i in os.listdir(mask_path):
        open_file = os.path.join(mask_path,i)
        save_file = os.path.join(cloud_path,i)

        if not os.path.exists(save_file):
            # 随机索引前 start 频率词
            start = random.randint(0, 15)
            word_counts = collections.Counter(word_list)
            word_counts = dict(word_counts.most_common()[start:])
            background = 255- np.array(Image.open(open_file))

            wc =WordCloud(
                background_color='black',
                max_words=500,
                mask=background,
                mode = 'RGB',
                font_path ="D:/Data/fonts/HGXK_CNKI.ttf",# 设置字体路径，用于设置中文,

            ).generate_from_frequencies(word_counts)
            wc.to_file(save_file)
            print(save_file,'Save Sucessfully!')




def image_video(origin_path,wordart_path,video_path):

    '''
    图片合成视频
    :param origin_path:存放原图片文件路径
    :param wordart_path:存放词云图文件路径
    :param video_path:生成词云视频存放路径
    :return:
    '''

    num_list = [int(str(i).split('.')[0]) for i in os.listdir(origin_path)]
    fps = 24# 视频帧率，越大越流畅
    height,width,_=cv2.imread(os.path.join(origin_path,'{}.jpg'.format(num_list[0]))).shape # 视频高度和宽度
    width = width*2
    # 创建一个写入操作;
    video_writer = cv2.VideoWriter(video_path,cv2.VideoWriter_fourcc(*'mp4v'),fps,(width,height))

    for i in sorted(num_list):
        i = '{}.jpg'.format(i)
        ori_jpg = os.path.join(origin_path,str(i))
        word_jpg = os.path.join(wordart_path,str(i))
        # com_jpg = os.path.join(Composite_path,str(i))
        ori_arr = cv2.imread(ori_jpg)
        word_arr = cv2.imread(word_jpg)

        # 利用 Numpy 进行拼接
        com_arr = np.hstack((ori_arr,word_arr))
        # cv2.imwrite(com_jpg,com_arr)# 合成图保存
        video_writer.write(com_arr) # 将每一帧画面写入视频流中
        print("{} Save Sucessfully---------".format(ori_jpg))
    video_writer.release()
