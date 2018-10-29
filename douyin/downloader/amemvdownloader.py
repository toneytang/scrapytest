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
        self.numbers = []
        self.challenges = []
        self.musics = []
        self.videos = []
        print('start to check items')
        for i in range(len(items)):
            url = self.getRealAddress(items[i])
            print('url: '+url)
            if not url: 
                print('not url')
                continue

            if re.search('share/user', url):
                print('user link')
                user_id = re.findall('share/user/(\d+)', url)
                if not len(user_id): continue
                res = requests.get(url, headers=HEADERS)
                if not res: continue
                dytk = re.findall("dytk: '(.*)'", res.content.decode('utf-8'))
                if len(dytk):
                    dytk.insert(0, user_id[0])
                    self.numbers.append(dytk)

            if re.search('share/challenge', url):
                print('challenge link')
                challenges_id = re.findall('share/challenge/(\d+)', url)
                if len(challenges_id): self.challenges.append(challenges_id[0])

            if re.search('share/music', url):
                print('music link')
                musics_id = re.findall('share/music/(\d+)', url)
                if len(musics_id): self.musics.append(musics_id[0])
            if re.search('share/video', url):
                print('single video link')
                video_link = []
                video_link.append([(re.findall('share/video/(\d+)', url))[0],(re.findall('mid=(\d+)', url))[0]])
                
                if len(video_link): self.videos.append(video_link[0])

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

        for params in self.numbers:
            self.download_videos(params)

        for challenge in self.challenges:
            self.download_challenge_videos(challenge)

        for music in self.musics:
            self.download_music_videos(music)
            
        for video in self.videos:
            self.download_single_video(video)

    def download_videos(self, params):
        if len(params) < 2: return
        number = params[0]
        dytk = params[1]
        video_count = self._download_user_media(number, dytk)
        self.queue.join()
        print("\nAweme number %s, video number %s\n\n" % (number, str(video_count)))
        print("\nFinish Downloading All the videos from %s\n\n" % number)
        self.checkFile(userVideoType)

    def download_challenge_videos(self, challenge):
        video_count = self._download_challenge_media(challenge)
        self.queue.join()
        print("\nAweme challenge #%s, video number %d\n\n" % (challenge, video_count))
        print("\nFinish Downloading All the videos from #%s\n\n" % challenge)
        self.checkFile('#' + challenge)

    def download_music_videos(self, music):
        video_count = self._download_music_media(music)
        self.queue.join()
        print("\nAweme music @%s, video number %d\n\n" % (music, video_count))
        print("\nFinish Downloading All the videos from @%s\n\n" % music)
        self.checkFile('@' + music)

    def download_single_video(self, params):
        print('single download')
        print(params[0])#folder
        print(params[1])#id
        if len(params) < 2: return
        video_folder = params[0]
        video_id = params[1]
        video_count = self._download_single_media(video_folder, video_id)
        self.queue.join()
        print("\nAweme number %s, video number %s\n\n" % (video_id, str(video_count)))
        print("\nFinish Downloading All the videos from %s\n\n" % video_id)
        self.checkFile('single')

    def _join_download_queue(self, aweme, target_folder):
        try:
            if aweme.get('video', None):
                self.queue.put(('video', aweme['video']['play_addr']['uri'], None, target_folder))
            else:
                if aweme.get('image_infos', None):
                    image = aweme['image_infos']['label_large']
                    self.queue.put(('image', image['uri'], image['url_list'][0], target_folder))

        except KeyError:
            print('KeyError')
            return
        except UnicodeDecodeError:
            print("Cannot decode response data from DESC %s" % aweme['desc'])
            return

    def __download_favorite_media(self, user_id, dytk, signature, favorite_folder, video_count):
        if not os.path.exists(favorite_folder):
            os.makedirs(favorite_folder)
        favorite_video_url = "https://www.douyin.com/aweme/v1/aweme/favorite/?{0}"
        favorite_video_params = {
            'user_id': str(user_id),
            'count': '21',
            'max_cursor': '0',
            'aid': '1128',
            '_signature': signature,
            'dytk': dytk
        }
        max_cursor = None
        while True:
            if max_cursor:
                favorite_video_params['max_cursor'] = str(max_cursor)
            url = favorite_video_url.format(
                '&'.join([key + '=' + favorite_video_params[key] for key in favorite_video_params]))
            res = requests.get(url, headers=HEADERS)
            contentJson = json.loads(res.content.decode('utf-8'))
            favorite_list = contentJson.get('aweme_list', [])
            for aweme in favorite_list:
                video_count += 1
                self._join_download_queue(aweme, favorite_folder)
            if contentJson.get('has_more') == 1:
                max_cursor = contentJson.get('max_cursor')
            else:
                break
        return video_count

    def _download_user_media(self, user_id, dytk):
        current_folder = os.getcwd()
        target_folder = os.path.join(current_folder, 'download/%s' % userVideoType)
        if not os.path.isdir(target_folder):
            os.mkdir(target_folder)

        if not user_id:
            print("Number %s does not exist" % user_id)
            return

        signature = self.generateSignature(str(user_id))

        user_video_url = "https://www.amemv.com/aweme/v1/aweme/post/?{0}"
        user_video_params = {
            'user_id': str(user_id),
            'count': '21',
            'max_cursor': '0',
            'aid': '1128',
            '_signature': signature,
            'dytk': dytk
        }
        max_cursor, video_count = None, 0
        while True:
            if max_cursor:
                user_video_params['max_cursor'] = str(max_cursor)
            url = user_video_url.format('&'.join([key + '=' + user_video_params[key] for key in user_video_params]))
            url = url.replace("\r", "").replace("\n", "")
            res = requests.get(url, headers=HEADERS)
            contentJson = json.loads(res.content.decode('utf-8'))
            js = json.dumps(contentJson, sort_keys=True, indent=4, separators=(',', ':'))
            aweme_list = contentJson.get('aweme_list', [])
            #print(js)
            if not aweme_list:
                break
            for aweme in aweme_list:
                #由于点赞量小于10000时采用整型数字，否则采用以w为单位的字符串表示，比如72000表示为‘7.2w’的字符串。所以先判定是否为字符串，为字符串者，就是超过10000
                #筛选条件，如果点赞量超过5000或者是字符串。即选中，否则排除
                if(isinstance(aweme['statistics']['digg_count'],str) or aweme['statistics']['digg_count']>5000):
                    video_count += 1
                    self._join_download_queue(aweme, target_folder)
                    print("add one video" + str(aweme['statistics']['digg_count']))
                else :
                    print("pass one video" + str(aweme['statistics']['digg_count']))
                    pass
            if contentJson.get('has_more') == 1:
                max_cursor = contentJson.get('max_cursor')
            else:
                break
        if not noFavorite:
            favorite_folder = target_folder + '/favorite'
            video_count = self.__download_favorite_media(user_id, dytk, signature, favorite_folder, video_count)

        if video_count == 0:
            print("There's no video in number %s." % user_id)

        return video_count

    def _download_challenge_media(self, challenge_id):

        if not challenge_id:
            print("Challenge #%s does not exist" % challenge_id)
            return
        current_folder = os.getcwd()
        target_folder = os.path.join(current_folder, 'download/#%s' % challenge_id)
        if not os.path.isdir(target_folder):
            os.mkdir(target_folder)

        signature = self.generateSignature(str(challenge_id) + '9' + '0')

        challenge_video_url = "https://www.iesdouyin.com/aweme/v1/challenge/aweme/?{0}"
        challenge_video_params = {
            'ch_id': str(challenge_id),
            'count': '9',
            'cursor': '0',
            'aid': '1128',
            'screen_limit': '3',
            'download_click_limit': '0',
            '_signature': signature
        }

        cursor, video_count = None, 0
        while True:
            if cursor:
                challenge_video_params['cursor'] = str(cursor)
                challenge_video_params['_signature'] = self.generateSignature(str(challenge_id) + '9' + str(cursor))
            url = challenge_video_url.format(
                '&'.join([key + '=' + challenge_video_params[key] for key in challenge_video_params]))
            res = requests.get(url, headers=HEADERS)
            contentJson = json.loads(res.content.decode('utf-8'))
            aweme_list = contentJson.get('aweme_list', [])
            if not aweme_list:
                break
            for aweme in aweme_list:
                video_count += 1
                self._join_download_queue(aweme, target_folder)
            if contentJson.get('has_more') == 1:
                cursor = contentJson.get('cursor')
            else:
                break
        if video_count == 0:
            print("There's no video in challenge %s." % challenge_id)
        return video_count

    def _download_music_media(self, music_id):
        if not music_id:
            print("Challenge #%s does not exist" % music_id)
            return
        current_folder = os.getcwd()
        target_folder = os.path.join(current_folder, 'download/@%s' % music_id)
        if not os.path.isdir(target_folder):
            os.mkdir(target_folder)

        signature = self.generateSignature(str(music_id))
        music_video_url = "https://www.iesdouyin.com/aweme/v1/music/aweme/?{0}"
        music_video_params = {
            'music_id': str(music_id),
            'count': '9',
            'cursor': '0',
            'aid': '1128',
            'screen_limit': '3',
            'download_click_limit': '0',
            '_signature': signature
        }
        cursor, video_count = None, 0
        while True:
            if cursor:
                music_video_params['cursor'] = str(cursor)
                music_video_params['_signature'] = self.generateSignature(str(music_id) + '9' + str(cursor))

            url = music_video_url.format(
                '&'.join([key + '=' + music_video_params[key] for key in music_video_params]))
            res = requests.get(url, headers=HEADERS)
            contentJson = json.loads(res.content.decode('utf-8'))
            aweme_list = contentJson.get('aweme_list', [])
            if not aweme_list:
                break
            for aweme in aweme_list:
                video_count += 1
                self._join_download_queue(aweme, target_folder)
            if contentJson.get('has_more') == 1:
                cursor = contentJson.get('cursor')
            else:
                break
        if video_count == 0:
            print("There's no video in music %s." % music_id)
        return video_count

    def _download_single_media(self, video_folder, video_id):
        if not video_id:
            print("video #%s does not exist" % video_id)
            return
        current_folder = os.getcwd()
        target_folder = os.path.join(current_folder, 'download\\single')
        if not os.path.isdir(target_folder):
            os.mkdir(target_folder)

        #signature = self.generateSignature(str(video_id))
        single_video_url = "https://www.amemv.com/share/video/"+str(video_folder)+ "/?mid=" + str(video_id)

        print(single_video_url)
        res = requests.get(single_video_url, headers=PC_HEADERS)
        print("?????")
        download_url = re.findall("(?<=playAddr: \").*?(?=\",)", res.text)
        uri = re.findall('(?<=\\bvideo_id=)\\w{32}', str(download_url[0]))
        download_url[0] = download_url[0].replace("playwm", "play")
        print('download_url[0]'+ download_url[0])
        print('uri[0]'+uri[0])
        
        
        self.queue.put(('videowm', uri[0], download_url[0], target_folder))
        self.queue.join()
        
        

        
        """
        cursor, video_count = None, 0
        while True:
            if cursor:
                music_video_params['cursor'] = str(cursor)
                music_video_params['_signature'] = self.generateSignature(str(music_id) + '9' + str(cursor))

            url = music_video_url.format(
                '&'.join([key + '=' + music_video_params[key] for key in music_video_params]))
            res = requests.get(url, headers=HEADERS)
            contentJson = json.loads(res.content.decode('utf-8'))
            aweme_list = contentJson.get('aweme_list', [])
            if not aweme_list:
                break
            for aweme in aweme_list:
                video_count += 1
                self._join_download_queue(aweme, target_folder)
            if contentJson.get('has_more') == 1:
                cursor = contentJson.get('cursor')
            else:
                break
        """

        return 1

