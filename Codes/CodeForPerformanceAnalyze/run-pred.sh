#!/bin/bash

# for n in {1..15}
# do
#     python3 ./tryToPred.py $n > ./Trace/final/Res$n.txt
# done

# for n in {0..15}
# do
#     python3 ./tryToPred2.py $n > Trace/final/LRes$n.txt
# done


# cp ./cutResult4/MicrowaveOven.npz ./cutResult/

# python ./7-26.py ibm2 > ./Trace/Res106.txt
# python ./7-28.py libm2 > ./Trace/Res107.txt
for n in {0..10}
do
    (time taskset -c 1 ./hello > ./log/temp2-{$n}.txt ) 2> ./log/temp-{$n}.txt
done

# for n in {0..17}
# do
#     python3 ./tryToPred2.py $n > ./Trace/paper/LRes$n.txt
# done

# python ./7-26.py ibm > ./Trace/Res100.txt
# python ./7-28.py libm > ./Trace/Res101.txt