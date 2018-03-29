import web
import re
from web import form
import urllib2
import os
import sys
import lucene
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

vm_env = lucene.initVM(vmargs=['-Djava.awt.headless=true'])
text_directory = SimpleFSDirectory(File("text_index"))
img_directory = SimpleFSDirectory(File("img_index"))
text_searcher = IndexSearcher(DirectoryReader.open(text_directory))
img_searcher = IndexSearcher(DirectoryReader.open(img_directory))
analyzer = WhitespaceAnalyzer(Version.LUCENE_CURRENT)