#!/bin/bash

#for local test
#get the path of this .sh
basepath=$(cd $(dirname ${BASH_SOURCE[0]}); pwd )

#create the folder and put the test2.txt into HDFS  
eval "hadoop fs -rm -r tempoutput"
eval "hadoop fs -rm -r tempinput"
eval "hadoop fs -mkdir tempinput"
eval "hadoop fs -copyFromLocal ${basepath}/$1 tempinput/test2.txt"

#get number of lines of the file-1, which equals to the number of the pages 
N=$(sed -n '$=' ${basepath}/$1)
let N-=1

command="hadoop jar /usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-2.8.2.jar \
-file ${basepath}/mapper.py \
-file ${basepath}/reducer.py \
-mapper mapper.py \
-reducer reducer.py"

mv='hadoop fs -mv '
rm='hadoop fs -rm -r '
cp='hadoop fs -copyToLocal'

#the function to compare float number
bigger(){
    awk -v n1="$1" -v n2="$2" 'BEGIN {if (n1+0>n2+0) exit 0; exit 1}'
}

#get the absolute value
abs() { echo ${1#-};}

function func()
{
#last page_rank of page.id 1
last_pk=1
#now the page rank of page.id 1
current_pk=$(sed -n "3,1p" ${basepath}/$1 | awk '{print $2}')
#the difference between them
diff=$(abs $(echo "scale=10; $last_pk - $current_pk" | bc))
cnt=1

while bigger $diff 0.001
do
    echo "Processing $cnt"
    eval "$command -input tempinput/* -output tempoutput -cmdenv N=$N"
    eval "$rm tempinput"
    eval "$mv /user/hadoop/tempoutput tempinput"
	eval "rm -r ${basepath}/result"
	eval "mkdir ${basepath}/result"
	eval "$cp tempinput/* ${basepath}/result"
	last_pk=$current_pk
	current_pk=$(sed -n "2,1p" ${basepath}/result/part-00000 | awk '{print $2}')
	diff=$(abs $(echo "scale=10; $last_pk - $currentpk" | bc))
	let cnt+=1
done
}

func $1

