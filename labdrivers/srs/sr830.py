"""Module containing a class to interface with a SR830 Lockin Amplifier

This module requires a National Instruments VISA driver, which can be found at
https://www.ni.com/visa/

Attributes:
    resource_manager: the pyvisa resource manager which provides the visa
                      objects used for communicating over the GPIB interface

    logger: a python logger object


Classes:
    sr830: a class for interfacing with a SR830 Lockin Amplifier

"""
import time
import logging

import visa
from pyvisa.errors import VisaIOError

# create a logger object for this module
logger = logging.getLogger(__name__)
# added so that log messages show up in Jupyter notebooks
logger.addHandler(logging.StreamHandler())


class sr830:
    """A class to interface with the SR830 lockin amplifier

    :param GPIBaddr: the GPIB address of the instrument
    """
    TIME_CONSTANT = { 0: '10 us',  10: '1 s',
                      1: '30 us',  11: '3 s',
                      2: '100 us', 12: '10 s',
                      3: '300 us', 13: '30 s',
                      4: '1 ms',   14: '100 s',
                      5: '3 ms',   15: '300 s',
                      6: '10 ms',  16: '1 ks',
                      7: '30 ms',  17: '3 ks',
                      8: '100 ms', 18: '10 ks',
                      9: '300 ms', 19: '30 ks'}

    SENSITIVITY = {   0: "2 nV/fA",		13: "50 uV/pA",
					  1: "5 nV/fA",		14: "100 uV/pA",
					  2: "10 nV/fA",	15: "200 uV/pA",
					  3: "20 nV/fA",	16: "500 uV/pA",
					  4: "50 nV/fA",	17: "1 mV/nA",
					  5: "100 nV/fA",	18: "2 mV/nA",
					  6: "200 nV/fA",	19: "5 mV/nA",
					  7: "500 nV/fA",	20: "10 mV/nA",
					  8: "1 uV/pA",		21: "20 mV/nA",
					  9: "2 uV/pA",		22: "50 mV/nA",
					 10: "5 uV/pA",		23: "100 mV/nA",
					 11: "10 uV/pA",	24: "200 mV/nA",
					 12: "20 uV/pA",	25: "500 mV/nA",
										26: "1 V/uA"}

    def __init__(self, GPIBaddr):
        """Create an instance of the sr830 class.

        Args:
            GPIBaddr (int): The GPIB address of the instrument.
        """
        try:
            # the pyvisa manager we'll use to connect to the GPIB resources
            resource_manager = visa.ResourceManager()
        except OSError:
            logger.exception("\n\tCould not find the VISA library. Is the National Instruments VISA driver installed?\n\n")
        
        self._gpib_addr = GPIBaddr
        self._instrument = None


    def __enter__(self):
        self._instrument = resource_manager.open_resource("GPIB::%d" % self._gpib_addr)


    def __exit__(self):
        self._instrument.close()


    def enable_remote(self):
        self._instrument = resource_manager.open_resource("GPIB::%d" % self._gpib_addr)


    def disable_remote(self):
        self._instrument.close()


    @property
    def sync_filter(self):
        """
        The state of the sync filter (< 200 Hz).
        """
        return self._instrument.query_ascii_values('SYNC?')[0]


    @sync_filter.setter
    def sync_filter(self, value):
        if isInstance(value, bool):
            self._instrument.query_ascii_values('SYNC {}'.format(int(value)))
        else:
            raise RuntimeError('Sync filter input expects [True|False].')


    @property
    def low_pass_filter_slope(self):
        """
        The low pass filter slope in units of dB/octave. The choices are:

         i   slope(dB/oct) 
        ---  -------------
         0         6
         1        12
         2        18
         3        24
        """
        response = self._instrument.query_ascii_values('OSFL?')[0]
        slope = {'0': '6 dB/oct', '1': '12 dB/oct', '2': '18 dB/oct', '3': '24 dB/oct'}
        return slope[response]


    @low_pass_filter_slope.setter
    def low_pass_filter_slope(self, value):
        """
        Sets the low pass filter slope.

        :param value: The slope in units of dB/oct.
        """
        if value in (6, 12, 18, 24):
            slope = {6: '0', 12: '1', 18: '2', 24: '3'}
            self._instrument.query_ascii_values('OSFL {}'.format(slope[value]))
        else:
            raise RuntimeError('Low pass filter slope only accepts [6|12|18|24].')


    @property
    def reserve(self):
        """
        The reserve mode of the SR830.
        """
        reserve = {'0': 'high', '1': 'normal', '2': 'low noise'}
        response = self._instrument.query_ascii_values('RMOD?')[0]
        return reserve[response]


    @reserve.setter
    def reserve(self, value):
        if isInstance(value, str):
            mode = value.lower()
        elif isInstance(value, int):
            mode = value
        else:
            raise RuntimeError('Reserve expects a string or integer argument.')
        
        modes_dict = {  'hi': 0, 'high': 0, 'high reserve': 0, 0: 0
                        'normal': 1, 1: 1,
                        'lo': 2, 'low': 2, 'low noise': 2, 2: 2}
        if mode in modes_dict.keys():
            self._instrument.query_ascii_values('RMOD {}'.format(mode))
        else:
            raise RuntimeError('Incorrect key for reserve.')


    @property
    def frequency(self):
        """
        The frequency of the output signal.
        """
        return self._instrument.query_ascii_values('FREQ?')[0]


    @frequency.setter
    def frequency(self, value):
        if 0.001 <= value <= 102000:
            self._instrument.write("FREQ {}".format(value))
        else:
            raise RuntimeError('Valid frequencies are between 0.001 Hz and 102 kHz.')
    

    @property
    def input(self):
        """
        The input on the SR830 machine. Possible values:
            0: A
            1: A-B
            2: I (1 MOhm)
            3: I (100 MOhm)
        """
        return self._instrument.query_ascii_values('ISRC?')


    @input.setter
    def input(self, input_value):
        input = {   '0': 0, 0:0, 'A': 0,
                    '1': 1, 1:1, 'A-B': 1, 'DIFFERENTIAL': 1,
                    '2': 2, 2:2, 'I1': 2, 'I1M': 2, 'I1MOHM': 2,
                    '3': 3, 3:3, 'I100': 3, 'I100M': 3, 'I100MOHM': 3
                }
        if isInstance(input_value, str):
            query = input_value.upper().replace('(','').replace(')','').replace(' ','')
        else:
            query = input_value

        if query in input.keys():
            command = input[query]
            self._instrument.write("ISRC {}".format(command))
        else:
            raise RuntimeError('Unexpected input for SR830 input command.')


    @property
    def phase(self):
        """
        The phase of the output relative to the input.
        """
        return self._instrument.query_ascii_values('PHAS?')[0]


    @phase.setter
    def phase(self, value):
        if (isInstance(value, float) or isInstance(value, int) and -360.0 <= value <= 729.99):
            self._instrument.write("PHAS {}".format(value))
        else:
            raise RuntimeError('Given phase is out of range for the SR830. Should be between -360.0 and 729.99.')
    
    
    @property
    def amplitude(self):
        """
        The amplitude of the voltage output.
        """
        return self._instrument.query_ascii_values('SLVL?')[0]

    
    @amplitude.setter
    def amplitude(self, value):
        if 0.004 <= value <= 5.0:
            self._instrument.write("SLVL {}".format(value))
        else:
            raise RuntimeError('Given amplitude is out of range. Expected 0.004 to 5.0 V.')


    @property
    def time_constant(self):
        """
        The time constant of the SR830.
        """
        const_index = self._instrument.query_ascii_values('OFLT?')[0]
        return TIME_CONSTANT[const_index]


    @time_constant.setter
    def time_constant(self, value):
        if value.lower() == 'increment':
            if self.time_constant + 1 <= 19:
                self.time_constant += 1
        elif value.lower() == 'decrement':
            if self.time_constant - 1 >= 0:
                self.time_constant -= 1
        elif 0 <= value <= 19:
            self._instrument.write("SENS {}".format(value))
        else:
            raise RuntimeError('Time constant index must be between 0 and 19 (inclusive).')
		
		
    @property
    def sensitivity(self):
        sens_index = self._instrument.query_ascii_values('SENS?')[0]
        return sense_dict[sens_index]


    @sensitivity.setter
    def sensitivity(self, value):
        self._instrument.write("SENS {}".format(sens_index))

                
    def setDisplay(self, channel, display, ratio=0):
        """Set the display of the amplifier.

        Display options are:
        (for channel 1)     (for channel 2)
            0: X            0: Y
            1: R            1: Theta
            2: X Noise      2: Y Noise
            3: Aux in 1     3: Aux in 3
            4: Aux in 2     4: Aux in 4

        Ratio options are (i.e. divide output by):
            0: none         0: none
            1: Aux in 1     1: Aux in 3
            2: Aux in 2     2: Aux in 4

        Args:
            channel (int): which channel to modify (1 or 2)
            display (int): what to display
            ratio (int, optional): display the output as a ratio
        """
        self._instrument.write("DDEF {}, {}, {}".format(channel, display, ratio))
        
    def getDisplay(self, channel):
        """Get the display configuration of the amplifier.

        Display options are:
        (for channel 1)     (for channel 2)
            0: X            0: Y
            1: R            1: Theta
            2: X Noise      2: Y Noise
            3: Aux in 1     3: Aux in 3
            4: Aux in 2     4: Aux in 4

        Args:
            channel (int): which channel to return the configuration for

        Returns:
            int: the parameter being displayed by the amplifier
        """
        return self._instrument.query_ascii_values("DDEF? {}".format(channel))
    
    def single_output(self, value):
        """Get the current value of a single parameter.
        Possible parameter values are:
            1: X
            2: Y
            3: R
            4: Theta

        Returns:
            float: the value of the specified parameter
        """
        return self._instrument.query_ascii_values("OUTP? {}".format(value))
            
    def multiple_output(self, *values):
        """Get the current value of between two and six instrument parameters.
        Possible parameters are:
            1: X
            2: Y
            3: R
            4: Theta
            5: Aux in 1
            6: Aux in 2
            7: Aux in 3
            8: Aux in 4
            9: Reference frequency
            10: CH1 display
            11: CH2 display

        Args:
            *parameters (*[int]): the indices of the parameters to get, separated by commas

        Returns:
            list: the values of the specified parameters
        """

        commandString = "SNAP?" +  " {}," * len(values)
        return self._instrument.query_ascii_values(commandString.format(*values))


    def auto_gain(self):
        """
        Mimics pressing the Auto Gain button. Does nothing if the time
        constant is more than 1 second.
        """
        self._instrument.query_ascii_values("AGAN")


    def auto_reserve(self):
        """
        Mimics pressing the Auto Reserve button.
        """
        self._instrument.query_ascii_values("ARSV")


    def auto_phase(self):
        """
        Mimics pressing the Auto Phase button.
        """
        self._instrument.query_ascii_values("APHS")


    def auto_offset(self, parameter):
        """
        Automatically offsets the given voltage parameter.

        :param parameter: A string from ['x'|'y'|'r'], case insensitive.
        """
        self._instrument.query_ascii_values("AOFF {}".format(parameter.upper()))