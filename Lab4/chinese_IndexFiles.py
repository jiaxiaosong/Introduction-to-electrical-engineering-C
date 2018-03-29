#!/usr/bin/env python
# -*- coding=utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

INDEX_DIR = "IndexFiles.index"
root = "html"

import sys
import os
import lucene
import threading
import time
import re
import urllib2
from datetime import datetime

from java.io import File
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version

"""
This class is loosely based on the Lucene (java implementation) demo class 
org.apache.lucene.demo.IndexFiles.  It will take a directory as an argument
and will index all of the files in that directory and downward recursively.
It will index on the file path, the file name and the file contents.  The
resulting Lucene index will be placed in the current directory and called
'index'.
"""

# find what is the coding of the str


class Ticker(object):

    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)


class IndexFiles(object):
    """Usage: python IndexFiles <doc_directory>"""

    def __init__(self, indexfile, storeDir, analyzer):

        if not os.path.exists(storeDir):
            os.mkdir(storeDir)
        store = SimpleFSDirectory(File(storeDir))
        analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)
        config = IndexWriterConfig(Version.LUCENE_CURRENT, analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer = IndexWriter(store, config)

        self.indexDocs(indexfile, writer)
        ticker = Ticker()
        print 'commit index',
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        ticker.tick = False
        print 'done'

    def indexDocs(self, indexfile, writer):
        t1 = FieldType()
        t1.setIndexed(False)
        t1.setStored(True)
        t1.setTokenized(False)
        t1.setIndexOptions(FieldInfo.IndexOptions.DOCS_AND_FREQS)

        t2 = FieldType()
        t2.setIndexed(True)
        t2.setStored(False)
        t2.setTokenized(True)
        t2.setIndexOptions(FieldInfo.IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

        index_info = open(indexfile)
        for line in index_info.readlines():
            info = line.split('\t', 2)
            "adding", info[0]
            try:
                path = os.path.join(root, info[0])
                file = open(path)
                #contents = unicode(file.read(), 'gbk')
                contents = file.read()
                file.close()

                proto, rest = urllib2.splittype(info[1])
                domain, rest = urllib2.splithost(rest)
                if not domain:
                    domain = "unknown"
                if domain[0:4] == "www.":
                    domain = domain[4:]
                doc = Document()
                doc.add(Field("name", info[0], t1))
                doc.add(Field("path", os.path.abspath(path), t1))
                doc.add(Field("url", info[1], t1))
                doc.add(Field("title", info[2], t1))
                doc.add(Field("site", domain, Field.Store.YES, Field.Index.ANALYZED))

                if len(contents) > 0:
                    doc.add(Field("contents", contents, t2))
                else:
                    print "warning: no content in %s" % info[0]
                writer.addDocument(doc)
            except Exception, e:
                print "Failed in indexDocs:", e
            finally:
            	index_info.close()


if __name__ == '__main__':
    """
    if len(sys.argv) < 2:
        print IndexFiles.__doc__
        sys.exit(1)
    """
    #euv = lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print 'lucene', lucene.VERSION

    '''try:
        """
        base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        IndexFiles(sys.argv[1], os.path.join(base_dir, INDEX_DIR),
                   StandardAnalyzer(Version.LUCENE_CURRENT))
                   """
        analyzer = WhitespaceAnalyzer(Version.LUCENE_CURRENT)
        IndexFiles('indexfile.txt', "index", analyzer)
        end = datetime.now()
        print end - start
    except Exception, e:
        print "Failed: ", e
        raise e'''

euv = lucene.initVM(vmargs=['-Djava.awt.headless=true'])


def fn():
    global euv
    base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    euv.attachCurrentThread()
    IndexFiles('indexfile.txt', "index",
               WhitespaceAnalyzer(Version.LUCENE_CURRENT))


threads = []
thread_num = 5
for i in range(thread_num):
    t = threading.Thread(target=fn)
    t.setDaemon(True)
    threads.append(t)
    t.start()
for t in threads:
    t.join()
