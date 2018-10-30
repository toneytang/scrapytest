# -*- coding: utf-8 -*-
#Filename:ShowFileProperties.py
#！/usr/bin/env python
import os,time,sys
#sys.path.append("..")
from separatefile import *


#print(os.path.abspath('test.py'))
#print(sys.path[0])


sourcePath = r"douyin\\download\\single"
targetPath = r"douyin\\download"
separateFile(sourcePath, targetPath)
