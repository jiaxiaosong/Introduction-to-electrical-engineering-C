#!/usr/bin/env python

from operator import itemgetter
import sys

#total-the sum of length, count-the number of length
current_char = None
current_count = 0.0
total = 0.0

for line in sys.stdin:
    line = line.strip()
	
    char, length = line.split('\t', 1)

    try:
        length = int(length)
    except ValueError:
        continue

    if current_char == char:
        current_count += 1.0
        total += length
    else:
        if current_char:
            print '%s\t%s' % (current_char, float(total)/float(current_count))
        current_count = 1.0
        current_char = char
        total = length

# do not forget to output the last word if needed!
if current_char == char:
    print '%s\t%s' % (current_char, float(total)/float(current_count))
