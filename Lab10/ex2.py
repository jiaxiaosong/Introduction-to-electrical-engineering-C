import cv2
import numpy as np
from matplotlib import pyplot as plt
from math import *


def gray_hist(filename):
    img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
    hist = cv2.calcHist([img], [0], None, [256], [0, 256]).flatten()
    total = hist.sum()
    hist /= total

    # draw the histogram
    x = np.linspace(0, 255, num=256)
    plt.bar(x, hist, align="center")
    plt.title('Grey Scale Histogram of ' + filename)
    plt.xlim(0, 256)
    plt.ylabel("Ratio")
    plt.xlabel("Grayscale")
    plt.show()


# implement by easy thought
def my_gray_grad_hist(filename):
    img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
    height, width = img.shape
    # store the gray gradient magnitude
    res = np.zeros(361)
    #calculate the ray gradient magnitude
    for i in range(1, height-1):
        for j in range(1, width-1):
            gx = int(img[i][j+1]) - int(img[i][j-1])
            gy = int(img[i+1][j]) - int(img[i-1][j])
            res[int(sqrt(gx*gx+gy*gy))] += 1
    total = res.sum()
    res /= total

    # draw the histogram
    x = np.linspace(0, 360, num=361)
    plt.bar(x, res, align="center")
    plt.title('Grey Scale Gradient Histogram of ' + filename)
    plt.xlim(0, 360)
    plt.ylim(0, 0.1)
    plt.ylabel("Pixels")
    plt.xlabel("Gray Scale Gradient")
    plt.show()


# implement by matrix operator
def matrix_gray_grad_hist(filename):
    img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
    height, width = img.shape
    # matrix operator
    mx = np.array([[-1, 0, 1]])
    my = np.array([[-1, 0, 1]]).T
    # get the gradient through the api filter2D
    gx = cv2.filter2D(img, cv2.CV_32F, mx)
    gy = cv2.filter2D(img, cv2.CV_32F, my)
    # store the gray gradient magnitude
    res = np.zeros(361)
    #calculate the ray gradient magnitude
    for i in range(1, height-1):
        for j in range(1, width-1):
            res[int(sqrt(gx[i][j]*gx[i][j]+gy[i][j]*gy[i][j]))] += 1
    total = res.sum()
    res /= total

    # draw the histogram
    x = np.linspace(0, 360, num=361)
    plt.bar(x, res, align="center")
    plt.title('Grey Scale Gradient Histogram of ' + filename)
    plt.xlim(0, 360)
    plt.ylim(0, 0.1)
    plt.ylabel("Ratio")
    plt.xlabel("Gray Scale Gradient")
    plt.show()


gray_hist("green.jpg")
matrix_gray_grad_hist("green.jpg")
my_gray_grad_hist("green.jpg")
