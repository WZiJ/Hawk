# Usage: python RunTimeStatistic.py <path that contains output log of runtime>

import re
import sys
import os

sumTime = 0

if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
    print("Error! Need input of path that contains output log of runtime")
    sys.exit(-1)

for i in range(10):
    with open(sys.argv[1] + '/temp2-{'+str(i)+'}.txt', 'r') as file:
        tempLine = file.readline()
        file.close()
        # read double values in the line from the file contains runtime
        doubleVal = re.findall(r'[-+]?\d*\.\d+|\d+', tempLine)
        sumTime += float(doubleVal[0])

print(sumTime * 1000 / 10 / 70172)
