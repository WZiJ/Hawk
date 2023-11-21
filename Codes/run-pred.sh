#!/bin/bash

# unzip test data
for n in {1..2}
do
    if [ ! -f "../Datasets/test-$n/SubSum30.npz" ]; then
        unzip ../Datasets/test-$n/test-$n.zip -d ../Datasets/test-$n
    fi
done

# # our previous prediction in total testing data
# for n in {0..17}
# do
#     python3 ./Predict.py ../../../dataset/CreateDataSet/ $n > ../PreResult/Res$n.txt
# done

# # show result of our pervious validation on 6 of testing data
# python3 ./cmpResult.py 0 17 ../PreResult ../GroundTruth > ./Result.txt


# prediction in 2 of testing data
for n in {1..2}
do
    python3 ./Predict.py ../Datasets $n > ../Result/Res$n.txt
done

# compare result
python3 ./cmpResult.py 1 2 ../Result ../GroundTruth > ./Result.txt