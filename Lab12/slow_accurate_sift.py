#!/usr/bin/env python
# -*- coding=utf-8 -*-
#实验拓展——Lowe

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import cv2
import numpy as np
from math import *
from matplotlib import pyplot as plt


# 1 用Harris角点近似关键点
def get_KeyPoints(img):
    tmp = cv2.goodFeaturesToTrack(
        img, maxCorners=1000, qualityLevel=0.01, minDistance=10, blockSize=3, k=0.04)
    KeyPoints = []
    for p in tmp:
        KeyPoints.append([p[0][1], p[0][0]])
    return KeyPoints


# 2 判断该关键点周围是否足够大（不在边界）:
def isValid(height, width, y, x):
    return ((y > 12) and (y < height-12) and (x > 12) and (x < width-12))


#高斯函数
def Gauessian(y, x, sigma):
    return exp(-(y*y+x*x)/(2*sigma*sigma))

# 3 求关键点主方向
def get_MainDir(img, y, x):
    y = int(y)
    x = int(x)
    dir_hist = [0]*36
    for i in range(-8, 9):
        for j in range(-8, 9):
            dx = img[y+i][x+j+1] - img[y+i][x+j-1]
            dy = img[y+i+1][x+j] - img[y+i-1][x+j]
            # 梯度幅值
            magnitude = sqrt(dx*dx+dy*dy)*Gauessian(i, j, 2.6)
            # 梯度方向0~360
            sita = np.arctan2(dy, dx)*180/pi+180
            if(sita >= 360):
                sita -= 360
            dir_hist[int(sita/10)] += magnitude

    dir_hist = smooth_hist(dir_hist)
    max_index = 0
    for i in range(0, 35):
        if(dir_hist[i] > dir_hist[max_index]):
            max_index = i

    res = [(max_index*10+5)*pi/180]
    for i in range(0,35):
        if(i == max_index or dir_hist[i] < dir_hist[max_index]*0.8):
            continue
        res.append((i*10+5)*pi/180)
    return res


#直方图平滑
def smooth_hist(hist):
    for i in range(2):
        res = [0]*36
        res[0] = 0.25*hist[35] + 0.5*hist[0] + 0.25*hist[1]
        res[35] = 0.25*hist[34] + 0.5*hist[35] + 0.25*hist[0]
        for j in range(1,35):
            res[j] = 0.25*hist[j-1] + 0.5*hist[j] + 0.25*hist[j+1]
        hist = res
    return hist
            

#得到该点的的灰度梯度方向
def get_dir(img, y, x):
    return np.arctan2(img[y+1][x]-img[y-1][x], img[y][x+1]-img[y][x-1])+pi

#得到该点的灰度梯度值
def get_mag(img, y, x):
    return sqrt((img[y+1][x]-img[y-1][x])**2+(img[y][x+1]-img[y][x-1])**2)

# 双线性插值
def insert_value(img, main_dir,y, x):
    x0 = int(x)
    y0 = int(y)
    sita = get_dir(img, y0+1, x0)*(y-y0)*(x0+1-x) + get_dir(img, y0, x0)*(y0+1-y)*(x0+1-x) + \
                   get_dir(img, y0, x0+1)*(y0+1-y)*(x-x0) + get_dir(img, y0+1, x0+1)*(y-y0)*(x-x0) - main_dir
    magnitude = get_mag(img, y0+1, x0)*(y-y0)*(x0+1-x) + get_mag(img, y0, x0)*(y0+1-y)*(x0+1-x) + \
                   get_mag(img, y0, x0+1)*(y0+1-y)*(x-x0) + get_mag(img, y0+1, x0+1)*(y-y0)*(x-x0)
    while(sita < 0):
        sita += 2*pi
    return sita,magnitude


