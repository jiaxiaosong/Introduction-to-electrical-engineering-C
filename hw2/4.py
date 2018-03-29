# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
import urllib2
import re
import urlparse
import os
import urllib
import sys

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
        content = urllib2.urlopen(page, timeout = 5).read()
    except Exception, e:
        print "Open Url Error"
        return None
    return content

def get_all_links(content, page):
    links = []
    tmp = set()
    soup = BeautifulSoup(content)
    for goal in soup.findAll('a',{'href':re.compile('^http|^/')}):
        url = goal.get('href')
        if(url[0]=='j' or len(url)<6):
            continue
        if(url[0] == '/'):
            url = urlparse.urljoin(page, url)
        if(url[-1] == '/'):
            url = url[:-1]
        if(url[0] == 'h'):
            tmp.add(url)
    links = list(tmp)
    return links
        
def union_dfs(a,b):
    for e in b:
        if e not in a:
            a.append(e)
            
def union_bfs(a,b):
        for e in b:
            if e not in a:
                a.insert(0,e)
       
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
    
def crawl(seed, method, max_page):
    tocrawl = [seed]
    crawled = []
    graph = {}
    count = 0
    max_page = int(max_page)
    while tocrawl:
        page = tocrawl.pop()
        if page not in crawled:
            crawled.append(page)
            content = get_page(page)
            if(content == None):  #不再爬取该网页
                continue
            count += 1
            add_page_to_folder(page, content)
            outlinks = get_all_links(content, page)
            graph[page] = outlinks
            globals()['union_%s' % method](tocrawl, outlinks)
            print page
            if(count == max_page):
                break
    return graph, crawled

if __name__ == '__main__':
    seed = sys.argv[1]
    method = sys.argv[2]
    max_page = sys.argv[3]
    graph, crawled = crawl(seed, method, max_page)

