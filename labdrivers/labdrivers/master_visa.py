import visa
import logging
from statistics import mean, stdev
import ctypes
import PyDAQmx
from datetime import datetime
import time
import socket
import clr

class MasterVisa():
    def __init__(self):

    @property
    def gpib_addr(self):
        return self._gpib_addr