import web
import re
import jieba
from web import form
import os
import sys
from bs4 import BeautifulSoup
import lucene
import envir
import urllib
import urllib2
from java.io import File
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.util import Version
from org.apache.lucene.search import BooleanQuery
from org.apache.lucene.search import BooleanClause
from org.apache.lucene.search.highlight import SimpleHTMLFormatter, Highlighter, QueryScorer, SimpleFragmenter, TokenSources

"""
This script is loosely based on the Lucene (java implementation) demo class
org.apache.lucene.demo.SearchFiles.  It will prompt for a search query, then it
will search the Lucene index in the current directory called 'index' for the
search query entered against the 'contents' field.  It will then display the
'path' and 'name' fields for each of the hits it finds in the index.  Note that
search.close() is currently commented out because it causes a stack overflow in
some cases.
"""
reload(sys)
sys.setdefaultencoding('utf-8')

INDEX_DIR = "IndexFiles.index"


# get the recommand words from the given words by baidu suggestion api
def get_recommand(word):
    User_Agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36'
    url = "https://www.baidu.com/s?wd="
    word = urllib.quote(word.encode('utf-8', 'ignore'))
    url += word
    req = urllib2.Request(url)
    req.add_header("User-Agent", User_Agent)
    content = urllib2.urlopen(req)
    soup = BeautifulSoup(content, 'html.parser')
    goal = soup.find('div', {'id': 'rs'})
    res = goal.get_text(" ").split(" ")
    return res[1:]


def parseCommand(command, opt):
    allowed_opt = ["site"]
    command_dict = {}
    for i in command.split(' '):
        if ':' in i:
            opt, value = i.split(':')[:2]
            opt = opt.lower()
            if opt in allowed_opt and value != '':
                command_dict[opt] = command_dict.get(opt, '') + ' ' + value
        else:
            command_dict[opt] = command_dict.get(opt, '') + ' ' + i
    return command_dict


urls = (
    '/', 'index',
    '/searching', 'searching'
)


render = web.template.render('templates')  # your templates


class index:

    def GET(self):
        return render.index()


def text_search(command):
    envir.vm_env.attachCurrentThread()
    command_dict = parseCommand(command, "contents")
    querys = BooleanQuery()
    for k, v in command_dict.iteritems():
        query = QueryParser(Version.LUCENE_CURRENT, k,
                            envir.analyzer).parse(v)
        querys.add(query, BooleanClause.Occur.MUST)

    scoreDocs = envir.text_searcher.search(querys, 30).scoreDocs
    res = []

    query_highlight = QueryParser(Version.LUCENE_CURRENT, k,
                                  envir.analyzer).parse(command_dict["contents"])
    myhighlighter = Highlighter(
        SimpleHTMLFormatter(), QueryScorer(query_highlight))
    myhighlighter.setTextFragmenter(SimpleFragmenter(50))
    for scoreDoc in scoreDocs:
        # find texts which are around the keyword
        doc = envir.text_searcher.doc(scoreDoc.doc)
        text = doc.get("contents")
        key_text = "".join((myhighlighter.getBestFragments(
            envir.analyzer, "contents", text, 3)))
        key_text = re.sub('\s', '', key_text)
        temp = [doc.get("title"), doc.get('url'), key_text]
        res.append(temp)
    return res


def img_search(command):
    envir.vm_env.attachCurrentThread()
    command_dict = parseCommand(command, "imgtitle")
    querys = BooleanQuery()
    for k, v in command_dict.iteritems():
        query = QueryParser(Version.LUCENE_CURRENT, k,
                            envir.analyzer).parse(v)
        querys.add(query, BooleanClause.Occur.MUST)

    scoreDocs = envir.img_searcher.search(querys, 30).scoreDocs
    res = []

    query_highlight = QueryParser(Version.LUCENE_CURRENT, k,
                                  envir.analyzer).parse(command_dict["imgtitle"])
    myhighlighter = Highlighter(
        SimpleHTMLFormatter(), QueryScorer(query_highlight))
    myhighlighter.setTextFragmenter(SimpleFragmenter(50))
    for scoreDoc in scoreDocs:
        # find texts which are around the keyword
        doc = envir.img_searcher.doc(scoreDoc.doc)
        text = doc.get("imgtitle")
        key_text = "".join((myhighlighter.getBestFragment(
            envir.analyzer, "imgtitle", text)))
        key_text = re.sub('\s', '', key_text)
        temp = [key_text, doc.get('imgurl'), doc.get("url"), doc.get('price')]
        res.append(temp)
    return res


class searching:

    def GET(self):
        # lucene
        user_data = web.input()
        if(user_data.keyword == ""):
            return render.index()
        keyword = user_data.keyword.decode('utf-8', 'ignore')
        command = " ".join(jieba.cut_for_search(
            keyword, HMM=True))

        if(user_data.search_kind == "text"):
            return render.text(text_search(command), keyword, get_recommand(keyword))
        else:
            return render.img(img_search(command), keyword)


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
    del envir.text_searcher
    del envir.img_searcher
