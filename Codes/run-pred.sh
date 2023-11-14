#!/bin/bash

for n in {1..6}
do
    python3 ./Predict.py $n > ../Result/Res$n.txt
done
