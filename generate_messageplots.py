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
filepath = "/Users/sanjana/Documents/GitHub/CS262-Logical-Clocks/graphed_trial2/"
filename1 = "MessageLog_1.txt"
filename2 = "MessageLog_2.txt"
filename3 = "MessageLog_3.txt"
outfile1 = "MessageQueue_1.png"
outfile2 = "MessageQueue_2.png"
outfile3 = "MessageQueue_3.png"

array1 = np.loadtxt(filepath + filename1)
array2 = np.loadtxt(filepath + filename2)
array3 = np.loadtxt(filepath + filename3)

# print('array1', array1, 'array2', array2, 'array3', array3)

# get the times per operation
time_1 = array1[0]
time_2 = array2[0]
time_3 = array3[0]

label_machine_1 = str(time_1) + " operations per second"
label_machine_2 = str(time_2) + " operations per second"
label_machine_3 = str(time_3) + " operations per second"

# want to graph these
plt.plot(array1[1:])
plt.xlabel("Logical Clock Time")
plt.ylabel("Length of Message Queue")
plt.yticks(np.arange(0, 25, 1.0))
plt.title(label_machine_1)
plt.savefig(filepath + outfile1)
plt.clf()

plt.plot(array2[1:])
plt.xlabel("Logical Clock Time")
plt.ylabel("Length of Message Queue")
plt.yticks(np.arange(0, 25, 1.0))
plt.title(label_machine_2)
plt.savefig(filepath + outfile2)
plt.clf()

plt.plot(array3[1:])
plt.xlabel("Logical Clock Time")
plt.ylabel("Length of Message Queue")
plt.yticks(np.arange(0, 25, 1.0))
plt.title(label_machine_3)
plt.savefig(filepath + outfile3)