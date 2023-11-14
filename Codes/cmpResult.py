import re


def Merge(real, pred, endCycle):
    print(real, pred)
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
            print("FN", real[i], pred[j])
            i += 1
            falseNeg += 1
        elif real[i] > pred[j] + 1500:
            print("FP", real[i], pred[j])
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
# for cmpIndx in range(18):
for cmpIndx in range(1, 7):
    highAppFile = open(f'../Result/Res{cmpIndx}.txt', 'r')
    fileConts = highAppFile.readlines()
    endCycle = int(fileConts[21].split('\t')[1])
    highAppFile.close()

    resultFile = open(f'../GroundTruth/FeaList{cmpIndx}.txt', 'r')
    print("Compare index: ", cmpIndx)

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
            # print(lineConts[0], leftBuf, rightBuf)

    resultFile.close()

    fileLen = []

    highAppFile = open(f'../Result/Res{cmpIndx}.txt', 'r')

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
                if item[1]+item2[1] > 0 or item[2]+item2[2] > 0:
                    print(appName)
                    print(item)
                    print(startEvent, leftAllBuf[k])
                    print(item2)
                    print(endEvent, rightAllBuf[k])
                break

    print('=========')
    for l in range(11, 21, 2):
        print(fileConts[l])
        startStr = re.findall('\d+', fileConts[l])
        endStr = re.findall('\d+', fileConts[l+1])
        appName = fileConts[l].split(' [')[0]

        print(appName, startStr, endStr)
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
                if item[1]+item2[1] > 0 or item[2]+item2[2] > 0:
                    print(appName)

                    print(item)
                    print(startEvent, leftAllBuf[k])
                    print(item2)
                    print(endEvent, rightAllBuf[k])
                break

for i in range(15):
    print(appNameList[i], truePos[i], falsePos[i], falseNeg[i], sep='\t')
