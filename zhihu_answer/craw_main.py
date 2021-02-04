import requests
import random
from bs4 import BeautifulSoup as bs
import re
import os
import xlsxwriter
import time
from fake_useragent import UserAgent


class crawl_write(requests.Session):

    def __init__(self,ques_id,file_path,name_xls,limit):
        super().__init__()
        self.ques_id = ques_id
        self.file_path = file_path
        self.name_xls = name_xls
        self.start_row,self.start_col = 0,0
        self.time_out = 10
        self.limit = limit
        self.headers = dict()
        # 增加头文件；
        self.headers['user-agent'] ='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        # 创建文件夹
        self.build_xls(file_path,name_xls)
        # 进行数据爬取
        self.run(self.ques_id,self.limit)



    def get_data(self,url):
        '''获取数据'''
        a_str = self.get(url,headers = self.headers,timeout = self.time_out)
        if a_str.status_code ==200:
            a_str.encoding ='utf-8'

            try:
                for i in a_str.json()['data']:
                    print(i)
                    self.start_row += 1
                    self.start_col = 0
                    question_id = i['question']['title']
                    author_name = i['author']['name']
                    author_icon_url = i['author']['avatar_url']
                    if i['author']['gender'] == 0:
                        author_sex = '女'
                    elif i['author']['gender'] == 1:
                        author_sex = '男'
                    else:
                        author_sex = None
                    author_follwer_count = i['author']['follower_count']
                    contents = i['content']
                    content_vote_count = i['voteup_count']
                    comment_count = i['comment_count']
                    content_created_time = i['created_time']
                    # 转化为time
                    if time.localtime(int(content_created_time)):
                        content_created_time = time.localtime(int(content_created_time))
                        content_created_time = time.strftime('%Y-%m-%d',content_created_time)
                        print(content_created_time)

                    contents = str(contents).replace(r'<br/>', '\n').replace(r'</p>', '\n').replace(r'<p>', '\n')
                    if re.findall(r'(https.*?.jpg)', contents):
                        jpg_list = re.findall(r'(https.*?.jpg)', contents)
                    else:
                        jpg_list = None
                    self.worksheet.write(self.start_row, self.start_col, str(author_name))
                    self.start_col += 1
                    self.worksheet.write(self.start_row, self.start_col, str(author_sex))
                    self.start_col += 1
                    self.worksheet.write(self.start_row, self.start_col, str(author_icon_url))
                    self.start_col += 1
                    self.worksheet.write(self.start_row, self.start_col, str(author_follwer_count))
                    self.start_col += 1
                    self.worksheet.write(self.start_row, self.start_col, str(contents))
                    self.start_col += 1
                    self.worksheet.write(self.start_row, self.start_col, str(content_vote_count))
                    self.start_col += 1
                    self.worksheet.write(self.start_row, self.start_col, str(comment_count))
                    self.start_col += 1
                    self.worksheet.write(self.start_row, self.start_col, str(content_created_time))
                    self.start_col += 1
                    self.worksheet.write(self.start_row, self.start_col, str(jpg_list))
            except Exception as e:
                print(e)


        else:
            #更换User-agent,进行重新更新；
            ua = UserAgent()
            google_ua =ua.chrome
            self.headers['user-agent'] = google_ua
            url1 = url
            self.get_data(url1)


    def build_xls(self,path,name):
        #创建sheet
        file_path = os.path.join(path,'{}.xlsx'.format(name))
        self.workbook1 = xlsxwriter.Workbook(file_path)
        self.worksheet = self.workbook1.add_worksheet()
        data_first = (
                      'author_name',
                      'author_sex',
                      'author_icon_url',
                      'author_follower_count',
                      'answer_contend',
                      'answer_voted',
                      'comment_count',
                      'created_time',
                      'jpg_list')

        for i in data_first:
            self.worksheet.write(self.start_row,self.start_col,i)
            self.start_col +=1

    def random_step(self):
        a = random.randint(2,5)
        return a

    def run(self,a_id,limit):
        for i in range(1,20):
            time.sleep(self.random_step())
            offset1 = limit*i
            url = 'https://www.zhihu.com/api/v4/questions/{}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit={}&offset={}&platform=desktop&sort_by=default'.format(a_id,limit,offset1)
            print('准备爬取第{}页'.format(i))
            print(url)
            self.get_data(url)
        self.workbook1.close()
        print('爬取完毕，数据保存完毕！')


if __name__ =='__main__':
    path = 'E:/ceshi'
    name = '神逻辑'
    ques_id = 267808119
    limit = 5
    crawl_write(ques_id,path,name,limit)
