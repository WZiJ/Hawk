import re
import sys

def Merge(real, pred, endCycle):
    truePos = 0
    falsePos = 0
    falseNeg = 0

    i = 0
    j = 0
    if len(real) > 1 and len(pred) > 1:
        if real[i] == 0:
            i += 1
        if pred[j] == 0:
            j += 1
        if real[-1] > endCycle - 500:
            real = real[:-1]
        if pred[-1] > endCycle - 500:
            pred = pred[:-1]
    while i < len(real) and j < len(pred):
        if real[i] < pred[j] - 1500:
            i += 1
            falseNeg += 1
        elif real[i] > pred[j] + 1500:
            j += 1
            falsePos += 1
        else:
            i += 1
            j += 1
            truePos += 1
    if i < len(real):
        falseNeg += len(real) - i
    if j < len(pred):
        falsePos += len(pred) - j
    return [truePos, falsePos, falseNeg]


lowAppNameList = ['Monitor', 'Humidifier',
                  'LEDLamp', 'Kneader', 'FluorescentLamp']

recogAppNameList = ['Humidifier', 'Kneader', 'MicrowaveOven', 'ElectricCooker',
                    'InductionCooker', 'SmartScreen', 'Washer', 'AirHeater', 'ElectricKettle']

truePos = [0] * 18
falsePos = [0] * 18
falseNeg = [0] * 18
appNameList = []

if __name__ == '__main__':
    # for cmpIndx in range(18):
    startFileId = int(sys.argv[1])
    endFileId = int(sys.argv[2])
    predFilePath = sys.argv[3]
    groundTruthPath = sys.argv[4]
    
    for cmpIndx in range(startFileId, endFileId + 1):
        highAppFile = open(f'{predFilePath}/Res{cmpIndx}.txt', 'r')
        fileConts = highAppFile.readlines()
        endCycle = int(fileConts[21].split('\t')[1])
        highAppFile.close()

        resultFile = open(f'{groundTruthPath}/FeaList{cmpIndx}.txt', 'r')

        leftAllBuf = []
        rightAllBuf = []
        appNameList = []

        for i in range(18):
            line = resultFile.readline()
            if not line.startswith('Desktop') and not line.startswith('PhoneCharger') and not line.startswith('Roomba'):
                lineConts = line.split(":")
                appNameList.append(lineConts[0])
                leftBuf = []
                rightBuf = []

                if len(lineConts) > 1:
                    numbers = re.findall('\d+', lineConts[1])
                    # print(numbers)
                    for l in range(0, len(numbers), 2):
                        lf = int(numbers[l])
                        rt = int(numbers[l + 1])
                        if rt > lf:
                            leftBuf.append(lf)
                            rightBuf.append(rt)
                if lineConts[0] in lowAppNameList and len(leftBuf) > 0 and leftBuf[0] == 0:
                    leftBuf = leftBuf[1:]
                    rightBuf = rightBuf[:-1]
                leftAllBuf.append(leftBuf)
                rightAllBuf.append(rightBuf)

        resultFile.close()

        fileLen = []

        highAppFile = open(f'{predFilePath}/Res{cmpIndx}.txt', 'r')

        fileConts = highAppFile.readlines()

        fileLen.append(endCycle)

        for l in range(1, 11):
            strList = re.findall('\d+', fileConts[l])
            startEvent = []
            endEvent = []
            if len(strList) == 0 or (strList[0] == '0' and strList[1] == '10000000'):
                continue
            for i in range(0, len(strList), 2):
                startEvent.append(int(strList[i]))
                if i < (len(strList) - 1) and strList[i+1] != '10000000':
                    endEvent.append(int(strList[i+1]))
                else:
                    endEvent.append(endCycle)

            appName = fileConts[l].split(' [[')[0]
            for k in range(len(appNameList)):
                if appNameList[k] == appName:
                    # if appNameList[k] == appName and appName in recogAppNameList:
                    item = Merge(leftAllBuf[k], startEvent, endCycle)
                    item2 = Merge(rightAllBuf[k], endEvent, endCycle)
                    truePos[k] += item[0]+item2[0]
                    falsePos[k] += item[1]+item2[1]
                    falseNeg[k] += item[2]+item2[2]
                    break

        for l in range(11, 21, 2):
            startStr = re.findall('\d+', fileConts[l])
            endStr = re.findall('\d+', fileConts[l+1])
            appName = fileConts[l].split(' [')[0]

            if len(startStr) == 0 and len(endStr) == 0:
                continue
            startEvent = []
            endEvent = []
            for i in range(0, len(startStr)):
                startEvent.append(int(startStr[i]))
            for i in range(0, len(endStr)):
                endEvent.append(int(endStr[i]))

            for k in range(len(appNameList)):
                if appNameList[k] == appName:
                    # if appNameList[k] == appName and appName in recogAppNameList:
                    item = Merge(leftAllBuf[k], startEvent, endCycle)
                    item2 = Merge(rightAllBuf[k], endEvent, endCycle)
                    truePos[k] += item[0]+item2[0]
                    falsePos[k] += item[1]+item2[1]
                    falseNeg[k] += item[2]+item2[2]
                    break
    print('App Name', 'True Pos', 'False Pos', 'False Neg', sep='\t')
    for i in range(15):
        print(appNameList[i], truePos[i], falsePos[i], falseNeg[i], sep='\t')
