import time
import os
from separatefile import *
count = 0
while True:
    print('*****************************************************')
    print('****    count = %d                            *******' % count)
    print('*****************************************************')
    os.system("scrapy crawl douyinSpider")
    count = count + 1
    sourcePath = r"douyin\\download\\single"
    targetPath = r"douyin\\download"
    separateFile(sourcePath, targetPath)
    time.sleep(10*60)  #每隔一天运行一次 24*60*60=86400s
    