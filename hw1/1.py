# encoding = utf8
import urllib2
from BeautifulSoup import BeautifulSoup
import re
import sys, os



def parseURL(content):
	urlset = set()
	soup = BeautifulSoup(content)
	f = open("res1.txt",'w+')
	res = "";
	for i in soup.findAll('a'):
		tmp = str(i.get('href',' '))
		if(tmp != ' '): #make all url begin with http://
			if(tmp[:2] == "//" ):
				tmp = "http:"+tmp
			elif(tmp[:1] == '/' and len(tmp)>=3):
				tmp = "http:/"+tmp
			elif(tmp[0] == 'w' and len(tmp)>=3):
				tmp = "http://" + tmp
			if(tmp[0] == 'h'):
				res += (tmp + "\n");
				urlset.add(tmp)
		f.write(res)
	f.close();
	return urlset

#test
#content = urllib2.urlopen('http://www.baidu.com')
#parseURL(content)

url = sys.argv[1]
content = urllib2.urlopen(url).read()
parseURL(content)



