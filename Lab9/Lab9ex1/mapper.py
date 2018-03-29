#!/usr/bin/env python

import sys
import string


#to delete the non-alpha character
delchar = string.punctuation+string.digits
identify = string.maketrans("","")

for line in sys.stdin:
    line = line.strip()
	#to delete the non-alpha character
    line = line.translate(identify, delchar)

    words = line.split()
    for word in words:
        if(not word.isalpha()):
            continue
        print '%s\t%s' % (word[0].lower(), len(word))
