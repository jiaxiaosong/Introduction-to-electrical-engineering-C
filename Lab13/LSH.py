#!/usr/bin/env python
# -*- coding=utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import cv2
import numpy as np
from math import *
import os
import time



#传入图片和投影集合,得到一张图片的投影到Hamming空间的向量
def get_cast(p, cast_set):
    #量化P 到　0,1,2
    p = quantization(p, 0.345166, 0.319847)
    #投影到Hamming空间
    cast_vec = cast_to_hamming(p, cast_set)
    return cast_vec


#得到12维Ｐ向量
def get_vector(img):
    B, G, R = cv2.split(img)
    vec = []
    height, width = img.shape[0:2]
    #H1
    b = B[0:int(height/2), 0:int(width/2)].sum()
    g = G[0:int(height/2), 0:int(width/2)].sum()
    r = R[0:int(height/2), 0:int(width/2)].sum()
    total = b + g + r
    vec += [float(b)/total, float(g)/total, float(r)/total]
    #H2
    b = B[0:int(height/2), int(width/2)+1:width].sum()
    g = G[0:int(height/2), int(width/2)+1:width].sum()
    r = R[0:int(height/2), int(width/2)+1:width].sum()
    total = b + g + r
    vec += [float(b)/total, float(g)/total, float(r)/total]
    #H3
    b = B[int(height/2)+1:height, 0:int(width/2)].sum()
    g = G[int(height/2)+1:height, 0:int(width/2)].sum()
    r = R[int(height/2)+1:height, 0:int(width/2)].sum()
    total = b + g + r
    vec += [float(b)/total, float(g)/total, float(r)/total]
    #H4
    b = B[int(height/2)+1:height, int(width/2)+1:width].sum()
    g = G[int(height/2)+1:height, int(width/2)+1:width].sum()
    r = R[int(height/2)+1:height, int(width/2)+1:width].sum()
    total = b + g + r
    vec += [float(b)/total, float(g)/total, float(r)/total]
    return vec


#量化P 到　0,1,2
def quantization(p, high, low):
    q = [0]*len(p)
    for i in range(len(p)):
        if p[i] > high:
            q[i] = 2
        elif p[i] > low:
            q[i] = 1
        else:
            q[i] = 0
    return q

#投影到Hamming空间
def cast_to_hamming(p, cast_set):
    res = ""
    for num in cast_set:
        #求出对应p集合第xi个元素
        xi = int(round(float(num)/2.0) - 1)
        #如果为０，则必然投影为０
        if(p[xi] == 0):
            res += "0"
        #如果为２，则必然投影为１
        elif(p[xi] == 2):
            res += "1"
        #如果为１
        else:
            res += str((num-2*xi)%2)
    return res


#参数：目标图片， 数据文件夹， 最多输出k个数据(在同一桶中前k近的)
def LSH(file_name, file_path, k=5):
    cast_set = [2,7,10,15]
    #储存HASH类（桶）　键值对:　投射到汉明空间的值-[[文件名,特征向量],...]
    search_set = {}

    file_set = os.listdir(file_path)
    for file in file_set:
        pic = cv2.imread(file_path+"/"+file, cv2.IMREAD_COLOR)
        vec = get_vector(pic)
        p = get_cast(vec, cast_set)
        if(search_set.has_key(p)):
            search_set[p].append([file, vec])
        else:
            search_set[p] = [[file,vec]]

    start = time.time()
    #获得要检索图片的HASH
    target = cv2.imread(file_name, cv2.IMREAD_COLOR)
    target_vec = get_vector(target)
    target_p = get_cast(target_vec, cast_set)

    #检索并输出结果
    #没有找到
    if(not search_set.has_key(target_p)):
        print "Sorry, there are no similar pictures by LSH"
        return
    else:
        print "Find Result(by LSH):"
        print "Filename\tCosine Similarity"
        print "cost", time.time()-start,"s"
        #储存桶内图片与目标图片的余弦相似度
        allsimilarity = []
        for ele in search_set[target_p]:
            allsimilarity.append((ele[0], get_cos(target_vec, ele[1])))
        #排序
        allsimilarity.sort(key=lambda x:x[1], reverse=True)
        #只输出前k大
        for i in range(min(len(allsimilarity), k)):
            print i+1,"\t",allsimilarity[i][0],"\t",allsimilarity[i][1]
        print
    

#计算两个特征向量的余弦相似度
def get_cos(x,y):
    x = np.array(x, dtype='float32') 
    y = np.array(y, dtype='float32')
    res = (x.dot(y.T)) / (np.linalg.norm(x) * np.linalg.norm(y))
    #归一化
    res = 0.5 + res*0.5
    return res


#参数：目标图片， 数据文件夹， 最多输出k个数据（前k相似）
def NN(file_name, file_path, k=5):
    start = time.time()
    target = cv2.imread(file_name, cv2.IMREAD_COLOR)
    target_vec = get_vector(target)

    #储存所有图片与目标图片的余弦相似度
    allsimilarity = []
    file_set = os.listdir(file_path)
    for file in file_set:
        pic = cv2.imread(file_path+"/"+file, cv2.IMREAD_COLOR)
        vec = get_vector(pic)
        allsimilarity.append((file, get_cos(vec, target_vec)))
    #排序
    allsimilarity.sort(key=lambda x:x[1], reverse=True)
    #只输出前k大
    print "Find Result(by NN):"
    print "Filename\tCosine Similarity"
    print "cost", time.time()-start,"s"
    for i in range(min(len(allsimilarity), k)):
        print i+1,"\t",allsimilarity[i][0],"\t",allsimilarity[i][1]




def main():
    LSH("target.jpg", "dataset", 10)
    NN("target.jpg", "dataset", 10)


main()
