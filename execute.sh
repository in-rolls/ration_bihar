"#!/bin/bash"

ThisRange="${RAJ_RANGE}"

for i in $ThisRange
do
   nohup scrapy crawl bihar -o o$i.json -a n=$i > n$i.out &
done
