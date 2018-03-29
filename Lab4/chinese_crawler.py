
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
import jieba


reload(sys)
sys.setdefaultencoding("utf-8")


def find_coding(content):
    start = content.find('charset=')+8
    if('gb' in content[start:start+8].lower()):
        decoding = 'GBK'
    else:
        decoding = 'utf-8'
    return decoding

title_reg = re.compile(r"<title>([\s\S]*?)</title>")
# find the title of the page
def find_title(content):
    global title_reg
    res = title_reg.search(content.lower())
    if(res is None):
        return "No Title"
    return res.group(1).replace("\n", " ")


def clean_html(html):
    # First we remove inline JavaScript/CSS:
    cleaned = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", html.strip())
    # Then we remove html comments. This has to be done before removing regular
    # tags since comments can contain '>' characters.
    cleaned = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleaned)
    # Next we can remove the remaining tags:
    cleaned = re.sub(r"(?s)<.*?>", " ", cleaned)
    # Finally, we deal with whitespace
    cleaned = re.sub(r"&nbsp;", " ", cleaned)
    cleaned = re.sub(r"  ", " ", cleaned)
    cleaned = re.sub(r"  ", " ", cleaned)
    return cleaned.strip()


def valid_filename(s):
    import string
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    s = ''.join(c for c in s if c in valid_chars)
    return s


def get_page(page):
    content = ''
    try:
        content = urllib2.urlopen(page, timeout=2).read()
        # print content
    except:
        return None
    return content

link_reg = re.compile(r'a href=\"(.+?)\"')
def get_all_links(content, page):
    global link_reg
    tmp = set()
    for url in link_reg.findall(str(content)):
        if(url[0] == 'j' or len(url) < 6):
            continue
        if(url[-3:] == 'exe' or url[-3:] == 'apk' or url[-3:] == 'pdf'):
            continue
        if(url[0] == '/'):
            url = urlparse.urljoin(page, url)
        if(url[-1] == '/'):
            url = url[:-1]
        if(url[0:4] == 'http'):
            tmp.add(url)
    links = list(tmp)
    return links


def add_page_to_folder(page, content, title):
    global index_file
    folder = 'html'  # 存放网页的文件夹
    filename = valid_filename(page)  # 将网址变成合法的文件名
    index_file.write(filename + '\t' + page + '\t' + title + '\n')
    if not os.path.exists(folder):  # 如果文件夹不存在则新建
        os.mkdir(folder)
    f = open(os.path.join(folder, filename), 'w')
    f.write(content.encode('utf-8', 'ignore'))  # 将网页存入文件
    f.close()


def working():
    global q, crawled, count, max_page
    while True:
        page = q.get()
        if not crawled.check(page):
            content = get_page(page)
            # fail to read the page
            if(content is None):
                crawled.set(page)
                continue
            try:
                # change the content to utf-8
                decoding = find_coding(content)
                content = content.encode(decoding, 'ignore')
                outlinks = get_all_links(content, page)
                title = find_title(content)
                print title
                content = clean_html(content)
                # jieba.enable_parallel(4)
                content = " ".join(jieba.cut_for_search(
                    content, HMM=True)).replace("\n", "")
                # print content
                add_page_to_folder(page, content, title)
            except:
                continue

            count += 1
            if varLock.acquire():
                print page
                for url in outlinks:
                    q.put(url)
                crawled.set(page)
                varLock.release()

            if(max_page < count):
                return


index_filename = 'indexfile.txt'
index_file = open(index_filename, 'a')

start = time.time()
seed = "https://baike.baidu.com/item/%E4%B8%AD%E5%9B%BD/1122445?fr=aladdin"
q = Queue.Queue()
q.put(seed)
count = 0
max_page = 1000
crawled = bloomfilter.BloomFilter(20*max_page, 5)

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


index_file.close()
print "It uses", time.time()-start, "sec to parse", max_page, "pages with", THREAD_NUM, "threads."
