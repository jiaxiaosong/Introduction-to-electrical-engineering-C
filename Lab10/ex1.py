import cv2
import numpy as np
from matplotlib import pyplot as plt

# calculate by numpy


def RGB_hist(filename):
    img = cv2.imread(filename, cv2.IMREAD_COLOR)
    B, G, R = cv2.split(img)
    B = B.sum()
    G = G.sum()
    R = R.sum()
    total = float(R+G+B)
    R = R/total
    G = G/total
    B = B/total

    draw_RGB(R, G, B, filename)


# draw the picture by matplotlib
def draw_RGB(R, G, B, filename):
    # three column
    fig = plt.figure(3)
    rects = plt.bar(left=(0.1, 0.2, 0.3), height=(R, G, B), color=(
        'r', 'g', 'b'), width=0.1, align='center', yerr=0.000001)
    # set the text
    for rect in rects:
        plt.text(rect.get_x()+rect.get_width()/2, 1.03 *
                 rect.get_height(), '%s' % rect.get_height())
    plt.xticks((0.1, 0.2, 0.3), ('R', 'G', 'B'))
    plt.title('RGB Histogram of ' + filename)
    plt.ylabel("Ratio")

    plt.ylim(0, 1.0)
    plt.xlim(0, 0.4)
    plt.show()


RGB_hist("red.jpg")
