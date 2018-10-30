# -*- coding: utf-8 -*-
#Filename:ShowFileProperties.py
#！/usr/bin/env python
import os,time
from pymediainfo import MediaInfo
def VisitDir(path):
    li= os.listdir(path)
    for filepath in li:
        pathname = os.path.join(path,filepath)
        if not os.path.isfile(pathname):
               pass
        else:
            media_info = MediaInfo.parse(pathname)
            for track in media_info.tracks:
                if(track.track_type == 'Video'):
                    print("height: %s, width: %s" % (track.height, track.width))
                pass
            print(media_info)
if __name__== "__main__":
     path =r"download\\single"
     VisitDir(path)
