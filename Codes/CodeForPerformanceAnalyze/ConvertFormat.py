# This file is used to convert the format of the data file
# from the format of the original NPZ file to the format of the binary file so C can read it.

# Usage: python ConvertFormat.py <path that contains SubSum30.npz>

import numpy as np
import sys
import os

if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
    print("Error! Need input of SubSum30.npz's path")
    sys.exit(-1)

# Read the data from the NPZ file
file = np.load(f'{sys.argv[1]}/SubSum30.npz', allow_pickle=False)
data = file['SubSum']
print(data.shape)

# Convert the data to the format of the binary file
with open('./data.bin', 'wb') as file:
    data.tofile(file)
