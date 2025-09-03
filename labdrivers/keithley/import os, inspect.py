import os, inspect
os.chdir('R:\\')

from labdrivers.srs import Sr830
from labdrivers.oxford import Triton200
#from labdrivers.ni import Nidaq
from labdrivers.keithley.keithley2400 import Keithley2400

import pyvisa as visa
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
#import scipy
import time
import cycler
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
from retry import retry

from IPython import display

#matplotlib inline
os.path.dirname(inspect.getfile(Keithley2400))
keithley = Keithley2400(gpib_addr=20)
keithley.measure_type = 'current'
keithley.source_type = 'voltage'
keithley.current_compliance = 0.01
#Create a file
Directory = 'C:\\Users\\jsshim2\\Madhavan Group\\';
num = 1
numstr = str(num)
date = datetime.today().strftime("%d%m%Y")
form = '.txt'
test = 'VoltageRampTest'
fname = Directory + date + test + numstr + form
check = os.path.exists(fname)
while check == True:
        num = num + 1
        numstr = str(num)
        fname = Directory + date + test + numstr + form
        check = os.path.exists(fname)
#createfile = open(fname,"x")
newfile = open(fname,"a")

dV = 0.1
Vgate = 1
keithley._instrument.write("OUTP ON")
keithley.read('voltage')
V = 0
t = 0
while V < Vgate:
    V = V + dV
    keithley.source_value = V
    time.sleep(0.2)
    current = keithley.read('current')[0]
    voltage = keithley.read('voltage')[0]
    time.sleep(0.2)
    now = datetime.now().strftime('%H:%M:%S')
    print(now)
    print(current,voltage,V)
    newfile.write(f'{datetime.now().strftime("%B %d, %Y %H:%M:%S")}\t')
    newfile.write(f'Current\t{current[0]}\tVoltage\t{voltage[0]}\t{V}\n')
    time.sleep(0.6)
    t = t + 1

keithley._instrument.write("OUTP OFF")