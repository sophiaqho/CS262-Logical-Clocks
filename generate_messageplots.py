import os
import socket
import math
import time
from datetime import datetime
import random
import logging
import numpy as np
import matplotlib.pyplot as plt

# load the message log files
filepath = "/Users/sanjana/Documents/GitHub/CS262-Logical-Clocks/"
filename1 = "MessageLog_1.txt"
filename2 = "MessageLog_2.txt"
filename3 = "MessageLog_3.txt"

array1 = np.loadtxt(filepath + filename1)
array2 = np.loadtxt(filepath + filename2)
array3 = np.loadtxt(filepath + filename3)

# print('array1', array1, 'array2', array2, 'array3', array3)

# get the times per operation
time_1 = array1[0]
time_2 = array2[0]
time_3 = array3[0]

# generate arrays with 120 entries per second
# LCD(1, 2, 3, 4, 5, 6) = 120; every operation
# takes place on an instance
def generate_larger_arrays(array1, array2, array3):
    inflated_len_1 = (len(array1) * 120) / array1[0]
    inflated_len_2 = (len(array2) * 120) / array2[0]
    inflated_len_3 = (len(array3) * 120) / array3[0]

    # TODO- ss

# manipulate the arrays
large_1_array, large_2_array, large_3_array = generate_larger_arrays(array1, array2, array3)


# want to graph these
plt.plot()
