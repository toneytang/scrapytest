# -*- coding: utf-8 -*-
import os, random, shutil
import sys
from pymediainfo import MediaInfo
class separateFile(object):
    def __init__(self, sourcePath, targetPath):
        current_folder = sys.path[0]+'\\'
        source_folder = current_folder + sourcePath
        target_folder = current_folder + targetPath
        li= os.listdir(source_folder)
        print(li)
        if not os.path.isdir(target_folder):
            os.mkdir(target_folder)
        if not os.path.isdir(target_folder + '\\horizon'):
            os.mkdir(target_folder + '\\horizon')
        if not os.path.isdir(target_folder + '\\vertical'):
            os.mkdir(target_folder)
            
        for filepath in li:
            #print(filepath)
            pathname = os.path.join(source_folder,filepath)
            if not os.path.isfile(pathname):
                   pass
            else:
                media_info = MediaInfo.parse(pathname)
                for track in media_info.tracks:
                    if(track.track_type == 'Video'):
                        #print("height: %s, width: %s" % (track.height, track.width))
                        if(track.width > track.height) :
                            shutil.move(source_folder+'\\'+filepath, target_folder + '\\horizon'+'\\'+filepath)
                            print("Move file height: %s, width: %s" % (track.height, track.width))
                        else:
                            shutil.move(source_folder+'\\'+filepath, target_folder + '\\vertical'+'\\'+filepath)
                            print("Move file height: %s, width: %s" % (track.height, track.width))
                    pass
                #print(media_info)
    pass
if __name__== "__main__":
     sourcePath =r"douyin\download\single"
     targetPath =r"douyin\download"
     separateFile(sourcePath, targetPath)