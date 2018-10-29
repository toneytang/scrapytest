# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

#import pymysql
#import datetime

from downloader.amemvdownloader import CrawlerScheduler as cs
class DouyinPipeline(object):

    #初始化连接MySQl数据库，这里charset一定要设置为utf8mb4，这样才可以存储表情符号，抖音中是有很多表情符号的，创建数据库时也要编码设置为utf8mb4。下面passwd输入自己的密码
    def __init__(self):
        '''
        self.connect = pymysql.connect(
            host = "127.0.0.1",
            port = 3306,
            db = "douyin",
            user = "root",
            passwd = "123456",
            charset = 'utf8mb4',
            use_unicode = True
            )
        self.cursor = self.connect.cursor()
        '''
        #print("连接数据库成功，正在存入数据库...")
        pass


    def process_item(self, item, spider):
        '''
        #执行sql语句，判断数据库中是否有此条视频信息，没有就插入，有就跳过，这里跳过没有更新数据库，因为更新也就更新下评论内容，这里就不更新了
        sql = "SELECT aweme_id FROM douyin_info WHERE aweme_id = {};".format(item['aweme_id'])
        status = self.cursor.execute(sql)
        if status == 0:
            self.cursor.execute(
                """insert into douyin_info(create_time,author_user_id, aweme_id, video_desc, digg_count ,share_count, comment_count,comment_list,share_url,origin_cover,play_addr,download_addr)
                value (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                 str(item['author_user_id']),
                 item['aweme_id'],
                 item['video_desc'],
                 item['digg_count'],
                 item['share_count'],
                 item['comment_count'],
                 str(item['comment_list']),
                 item['share_url'],
                 str(item['origin_cover']),
                 str(item['play_addr']),
                 str(item['download_addr'])
                 ))
            self.connect.commit()
        else:pass
        '''
        '''
        print(str(item['author_user_id'])+
              item['aweme_id']+
              item['video_desc']+
              item['digg_count']+
              item['share_count']+
              item['comment_count']+
              str(item['comment_list'])+
              item['share_url']+
              str(item['origin_cover'])+
              str(item['play_addr'])+
              str(item['download_addr']))
        '''
        L = []
        L.append(item['share_url'] + ',')
        print("try to download")
        cs(L)
        return item

    def close_spider(self,spider):
        #self.connect.close()
        pass