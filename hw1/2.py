# encoding = utf8
import urllib2
from BeautifulSoup import BeautifulSoup
import re
import sys,os



def parseIMG(content):
	imgset = set()
	soup = BeautifulSoup(content)
	f = open("res2.txt",'w+')
	res = ""
	for i in soup.findAll('img'):
		tmp = str(i.get('src',' '))
		if(tmp != ' '):
			if(tmp[:2] == "//" ):
				tmp = "http:"+tmp
			elif(tmp[:1] == '/' and len(tmp)>=3):
				tmp = "http:/"+tmp
			elif(tmp[0] == 'w' and len(tmp)>=3):
				tmp = "http://" + tmp
			if(tmp[0] == 'h'):
				res += (tmp + "\n");
				imgset.add(tmp)
		f.write(res)
	f.close();
	return imgset


#test
#content = urllib2.urlopen('http://www.baidu.com')
#parseIMG(content)

url = sys.argv[1]
content = urllib2.urlopen(url).read()
parseIMG(content)
