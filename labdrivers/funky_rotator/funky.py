""" This was made by Alex and Junseok, two guys who know zero C at all """

import ctypes
import numpy as np
from ctypes import *
import time

class Rotator:
    def __init__(self):
        #self.rotator = ctypes.WinDLL(
        #    "C:/ProgramData/Anaconda3/Lib/site-packages/labdrivers/funky_rotator/WJ_API.dll"
        #)
        self.rotator = ctypes.WinDLL(
            "R:/labdrivers/funky_rotator/WJ_API.dll"
        )
        self.rotator.WJ_Close.restype = c_int32

        self.rotator.WJ_Open.restype = c_int32
        self.rotator.WJ_Open.argtypes = [c_int32]

        self.rotator.WJ_Get_Axes_Pulses.argtypes = [ctypes.POINTER(c_int32 * 4)]
        self.rotator.WJ_Get_Axes_Pulses.restype = c_int32

        self.rotator.WJ_Move_Axis_Pulses.argtypes = [c_int32, c_int32]

        self.rotator.WJ_Get_Axis_Acc.argtypes = [c_int32, ctypes.POINTER(c_int32 * 1)]
        self.rotator.WJ_Get_Axis_Acc.restypes = c_int32

        self.pulse = (c_int32 * 4)()
        self.moving = (c_int32 * 1)()
        self.axis = 1
        self.acc = (c_int32 * 1)()
        self.vel_read = (c_int32 * 1)()

        self.rotator.WJ_Close()
        self.rotator.WJ_Open(0)
        self.rotator.WJ_Get_Axes_Pulses(self.pulse)

    def Go_To_Angle(self, degree):
        round(degree * 50004 / 360) + list(self.pulse)[0]
        if (degree >= 0) and (degree <= 360):
            pchange = round(degree * 50004 / 360) - list(self.pulse)[0]
            self.rotator.WJ_Move_Axis_Pulses(self.axis, pchange)
        else:
            raise RuntimeError("The angle must be between 0 and 360 degrees.")
        moving = True
        while moving == True:
            current_status = self.Read_Status()
            print("\r",f'Currently at {current_status[0]}{u'\N{DEGREE SIGN}'}, and moving to {degree}{u'\N{DEGREE SIGN}'}.',end='                                        ')
            if current_status[1] == 0:
                moving = False
                print("\r",f'Sitting at {current_status[0]}{u'\N{DEGREE SIGN}'}.',end='                                        ')
            time.sleep(1)

    def Move_By_Angle(self, degree):
        '''
        Moves to an angle between 0 and 360.
        '''
        round(degree * 50004 / 360) + list(self.pulse)[0]
        if (degree >= 0) and (degree <= 360):
            pchange = round(degree * 50004 / 360) - list(self.pulse)[0]
            self.rotator.WJ_Move_Axis_Pulses(self.axis, pchange)
        else:
            raise RuntimeError("The angle must be between 0 and 360 degrees.")

    def Read_Status(self):
        '''
        Returns the current angle in degrees [0] and the status [1] of the rotator.
        If the rotator is currently moving, returns 1 at [1]; if not, 0.
        '''
        self.rotator.WJ_Get_Axes_Pulses(self.pulse)
        self.rotator.WJ_Get_Axis_Status(self.axis, self.moving)
        first_reading = round(list(self.pulse)[0] * 360 / 50004, 2), self.moving[0]
        self.rotator.WJ_Get_Axes_Pulses(self.pulse)
        self.rotator.WJ_Get_Axis_Status(self.axis, self.moving)
        second_reading = round(list(self.pulse)[0] * 360 / 50004, 2), self.moving[0]
        return round(list(self.pulse)[0] * 360 / 50004, 2), self.moving[0]
    
    def Read_Acc(self):
        self.rotator.WJ_Get_Axis_Acc(self.axis, self.acc)
        return list(self.acc)[0]
    
    def Read_Speed(self):
        self.rotator.WJ_Get_Axis_Vel(self.axis, self.vel_read)
        return list(self.vel_read)[0]
    
    def Set_Speed(self,speed):
        self.rotator.WJ_Set_Axis_Vel(self.axis, speed)
        #return list(self.vel_set)[0]
        
    def Read_Angle(self,axis=1):
        self.rotator.WJ_Get_Axes_Pulses.argtypes = [ctypes.POINTER(c_long)]
        self.rotator.WJ_Get_Axes_Pulses.restype = c_long
        pulse_val = (c_long * 4)()
        self.rotator.WJ_Get_Axes_Pulses(pulse_val)
        pulse_vals = list(pulse_val)
        return np.array(pulse_vals)[0] * 360 / 50004
        #return round(self.current_steps * 360 / 50004,2)
    
"""
 def Set_Angle(degree, axis=1):
        rotator.WJ_Move_Axis_Pulses.argtypes = [c_int32, c_int32]
        pulses = int(degree * 50004 / 360)
        rotator.WJ_Move_Axis_Pulses(1, pulses)
"""