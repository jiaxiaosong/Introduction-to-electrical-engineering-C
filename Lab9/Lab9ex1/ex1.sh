#!/bin/bash

#for local test
basepath=$(cd $(dirname ${BASH_SOURCE[0]}); pwd )
eval "hadoop fs -rm -r tempoutput"
eval "hadoop fs -rm -r tempinput"
eval "hadoop fs -mkdir tempinput"
eval "hadoop fs -copyFromLocal ${basepath}/$1 tempinput/test1.txt"

command='hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-2.8.2.jar -file ${basepath}/mapper.py -file ${basepath}/reducer.py -mapper mapper.py -reducer reducer.py'
rm='hadoop fs -rm -r '
cp='hadoop fs -copyToLocal '

eval "$command -input tempinput/* -output tempoutput"
eval "rm -r ${basepath}/result"
eval "mkdir ${basepath}/result"
eval "$cp tempoutput/* ${basepath}/result"
