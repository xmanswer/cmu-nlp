# -*- coding: utf-8 -*-
"""
Created on Wed Sep 07 12:01:52 2016
This script will replace restricted names with John Smith
@author: minxu
"""

import re
import os

FULL_NAME = 'John Smith'
LAST_NAME = 'Smith'
NAMES = 'names.txt'
ORI_DIR = 'nyt'
MOD_DIR = 'minxu-nyt-modified'
N_FILES = 1000
names = set()

if not os.path.exists(MOD_DIR):
    os.mkdir(MOD_DIR)

def process_line(line):
#    rep = False
    for name in names:
        reg = r'\b' + name + r'\b'
        newline = re.sub(reg, FULL_NAME, line)
        if newline != line:
            #rep = True
            reg = r'\b' + name.split()[1] + r'\b'
            newline = re.sub(reg, LAST_NAME, newline)
        line = newline
    
#    if rep:
#        print line
    return line

names = set()
with open(NAMES) as f:
    for l in f:
        names.add(l.strip())

for i in range(N_FILES):
    fin = ORI_DIR + '/file' + str(i) + '.txt'
    fout = open(MOD_DIR + '/file' + str(i) + '.txt', 'w')
    with open(fin) as f:
        line = f.readline()
        line = process_line(line)
        fout.write(line)
    fout.close()
    
    