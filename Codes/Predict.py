import xgboost  # work well on 1.5.2
import numpy as np
from numpy import fft
import sys
import time

# The input to model just 0-9th harmonics
RemainLen = 10


def sortAlgorithm(a):
    return a[0]


def sortAlgorithm1(a):
    return a[1]

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python Predict.py [path] [fileId]")
        sys.exit(-1)
        
    startTime = time.time()
    print(f"python {sys.argv[0]} {sys.argv[1]} {sys.argv[2]}")
    largeApps = []
    openUpper = []
    openDowner = []
    closeUpper = []
    closeDowner = []

    littleApps = []
    littlePos = []
    largeApps = []
    minPos1 = 320
    llPosList = []
    lrPosList = []
    rlPosList = []
    rrPosList = []
    appNameList = []

    openUpper = []
    openDowner = []
    closeUpper = []
    closeDowner = []
    lOpenUpper = []
    lOpenDowner = []
    lCloseUpper = []
    lCloseDowner = []
    with open('./appFeature.cfg', 'r') as fFile:
        pos = 0
        while True:
            lineCont = fFile.readline()

            if not lineCont:
                break
            conts = lineCont.split('\t')
            appNameList.append(conts[0])
            if len(conts[11]) > 1:
                littleApps.append(conts[0])
                lOpenDowner.append(int(conts[6]))
                lOpenUpper.append(int(conts[7]))
                lCloseDowner.append(int(conts[8]))
                lCloseUpper.append(int(conts[9]))
                llPosList.append(int(conts[11]))
                lrPosList.append(int(conts[12]))
                rlPosList.append(int(conts[13]))
                rrPosList.append(int(conts[14]))
                littlePos.append(pos)
            else:
                largeApps.append(conts[0])
                openDowner.append(int(conts[6]))
                openUpper.append(int(conts[7]))
                closeDowner.append(int(conts[8]))
                closeUpper.append(int(conts[9]))
            pos += 1
        fFile.close()

    sumSubFile = np.load(
        f'{sys.argv[1]}/test-{sys.argv[2]}/SubSum30.npz', allow_pickle=False)

    # read differential aggregated current for interval of 30 cycles(600ms)
    testDat = sumSubFile['SubSum']

    # load model
    allModel = xgboost.Booster()
    allModel.load_model('../Models/all.model')
    
    littleModels = []

    for i in range(len(littleApps) * 2):
        littleModels.append(xgboost.Booster())
        littleModels[i].load_model(f'../Models/little-{i}.model')

    # use fft to extract features and normalize the features, then we cut and concatenate the features
    testDat_fft = fft.fft(testDat)[:, :RemainLen] / 161

    testFFTDat = np.concatenate(
        (np.abs(testDat_fft), np.imag(testDat_fft), np.real(testDat_fft)), axis=1)



    # This is a trick, we train and test with this transform
    testFFTDat[:, 0] = testFFTDat[:, 0] + testFFTDat[:, 1]
    testFFTDat[:, RemainLen] += testFFTDat[:, RemainLen + 1]
    testFFTDat[:, RemainLen*2] += testFFTDat[:, RemainLen*2 + 1]

    littleFeaList = []
    for i in range(len(littleApps)):
        cutFeature = np.concatenate(
            (testDat[:, llPosList[i]:lrPosList[i]], testDat[:, rlPosList[i]:rrPosList[i]]), axis=1)
        shortFFT = fft.fft(cutFeature, axis=1)[
            :, :RemainLen] / (len(cutFeature[0]) / 2 + 1)
        shortFFT = np.concatenate(
            (np.abs(shortFFT), np.imag(shortFFT), np.real(shortFFT)), axis=1)
        littleFeaList.append(shortFFT)

    prePareTime = (time.time() - startTime) * 1000
    predictResults = []
    dTTest = xgboost.DMatrix(testFFTDat)
    startTime = time.time()
    resul = allModel.predict(dTTest)

    predPos = [[] for i in range(20)]

    # filtrate maxPos by FFT range
    for j in range(len(testFFTDat)):
        maxPos = int(resul[j] + 0.5)
        if maxPos < 20:
            if maxPos % 2 == 1:
                if testFFTDat[j][1] > closeUpper[int(maxPos / 2)] or testFFTDat[j][1] < closeDowner[int(maxPos / 2)]:
                    continue
            else:
                if testFFTDat[j][1] > openUpper[int(maxPos / 2)] or testFFTDat[j][1] < openDowner[int(maxPos / 2)]:
                    continue
            predPos[maxPos].append(j)

    EventList = [[] for _ in range(20)]
    # vote number over 30 cycles
    voteNumList = [[] for _ in range(20)]

    # vote Threshold for large appliances
    voteThresList = [5, 10, 6, 3, 9, 4, 8, 2, 23, 12]

    # filtrate maxPos by vote number and state of appliance's on/off
    for i in range(20):
        curInd = 0
        for k in range(len(predPos[i]) - voteThresList[int(i/2)]):
            if k >= curInd:
                if predPos[i][k] > predPos[i][k + voteThresList[int(i/2)]] - 30:
                    if len(EventList[i]) == 0 or EventList[i][-1] < predPos[i][k] - 50:

                        EventList[i].append(predPos[i][k])
                        voteNum = 0
                        for l in range(30):
                            if k+l < len(predPos[i]) and predPos[i][k + l] - predPos[i][k] < 30:
                                voteNum += 1
                        voteNumList[i].append(voteNum)
                        curInd = voteThresList[int(i/2)] + k

    for i in range(10):
        EventList[i * 2 + 1].append(10000000)
        voteNumList[i * 2 + 1].append(1)

    appRangeList = [[] for i in range(10)]

    for i in range(10):
        appState = -1
        appAllEventList = []
        for l in range(len(EventList[i * 2])):
            appAllEventList.append(
                (EventList[i * 2][l], 1, voteNumList[i * 2][l]))
        for l in range(len(EventList[i * 2 + 1])):
            appAllEventList.append(
                (EventList[i * 2 + 1][l], 0, voteNumList[i * 2 + 1][l]))
        appAllEventList = sorted(appAllEventList, key=sortAlgorithm)
        if appAllEventList[0][1] == 0:
            appState = 1
        else:
            appState = 0
        startPos = 0
        preVoteNum = 0
        for l in range(len(appAllEventList)):
            if appState == 1 and appAllEventList[l][1] == 0:
                appRangeList[i].append([startPos, appAllEventList[l][0]])
                preVoteNum = appAllEventList[l][2]
                appState = 0
            elif appState == 0 and appAllEventList[l][1] == 1:
                startPos = appAllEventList[l][0]
                preVoteNum = appAllEventList[l][2]
                appState = 1
            elif appState == 1 and appAllEventList[l][1] == 1:
                if appAllEventList[l][2] > preVoteNum:
                    if len(appRangeList[i]) > 0:
                        appRangeList[i][-1][1] = appAllEventList[l][0]
                        preVoteNum = appAllEventList[l][2]
            elif appState == 0 and appAllEventList[l][1] == 0:
                if appAllEventList[l][2] > preVoteNum:
                    startPos = appAllEventList[l][0]
                    preVoteNum = appAllEventList[l][2]
        print(largeApps[i], appRangeList[i])

    predPossibLists = []
    for i in range(len(littleApps)):
        testdd = xgboost.DMatrix(littleFeaList[i])
        pred1 = littleModels[i * 2].predict(testdd)
        predPossibLists.append(pred1)

        testdd = xgboost.DMatrix(littleFeaList[i])
        pred2 = littleModels[i * 2 + 1].predict(testdd)
        predPossibLists.append(pred2)

    littlePos = [[] for i in range(len(littleApps) * 2)]
    for l in range(len(resul)):
        if resul[l] == 20:
            maxPas = 0
            maxPos = -1

            for k in range(len(predPossibLists)):
                if predPossibLists[k][l] > 0.5:
                    if k % 2 == 0:
                        if littleFeaList[int(k/2)][l][1] > lOpenDowner[int(k/2)] and littleFeaList[int(k/2)][l][1] < lOpenUpper[int(k/2)]:
                            littlePos[k].append(l)
                    else:
                        if littleFeaList[int(k/2)][l][1] > lCloseDowner[int(k/2)] and littleFeaList[int(k/2)][l][1] < lCloseUpper[int(k/2)]:
                            littlePos[k].append(l)


    voteNumList = [12, 12, 10, 10, 10, 8, 6, 6, 10, 10]
    for i in range(len(littlePos)):
        for k in range(voteNumList[i]):
            littlePos[i].append(1000000000)
    littleEventList = [[] for i in range(2 * len(littleApps))]
    try:
        for i in range(len(littlePos)):
            curInd = 0
            for k in range(len(littlePos[i]) - voteNumList[i] - 1):
                if k >= curInd:
                    if littlePos[i][k] > littlePos[i][k + voteNumList[i]] - 30:
                        if len(littleEventList[i]) == 0 or littlePos[i][littleEventList[i][-1]] < littlePos[i][k] - 50:
                            littleEventList[i].append(k)
                            curInd = voteNumList[i] + k
    except Exception as e:
        print(i, len(littlePos), voteNumList[i])
        print(str(e))
        sys.exit(-1)

    for i in range(len(littlePos)):
        print(littleApps[int(i / 2)] + ' [', end=' ')
        for j in range(len(littleEventList[i])):
            print(littlePos[i][littleEventList[i][j]], end=', ')
        print(']')
    print("Cycle number:\t", testFFTDat.shape[0])
    print("Prepare time:\t", prePareTime, "ms")
    print("Classification time:\t", (time.time() - startTime) * 1000, "ms")
