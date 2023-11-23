#!/bin/bash

for n in {0..10}
do
    (time taskset -c 1 ./hello ../../Models/ > ./log/temp2-{$n}.txt ) 2> ./log/temp-{$n}.txt
done

python ./RunTimeStatistic.py ./log/