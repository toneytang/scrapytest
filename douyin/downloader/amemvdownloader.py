# -*- coding: utf-8 -*-

import os
import sys, getopt
sys.path.append("..")
#print(sys.path)
import hashlib
import codecs
import requests
import re
from six.moves import queue as Queue
from threading import Thread
import json

# Setting timeout
TIMEOUT = 10

# Retry times
RETRY = 5

# Numbers of downloading threads concurrently
THREADS = 10

userVideoType = 'girl'
diggLevelNumber = 5000

HEADERS = {
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'upgrade-insecure-requests': '1',
    'user-agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
}

PC_HEADERS = {
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'upgrade-insecure-requests': '1',
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
}

FAILED_FILE_MD5 = '6419a414275112dcc2e073f62a3ce91e'


class DownloadWorker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            medium_type, uri, download_url, target_folder = self.queue.get()
            self.download(medium_type, uri, download_url, target_folder)
            self.queue.task_done()
    def videoDowloadedCheck(self, fileName):
        '''
        print('file name is '+fileName)
        clipDB_instance = clipsDB()
        videoInsetSuccessFlag = clipDB_instance.getOneClipById(fileName)
        if videoInsetSuccessFlag == False: 
            print("video %s downloaded before!!" % fileName)
            return False
        else:
            return True
        '''
        return False
    def videoLogIntoDB(self, fileName):
        '''
        clip1 = clipClass()
        clip1.clipID = fileName
        clipDB_instance = clipsDB()
        clipDB_instance.insertOneClip(clip1)
        
        print('input video to DB')
        '''
        pass
        

    def download(self, medium_type, uri, download_url, target_folder):
        if medium_type == 'image':
            self._download(uri, 'image', download_url, target_folder)
        elif medium_type == 'video':
            download_url = 'https://aweme.snssdk.com/aweme/v1/play/?{0}'
            download_params = {
                'video_id': uri,
                'line': '0',
                'ratio': '720p',
                'media_type': '4',
                'vr_type': '0',
                'test_cdn': 'None',
                'improve_bitrate': '0'
            }
            download_url = download_url.format(
                '&'.join(
                    [key + '=' + download_params[key] for key in download_params]
                )
            )
            self._download(uri, 'video', download_url, target_folder)
        elif medium_type == 'videowm':
            self._download(uri, 'video', download_url, target_folder)
            download_url = 'https://aweme.snssdk.com/aweme/v1/play/?video_id={0}&line=0'
            download_url = download_url.format(uri)
            res = requests.get(download_url, headers=HEADERS, allow_redirects=False)
            download_url = res.headers['Location']
            self._download(uri, 'video', download_url, target_folder)

    def _download(self, uri, medium_type, medium_url, target_folder):
        file_name = uri
        if medium_type == 'video':
            file_name += '.mp4'
        elif medium_type == 'image':
            file_name += '.jpg'
            file_name = file_name.replace("/", "-")
        else:
            return

        file_path = os.path.join(target_folder, file_name)
        fileExistFlag = self.videoDowloadedCheck(file_name)
        print(str(fileExistFlag))
        if not (os.path.isfile(file_path) or fileExistFlag):#如果文件不存在，即下载
            print("Downloading %s from %s.\n" % (file_name, medium_url))
            retry_times = 0
            while retry_times < RETRY:
                try:
                    print('medium_url = '+medium_url)
                    resp = requests.get(medium_url, headers=HEADERS, stream=True, timeout=TIMEOUT)
                    if resp.status_code == 403:
                        retry_times = RETRY
                        print("Access Denied when retrieve %s.\n" % medium_url)
                        raise Exception("Access Denied")
                    with open(file_path, 'wb') as fh:
                        for chunk in resp.iter_content(chunk_size=1024):
                            fh.write(chunk)
                        self.videoLogIntoDB(file_name)
                    break
                except:
                    pass
                retry_times += 1
            else:
                try:
                    os.remove(file_path)
                except OSError:
                    pass
                print("Failed to retrieve %s from %s.\n" % (file_name, medium_url))
                

class CrawlerScheduler(object):

    def __init__(self, items):
        self.links = items
        self.queue = Queue.Queue()
        self.scheduling()

    # 短地址转长地址
    def getRealAddress(self, url):
        if url.find('v.douyin.com') < 0: return url
        res = requests.get(url, headers=HEADERS, allow_redirects=False)
        return res.headers['Location']

    def generateSignature(self, str):
        p = os.popen('node fuck-byted-acrawler.js %s' % str)
        return p.readlines()[0]

    def calculateFileMd5(self, filename):
        hmd5 = hashlib.md5()
        fp = open(filename, "rb")
        hmd5.update(fp.read())
        return hmd5.hexdigest()

    def checkFile(self, directory):
        current_folder = os.getcwd()
        targetDir = os.path.join(current_folder, 'download/%s' % directory)
        list = os.listdir(targetDir)
        failedUriList = []
        for i in range(0, len(list)):
            path = os.path.join(targetDir, list[i])
            if not os.path.isfile(path): break
            if self.calculateFileMd5(path) == FAILED_FILE_MD5:
                uri = re.findall(targetDir + '/(.*).mp4', path)
                if uri: failedUriList.append(uri[0])
                os.remove(path)
        if failedUriList:
            print('failed downloads: %d, The downgrade plan is ready to be downloaded!' % len(failedUriList))
            for uri in self.numbers:
                self.queue.put(('videowm', uri, None, targetDir))
            self.queue.join()
            print("\nFinish Downloading All the videos from %d\n\n" % len(failedUriList))

    def scheduling(self):
        for x in range(THREADS):
            worker = DownloadWorker(self.queue)
            worker.daemon = True
            worker.start()

        for link in self.links:
            self.download_link(link)
        pass

    def download_link(self, link):
        print('single download')
        current_folder = os.getcwd()
        target_folder = os.path.join(current_folder, 'download\\single')
        if not os.path.isdir(target_folder):
            os.mkdir(target_folder)

        uri = re.findall('(?<=\\bvideo_id=)\\w{32}', link)
        self.queue.put(('videowm', uri[0], link, target_folder))
        self.queue.join()
        self.checkFile('single')