#传入关键点及其主方向，求出128维特征向量
def get_descriptor(img, main_dir, y, x):
    cos_main = cos(main_dir)
    sin_main = sin(main_dir)
    descriptor = []
    for row in range(4):
        for column in range(4):
                subdescriptor = [0]*8
                for i in range(4):
                    for j in range(4):
                        # 计算旋转后采样点坐标
                        xp = cos_main*(column*4-8+j) - sin_main*(row*4-8+i) + x
                        yp = sin_main*(column*4-8+j) + cos_main*(row*4-8+i) + y

                        # 双线性插值
                        sita,magnitude = insert_value(img, main_dir, yp, xp)
                        sita = sita * 180/pi
                        if(sita>=360):
                            sita -= 360
                        #加高斯门限值0.2
                        subdescriptor[int(sita/45)] += min(magnitude*Gauessian(yp-y, xp-x, 2), 0.2)
                descriptor.extend(subdescriptor)
    descriptor = np.array(descriptor, dtype='float32')
    #归一化
    total = np.sum(descriptor**2)**0.5
    if(total == 0):
        return descriptor
    descriptor = descriptor / total
    return descriptor



#获得给定图片所有的128维特征向量
def get_descriptor_set(ori_img):
    descriptor_set = []
    scale = 1.0
    height, width = ori_img.shape
    #获得在高斯金字塔各层下的特征向量
    while(height*scale > 100 and width*scale > 100):
        img = cv2.resize(ori_img, (int(scale*width), int(scale*height)), interpolation=cv2.INTER_AREA)
        # 1 用Harris角点近似关键点
        KeyPoints=get_KeyPoints(img)
        for KeyPoint in KeyPoints:
            y, x=KeyPoint
            # 2 判断该关键点周围是否足够大（不在边界）:
            if(not isValid(int(height*scale), int(width*scale), y, x)):
                continue

            # 3 求关键点主方向及辅方向
            main_dir=get_MainDir(img, y, x)

            # 4 生成描述子
            for dire in main_dir:
                descriptor=get_descriptor(img, dire, y, x)
                descriptor_set.append([descriptor, [y/scale,x/scale]])
        scale /= 2.0
    return descriptor_set


#得到两组特征向量 进行匹配连线
def draw_matches(img1, img2, des1, des2, ratio):
    rows1 = img1.shape[0]
    cols1 = img1.shape[1]
    rows2 = img2.shape[0]
    cols2 = img2.shape[1]

    res = np.zeros((max([rows1,rows2]),cols1+cols2,3), dtype='uint8')
    res[:rows1,:cols1] = np.dstack([img1, img1, img1])
    res[:rows2,cols1:] = np.dstack([img2, img2, img2])

    #求出每两个特征向量的欧式距离
    for i in range(len(des1)):
        minm = 10000
        second_minm = 10000
        minm_index = -1
        #找出与图１第i个关键点欧氏距离最近和次近的两个图二中关键点
        for j in range(len(des2)):
            distance = np.linalg.norm(des1[i][0] - des2[j][0])
            if(distance < minm):
                second_minm = minm
                minm = distance
                minm_index = j
            if(minm < distance and distance < second_minm):
                second_minm = distance

        #如果最小值和次小值比例小于ratio则认为二者匹配
        if(minm/second_minm < ratio):        
            #在关键点出画园，　将两点连线
            y1,x1 = des1[i][1]
            y2,x2 = des2[minm_index][1]
            a = np.random.randint(0,256)
            b = np.random.randint(0,256)
            c = np.random.randint(0,256)

            cv2.circle(res, (int(np.round(x1)),int(np.round(y1))), 2, (a, b, c), 1)
            cv2.circle(res, (int(np.round(x2)+cols1),int(np.round(y2))), 2, (a, b, c), 1)
            cv2.line(res, (int(np.round(x1)),int(np.round(y1))), (int(np.round(x2)+cols1),int(np.round(y2))), (a, b, c), 
                1, lineType=cv2.CV_AA, shift=0)
    cv2.imshow('Result', res)  
    cv2.waitKey(0)


def main():
    img1 = np.float32(cv2.imread('target.jpg', cv2.IMREAD_GRAYSCALE))
    des1 = get_descriptor_set(img1)

    img2 = np.float32(cv2.imread('3.jpg', cv2.IMREAD_GRAYSCALE))
    des2 = get_descriptor_set(img2)

    draw_matches(img1, img2, des1, des2, 0.8)

main()
