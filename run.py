import time
import os
count = 0
while True:
    print('*****************************************************')
    print('****    count = %d                            *******' % count)
    print('*****************************************************')
    os.system("scrapy crawl douyinSpider")
    count = count + 1
    time.sleep(10*60)  #每隔一天运行一次 24*60*60=86400s
