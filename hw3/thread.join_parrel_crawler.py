
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
import bloomfilter

reload(sys)
sys.setdefaultencoding("utf-8")

def valid_filename(s):
    import string
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    s = ''.join(c for c in s if c in valid_chars)
    return s

def get_page(page):
    content = ''
    try:
        content = urllib2.urlopen(page, timeout = 1).read()
    except:
        return None
    return content

def get_all_links(content, page):
    tmp = set()
    for url in re.compile(r'a href=\"(.+?)\"').findall(content):
        if(url[0]=='j' or len(url)<6):
            continue
        if(url[0] == '/'):
            url = urlparse.urljoin(page, url)
        if(url[-1] == '/'):
            url = url[:-1]
        if(url[0:4] == 'http'):
            tmp.add(url)
    links = list(tmp)
    return links

def add_page_to_folder(page, content): #将网页存到文件夹里，将网址和对应的文件名写入index.txt中
    index_filename = 'index.txt'    #index.txt中每行是'网址 对应的文件名'
    folder = 'html'                 #存放网页的文件夹
    filename = valid_filename(page) #将网址变成合法的文件名
    index = open(index_filename, 'a')
    index.write(page.encode('ascii', 'ignore') + '\t' + filename + '\n')
    index.close()
    if not os.path.exists(folder):  #如果文件夹不存在则新建
        os.mkdir(folder)
    f = open(os.path.join(folder, filename), 'w')
    f.write(content)                #将网页存入文件
    f.close()

def working():
    global q, crawled, count, max_page
    while True:
        page = q.get()
        if not crawled.check(page):
            content = get_page(page)

            #fail to read the page
            if(content == None):
                crawled.set(page)
                continue

            add_page_to_folder(page, content)
            outlinks = get_all_links(content, page)
            count += 1
            if varLock.acquire():
                print page
                for url in outlinks:
                   q.put(url)
                crawled.set(page)
                varLock.release()

            if(max_page < count):
            	return



start = time.time()
seed = "http://www.baidu.com"
q = Queue.Queue()
q.put(seed)
count = 0
max_page = 20
crawled = bloomfilter.BloomFilter(20*max_page, 5)

THREAD_NUM = 10
threads = []
varLock = threading.Lock()
for i in range(THREAD_NUM):
    t = threading.Thread(target = working)
    t.setDaemon(True)
    threads.append(t)
    t.start()
for t in threads:
	t.join()

print "It uses", time.time()-start,"sec to parse", max_page,"pages with", THREAD_NUM, "threads."
