
# -*- coding:utf-8 -*-
import time
import Queue
import threading
import urllib2
import re
import urlparse
import os
import urllib
import sys

import random
import jieba


reload(sys)
sys.setdefaultencoding("utf-8")


title_reg = re.compile(r"<title>([\s\S]*?)</title>")
# find the title of the page


def get_crawl_list(max_page):
    temp = range(200000, 5000000)
    random.shuffle(temp)
    return temp


def get_page(page):
    content = ''
    try:
        content = urllib2.urlopen(page, timeout=2).read()
        # print content
    except:
        return None
    return content


def get_pic(content, page):
    index1 = content.find("data-origin=")+13
    index2 = content.find("\"", index1)
    pic_url = content[index1:index2]
    index1 = content.find("alt=\"", index2)+5
    index2 = content.find("\"", index1)
    title = content[index1:index2]
    return pic_url, title


def working():
    global q, count, max_page, pic_info, crawl_list, crawl_times
    while True:
        number = crawl_list[crawl_times]
        page = "https://item.jd.com/" + str(number) + ".html"
        crawl_times += 1
        content = get_page(page)
        # fail to read the page
        if(content is None):
            continue
        try:
            print page
            content = content.decode('GBK', 'ignore')
            pic_url, title = get_pic(content, page)
            #不存在该页面跳转回京东首页，首字母m
            if(pic_url[0] == 'm'):
                continue
            title = " ".join(jieba.cut_for_search(title, HMM=True)).replace("\n", "")
            pic_info.write(page + " " + pic_url + " " + title + '\n')
            count += 1
        except:
            continue
        if(max_page < count):
            return


pic_filename = 'pic_info.txt'
pic_info = open(pic_filename, 'a')


start = time.time()
count = 0
max_page = 1000
crawl_list = get_crawl_list(max_page)
crawl_times = 0


THREAD_NUM = 100
threads = []
varLock = threading.Lock()

for i in range(THREAD_NUM):
    t = threading.Thread(target=working)
    t.setDaemon(True)
    threads.append(t)
    t.start()
for t in threads:
    t.join()


pic_info.close()
print "It uses", time.time()-start, "sec to parse", max_page, "pages with", THREAD_NUM, "threads."
