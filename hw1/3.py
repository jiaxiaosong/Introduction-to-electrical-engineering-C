# coding = utf8
from BeautifulSoup import BeautifulSoup
import urllib2
import re
import sys, os
import urlparse

reload(sys)
sys.setdefaultencoding('utf-8')

def parseQiushibaikePic(content):
	docs = {};
	res = ''
	f = open("res3.txt","w+")
	soup = BeautifulSoup(content)
	for qiu_pic in soup.findAll('div', {'id':re.compile('^qiushi_tag_\d+')}):
		qiushi_tag = str(qiu_pic.get('id',' ')[11:])
		sentence = str(qiu_pic.find('div',{'class':'content'}).span.text)
		pic =  'http:'+str(qiu_pic.find('div',{"class":"thumb"}).find('a').find('img').get('src',' '))
		docs[qiushi_tag] = {"content":sentence, "imgurl":pic}
		res += (pic + '\t' + sentence + '\n')
	url = "https://www.qiushibaike.com/pic"
	nextpage = urlparse.urljoin(url , soup.find('span', {'class':'next'}).parent.get('href', ' '))
	f.write(res)
	f.close()
	return docs,nextpage

'''test
def main():
	req = urllib2.Request("https://www.qiushibaike.com/pic", None, {'User-agent':'Custom User Agent'})
	content = urllib2.urlopen(req)
	parseQiushibaikePic(content)
'''

url = sys.argv[1]
req = urllib2.Request(url, None, {'User-agent':'Custom User Agent'})
content = urllib2.urlopen(req).read()
str(parseQiushibaikePic(content)).decode('string_escape')
