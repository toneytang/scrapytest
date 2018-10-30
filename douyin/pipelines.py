# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sys
sys.path.append(".")

from downloader.amemvdownloader import CrawlerScheduler as cs
class DouyinPipeline(object):
    def __init__(self):
        pass
    def process_item(self, item, spider):
        L = []
        L.append(item['play_addr'])
        print("try to download")
        cs(L)
        return item
    def close_spider(self,spider):
        pass
