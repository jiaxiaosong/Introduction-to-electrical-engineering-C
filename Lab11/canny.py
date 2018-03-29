#!/usr/bin/env python
# -*- coding=utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import cv2
import numpy as np
from math import *
from matplotlib import pyplot as plt


def canny_operator(img):
    mx = np.array([[-1, 1], [-1, 1]])
    my = np.array([[1, 1], [-1, -1]])
    dx = cv2.filter2D(img, cv2.CV_32F, mx, anchor=(0, 0))/2
    dy = cv2.filter2D(img, cv2.CV_32F, my, anchor=(0, 0))/2
    res = np.sqrt(dx*dx+dy*dy)
    return res

# my final gradient algorithm
def scharr(img):
    dx = cv2.Sobel(img, cv2.CV_32F, 1, 0, ksize=-1)/16
    dy = cv2.Sobel(img, cv2.CV_32F, 0, 1, ksize=-1)/16
    amp = np.sqrt(dx*dx+dy*dy)
    # calculate the angle of the gradient
    angles = np.zeros(img.shape)
    for i in range(1, img.shape[0]-1):
        for j in range(1, img.shape[1]-1):
            if(dx[i][j] == 0):
                angles[i][j] = np.sign(dy[i][j])*pi/2.0
            else:
                angles[i][j] = atan(dy[i][j]/dx[i][j])
    return amp, angles


def non_maxm_suppression(grad, angles):
    res = np.zeros(grad.shape)
    for y in range(1, grad.shape[0]-1):
        for x in range(1, grad.shape[1]-1):
            if(grad[y][x] == 0):
                continue
            angle = angles[y][x]
            if(abs(angle) > pi/4):
                if(angle == 0):
                    weight = 1
                else:
                    weight = 1/abs(tan(angle))
                if(angle > 0):
                    dtmp1 = (1-weight) * grad[y+1][x] + weight * grad[y+1][x+1]
                    dtmp2 = (1-weight) * grad[y-1][x] + weight * grad[y-1][x-1]
                else:
                    dtmp1 = (1-weight) * grad[y-1][x] + weight * grad[y-1][x+1]
                    dtmp2 = (1-weight) * grad[y+1][x] + weight * grad[y+1][x-1]
            else:
                weight = abs(tan(angle))
                if(angle > 0):
                    dtmp1 = (1-weight) * grad[y][x+1] + weight * grad[y+1][x+1]
                    dtmp2 = (1-weight) * grad[y][x-1] + weight * grad[y-1][x-1]
                else:
                    dtmp1 = (1-weight) * grad[y][x+1] + weight * grad[y-1][x+1]
                    dtmp2 = (1-weight) * grad[y][x-1] + weight * grad[y+1][x-1]

            if(grad[y][x] > dtmp1 and grad[y][x] > dtmp2):
                res[y][x] = grad[y][x]
    return res


def get_high_threshold(grad, weight):
    maxm = int(np.max(grad))
    hist, bins = np.histogram(grad.ravel(), maxm+1, [0, maxm+1])
    cnt = 0
    threshold = float(grad.size-hist[0]) * weight
    for i in range(1, hist.size):
        cnt += hist[i]
        if(cnt > threshold):
            return i


def edge_linking(grad, high, low):
    res = np.zeros(grad.shape)
    y_stack = []
    x_stack = []
    # strong edge
    for i in range(1, grad.shape[0]-1):
        for j in range(1, grad.shape[1]-1):
            if(grad[i][j] > high):
                res[i][j] = 255
                y_stack.append(i)
                x_stack.append(j)

    # weak edge
    while(len(y_stack) != 0):
        y = y_stack.pop()
        x = x_stack.pop()
        res[y][x] = 255
        # right
        if(grad[y][x+1] > low and res[y][x+1] < 255):
            y_stack.append(y)
            x_stack.append(x+1)
            res[y][x+1] = 255
        # up right
        if(grad[y+1][x+1] > low and res[y+1][x+1] < 255):
            y_stack.append(y+1)
            x_stack.append(x+1)
            res[y+1][x+1] = 255
        # up
        if(grad[y+1][x] > low and res[y+1][x] < 255):
            y_stack.append(y+1)
            x_stack.append(x)
            res[y+1][x] = 255
        # up left
        if(grad[y+1][x-1] > low and res[y+1][x-1] < 255):
            y_stack.append(y+1)
            x_stack.append(x-1)
            res[y+1][x-1] = 255
        # left
        if(grad[y][x-1] > low and res[y][x-1] < 255):
            y_stack.append(y)
            x_stack.append(x-1)
            res[y][x-1] = 255
        # down left
        if(grad[y-1][x-1] > low and res[y-1][x-1] < 255):
            y_stack.append(y-1)
            x_stack.append(x-1)
            res[y-1][x-1] = 255
        # down
        if(grad[y-1][x] > low and res[y-1][x] < 255):
            y_stack.append(y-1)
            x_stack.append(x)
            res[y-1][x] = 255
        # down right
        if(grad[y-1][x+1] > low and res[y-1][x+1] < 255):
            y_stack.append(y-1)
            x_stack.append(x+1)
            res[y-1][x+1] = 255
    return res


def canny(filename):
    # 1 get the gray scale
    img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)

    # 2 smooth filter
    #img = cv2.GaussianBlur(img, (3,3), 1.5)
    img_smoothed = cv2.adaptiveBilateralFilter(img, (3, 3), 75)

    # 3 get the gradient
    #grad = canny_operator(img)
    grad, angles = scharr(img_smoothed)

    # 4 Non-Maximum Suppression
    suppress = non_maxm_suppression(grad, angles)

    # 5 fuzzy thresholds algrithm and edge linking
    high = get_high_threshold(suppress, 0.7)
    low = round(high*0.4)
    img_edge = edge_linking(suppress, high, low)

    opencv_canny = cv2.Canny(img, 50, 150)
    plt.subplot(131), plt.imshow(
        img, cmap=plt.cm.gray), plt.title("Origin Picture")
    plt.subplot(132), plt.imshow(
        img_edge, cmap=plt.cm.gray), plt.title("My Canny")
    plt.subplot(133), plt.imshow(
        opencv_canny, cmap=plt.cm.gray), plt.title("Opencv's Canny")
    plt.show()

canny("1.jpg")
