# -*- coding:utf-8 -*-
import urllib2, cookielib, urllib
from bs4 import BeautifulSoup

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def bbs_set(id, pw, text):
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
    postdata = urllib.urlencode({'id':id, 'pw': pw, 'submit':'login'})
    req = urllib2.Request(url = 'https://bbs.sjtu.edu.cn/bbslogin', data = postdata)
    response = urllib2.urlopen(req)

    postdata2 =  urllib.urlencode({'type':'update', 'text':text})
    req2 = urllib2.Request(url = 'https://bbs.sjtu.edu.cn/bbsplan', data = postdata2)
    response2 = urllib2.urlopen(req2).read()
    
    content = urllib2.urlopen('https://bbs.sjtu.edu.cn/bbsplan')
    soup = BeautifulSoup(content)
    print str(soup.find('textarea').string).strip().decode('utf8')

if __name__ == '__main__':
	
    id = sys.argv[1]
    pw = sys.argv[2]
    text = sys.argv[3].decode('utf-8').encode('gbk')

    bbs_set(id, pw, text)
