#!/usr/bin/env python

from operator import itemgetter
import sys
import os

out_nodes = []
current_node = None
current_pk = 0.0
N = int(os.environ["N"])
#N = 4
p = 0.85
# input comes from STDIN
for line in sys.stdin:
    # remove leading and trailing whitespace
    line = line.strip()

    # parse the input we got from mapper.py
    node, data = line.split('\t', 1)

    # this IF-switch only works because Hadoop sorts map output
    # by key (here: word) before it is passed to the reducer
    if current_node == node:
        # This data is about outbound
        if(data[0] == 'n'):
            out_nodes = data.split()[1:]
        # This data is about pagerank
        else:
            current_pk += float(data)
    else:
        if current_node:
            # write result to STDOUT
            print(str(current_node)+'\t'+str(current_pk+(1-p)/float(N))+'\t' +
                  ' '.join(str(nodes) for nodes in out_nodes))
        current_node = node
        out_nodes = []
        # This data is about outbound
        if(data[0] == 'n'):
            out_nodes = data.split()[1:]
            current_pk = 0.0
		# This data is about pagerank
        else:
            current_pk = float(data)

# do not forget to output the last word if needed!
if current_node:
    # write result to STDOUT
    print(str(current_node)+'\t'+str(current_pk+(1-p)/float(N))+'\t' +
          ' '.join(str(node) for node in out_nodes))
