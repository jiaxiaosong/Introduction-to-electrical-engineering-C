#!/usr/bin/env python

import sys
import os
#N = 4
p = 0.85
# input comes from STDIN (standard input)

for line in sys.stdin:
    line = line.strip()
    # split the input node-page.id pk-page.rank
    node, pk, out_nodes = line.split('\t', 2)
    try:
        pk = float(pk)
    except ValueError:
        # it was not a number, so silently
        # ignore/discard this line
        continue

    if(len(out_nodes) == 0):
        # No outnodes
        print(node+'\t'+'n')
    else:
        # print all the outnodes
        out_nodes = out_nodes.split()
        print(node+'\t'+'n '+' '.join(str(nodes) for nodes in out_nodes))
        rank = p*pk/len(out_nodes)
        for nodes in out_nodes:
                print '%s\t%s' % (nodes, rank)