def usage():
    print("1. Please create file share-url.txt under this same directory.\n"
          "2. In share-url.txt, you can specify amemv share page url separated by "
          "comma/space/tab/CR. Accept multiple lines of text\n"
          "3. Save the file and retry.\n\n"
          "Sample File Content:\nurl1,url2\n\n"
          "Or use command line options:\n\n"
          "Sample:\npython amemv-video-ripper.py number1,number2\n\n\n")
    print(u"未找到share-url.txt文件，请创建.\n"
          u"请在文件中指定抖音分享页面URL，并以 逗号/空格/tab/表格鍵/回车符 分割，支持多行.\n"
          u"保存文件并重试.\n\n"
          u"例子: url1,url12\n\n"
          u"或者直接使用命令行参数指定站点\n"
          u"例子: python amemv-video-ripper.py url1,url2")


def parse_sites(fileName):
    with open(fileName, "rb") as f:
        txt = f.read().rstrip().lstrip()
        txt = codecs.decode(txt, 'utf-8')
        txt = txt.replace("\t", ",").replace("\r", ",").replace("\n", ",").replace(" ", ",")
        txt = txt.split(",")
    numbers = list()
    for raw_site in txt:
        site = raw_site.lstrip().rstrip()
        if site:
            numbers.append(site)
    return numbers


noFavorite = True
videoNameFile = open("videos.txt", 'a+')

if __name__ == "__main__":
    content, opts, args = None, None, []
    
    if(videoNameFile != None):
        videoNameList = videoNameFile.readlines();
    else:
        videoNameList = []
    try:
        if len(sys.argv) >= 2:
            opts, args = getopt.getopt(sys.argv[1:], "hi:o:", ["no-favorite"])
    except getopt.GetoptError as err:
        usage()
        sys.exit(2)

    if not args:
        # check the sites file
        filename = "share-url.txt"
        if os.path.exists(filename):
            content = parse_sites(filename)
            print('load file')
        else:
            usage()
            sys.exit(1)
    else:
        content = (args[0] if args else '').split(",")

    if len(content) == 0 or content[0] == "":
        print('no link')
        usage()
        sys.exit(1)

    if opts:
        for o, val in opts:
            if o in ("-nf", "--no-favorite"):
                noFavorite = True
                break

    CrawlerScheduler(content)
