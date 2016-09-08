# -*- coding: utf-8 -*-
"""
Created on Wed Sep 07 14:05:32 2016
This script can read encrypted and regular files,
and decrypt the encrypted file based on frequency analysis of
simple letter substitution.
It combines 1-gram frequencies, 2-gram frequencies of letters and a word
level edit distance analysis
@author: minxu
"""

import re

ORI_DIR = 'nyt'
N_FILES = 1000
INFILE = 'mit.txt'
OUTFILE = 'minxu-task2.txt'
K1, K2 = 1, 12 #weights for 1-gram and 2-gram
dict1, dict2, dict1_2, dict2_2 = dict(), dict(), dict(), dict()
ori_count, map_count = dict(), dict()

#help func to build dictionary
def build_dict(dic, w):
    w = w.lower()
    dic[w] = dic[w] + 1 if w in dic else 1

#build dictionaries from mit.txt
with open(INFILE) as f:    
    lines = f.read().splitlines()
    map(lambda w : build_dict(ori_count, w), [i.lower() for j in [re.sub(r'[^a-zA-Z]', ' ', l).split() for l in lines] for i in j])
    lines = map(lambda l : re.sub(r'[^a-zA-Z]', '', l), lines)
    map(lambda l : map(lambda w : build_dict(dict1, w) , l), lines)
    map(lambda l : map(lambda w : build_dict(dict1_2, w) , [l[i : i+2] for i in range(0, len(l)-1)]), lines)

#build dictionaries from task1 files
for i in range(N_FILES):
    with open(ORI_DIR + '/file' + str(i) + '.txt') as f:
        lines = f.read().splitlines()
        map(lambda w : build_dict(map_count, w), [i.lower() for j in [re.sub(r'[^a-zA-Z]', ' ', l).split() for l in lines] for i in j])
        lines = map(lambda l : re.sub(r'[^a-zA-Z]', '', l), lines)
        map(lambda l : map(lambda w : build_dict(dict2, w) , l), lines)
        map(lambda l : map(lambda w : build_dict(dict2_2, w) , [l[i : i+2] for i in range(0, len(l)-1)]), lines)

#first layer mapping based on letter freq
tups1 = sorted(dict1.items(), key=lambda x: x[1], reverse=True)
tups2 = sorted(dict2.items(), key=lambda x: x[1], reverse=True)
tups1_2 = sorted(dict1_2.items(), key=lambda x: x[1], reverse=True)
tups2_2 = sorted(dict2_2.items(), key=lambda x: x[1], reverse=True)
ori_sortedset = sorted(ori_count.items(), key=lambda x: x[1], reverse=True)
map_sortedset = sorted(map_count.items(), key=lambda x: x[1], reverse=True)
dicmap_single, dicmap_double = dict(), dict()
size1, size2 = sum(dict1.values()), sum(dict2.values())

#generate score based on how far off the two words are in terms of frequency
def gen_score(dicmap, (k1, v1), (k2, v2)):
    prec1 = float(v1) / float(size1)
    prec2 = float(v2) / float(size2)
    if k1 not in dicmap:
        dicmap[k1] = dict()
    dicmap[k1][k2] = abs(prec2 - prec1)
    
#normalize the scores
def normalize(dic, k):
    vlist = dic[k].values()
    maxv, minv = max(vlist), min(vlist)
    dic[k] = {k : 1 - (v - minv) / (maxv - minv) for k, v in dic[k].iteritems()}
    size = sum(dic[k].values())
    dic[k] = {k : v / size for k, v in dic[k].iteritems()}

#calculate and normalize mapping scores for 1-gram and 2-gram letters
map(lambda tup1 : map(lambda tup2 : gen_score(dicmap_single, tup1, tup2), tups2), tups1)
map(lambda tup1 : map(lambda tup2 : gen_score(dicmap_double, tup1, tup2), tups2_2), tups1_2)
map(lambda k : normalize(dicmap_single, k), dicmap_single.keys())
map(lambda k : normalize(dicmap_double, k), dicmap_double.keys())

#combine 1-gram and 2-gram scores for mapping iteratively
#should achieve reasonably good mapping for now
dicmap = dict()
temp = dicmap_single
for _ in range(10):
    temp2 = dict()
    for k in dicmap_single:
        #1-gram score is based on previous mapping method
        map1 = dicmap_single[k]
        #calculate score for 2-gram
        map2 = dict()
        for k2, v2 in dicmap_double.iteritems():
            if not k2.startswith(k): continue
            for mapped_k, mapped_v in v2.iteritems():
                if mapped_k[0] not in map2:
                    map2[mapped_k[0]] = 0
                map2[mapped_k[0]] += mapped_v * temp[k2[1]][mapped_k[1]]
        #combine socres        
        score, mscore, map2sum = dict(), 0, sum(map2.values())
        for c in dicmap_single.keys():
            score[c] = (map1[c] ** (K1)) * ((map2[c] / map2sum) ** (K2))
            if score[c] > mscore:
                dicmap[k], mscore = c, score[c]
        dicscore_sum = sum(score.values())
        temp2[k] = {k:v/dicscore_sum for k,v in score.iteritems()}
    temp = temp2

#second layer word level mapping based on edit distance
#edit distance is some value between 0 and 1
def edit_distance(w1, w2):
    if len(w1) != len(w2):
        return (w1, w2, 1)
    ed = 0
    for i in range(len(w1)):
        if w1[i] != w2[i]:
            ed += 1
    return (w1, w2, float(ed) / len(w1))

#for each word in mit.txt, get the smallest edit distance word in nyt
edit_map = dict()
for w1 in ori_sortedset:
    w1_new = ''.join(dicmap[c] for c in w1[0])
    if w1_new not in map_count:
        cand = sorted(map(lambda w2 : edit_distance(w1_new, w2[0]), map_sortedset), key=lambda x: x[2])
        edit_map[w1[0]] = cand[0]

#rank the words in asc order of edit distance
#the more correct mapping there is, the higher the rank is
edit_list = edit_map.iteritems()
edit_sortedset = sorted(edit_list, key = lambda x : x[1][2])

successed = {k : False for k in temp}
#for each word, greedly identify correctly mapped letter
for tup in edit_sortedset:
    w1 = tup[0]
    w1_new = ''.join(dicmap[c] for c in w1)
    w2 = tup[1][1]
    for i in range(len(w1)):
        if w1_new[i] == w2[i]:
            successed[w1[i]] = True
        else: #if incorrect, assuming the corresponding letter is more correct
            if not successed[w1[i]]:
                successed[w1[i]] = True
                dicmap[w1[i]] = w2[i]
    if sum(v for i , v in successed.items()) == 26:
        break

#generate output, do char level processing to keep the format unchange
res = []
with open(INFILE) as f:
    for l in f:
        for w in l:
            if w >= 'a' and w <= 'z':
                res.append(dicmap[w])
            elif w >= 'A'and w <= 'Z':
                res.append(dicmap[w.lower()].upper())
            else:
                res.append(w)
outputstr = ''.join(res)

with open(OUTFILE, 'w') as f:
    f.write(outputstr)