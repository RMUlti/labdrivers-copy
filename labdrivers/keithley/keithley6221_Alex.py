import time

import numpy as np
import pyvisa as visa
from retry import retry


class Keithley6221:
    def __init__(self, gpib_addr):
        """
        Constructor for Keithley 6221

        :param gpib_addr: GPIB address (configured on Keithley 6221)
        """
        self._gpib_addr = str(gpib_addr)
        self._resource_manager = visa.ResourceManager()
        self._instrument = self._resource_manager.open_resource(
            "GPIB::{}".format(self.gpib_addr)
        )
        self._instrument.write("FORM:SREG ASC")

    def name(self):
        ans = self._instrument.query("*IDN?")
        return ans

    @retry(tries=10, delay=5)
    def retry_event_status(self):
        return int(self._instrument.query("STAT:OPER:EVEN?").strip("\n"))

    def clear_buffer(self):
        self._instrument.write("*CLS")

    def gpib_addr_query(self):
        """Returns the queried GPIB address of the Keithley 6221."""
        ans = self._instrument.query("SYST:COMM:GPIB:ADDR?").strip()
        return int(self._gpib_addr)

    @property
    def gpib_addr(self):
        """Returns the GPIB address of the Keithley 6221."""
        return int(self._gpib_addr)

    @property
    def output(self):
        ans = self._instrument.query("OUTP:STAT?").strip()
        if ans == 0:
            return "Off"
        elif ans == 1:
            return "True"
        else:
            return "Error"

    @output.setter
    def output(self, state):
        if state == 0 or state == False or str(state).lower() == "off":
            self._instrument.write(f"OUTP:STAT {0}")
        elif state == 1 or state == True or str(state).lower() == "on":
            self._instrument.write(f"OUTP:STAT {1}")
        else:
            raise RuntimeError(
                "The output can either be 0 (False, 'Off') or 1 (True, 'On')."
            )

    @property
    def wave_amplitude(self):
        ans = self._instrument.query("SOUR:WAVE:AMPL?").strip()
        return float(ans)

    @wave_amplitude.setter
    def wave_amplitude(self, amp):
        if 2e-12 <= float(amp) <= 105e-3:
            self._instrument.write(f"SOUR:WAVE:AMPL {amp}")
        else:
            raise RuntimeError(
                "The wave amplitude must be a number between 2E-12 A 105E-3 A."
            )

    @property
    def wave_offset(self):
        ans = self._instrument.query("SOUR:WAVE:OFFS?").strip()
        return float(ans)

    @wave_offset.setter
    def wave_offset(self, offset):
        if -103e-3 <= float(offset) <= 103e-3:
            self._instrument.write(f"SOUR:WAVE:OFFS {offset}")
        else:
            raise RuntimeError(
                "The wave offset must be a number within \u00B1103E-3 A."
            )

    def ramp_wave_offset(self, offset, n_step=1001, sleep_time=0.01):
        if -103e-3 <= float(offset) <= 103e-3:
            startpoint = self._instrument.query("SOUR:WAVE:OFFS?").strip()
            value_list = np.linspace(float(startpoint), float(offset), n_step)
            for value in value_list:
                time.sleep(sleep_time)
                self._instrument.write(f"SOUR:WAVE:OFFS {value}")
        else:
            raise RuntimeError(
                "The wave offset must be a number within \u00B1103E-3 A."
            )

    @property
    def range(self):
        ans = self._instrument.query("SOUR:CURR:RANG?").strip()
        return ans

    @range.setter
    def range(self, value):
        if -105e-3 <= value <= 105e-3:
            self._instrument.write(f"SOUR:CURR:RANG {value}")
        else:
            raise RuntimeError("The output range can be within \u00B1105E-3 A.")

    @property
    def wave_range(self):
        ans = self._instrument.query("SOUR:WAVE:RANG?").strip()
        return ans

    @wave_range.setter
    def wave_range(self, value):
        if value.lower() == "best":
            self._instrument.write(f"SOUR:WAVE:RANG BEST")
        elif value.lower() == "fixed":
            self._instrument.write(f"SOUR:WAVE:RANG FIX")
        else:
            raise RuntimeError("The wave range can be either 'Best' or 'Fixed'.")

    @property
    def wave_arm(self):
        ans = self._instrument.query("SOUR:WAVE:ARM?").strip()
        if int(ans) == 0:
            arm_stat = "Not Armed"
        elif int(ans) == 1:
            arm_stat = "Armed"
        return arm_stat

    @wave_arm.setter
    def wave_arm(self, arm_stat):
        if arm_stat == True:
            self._instrument.write("SOUR:WAVE:ARM")
        elif arm_stat == False:
            self._instrument.write("SOUR:WAVE:ABOR")
        else:
            return "Armed status can either be True or False."

    @property
    def wave_freq(self):
        ans = self._instrument.query("SOUR:WAVE:FREQ?").strip()
        return float(ans)

    @wave_freq.setter
    def wave_freq(self, freq):
        if 1e-3 <= freq <= 1e5:
            self._instrument.write(f"SOUR:WAVE:FREQ {freq}")
        else:
            return "Armed status must be a number from 1E-3 Hz to 1E5 Hz."

    @property
    def compliance(self):
        ans = self._instrument.query("SOUR:CURR:COMP?").strip()
        return float(ans)

    @compliance.setter
    def compliance(self, comp):
        if 0.1 <= float(comp) <= 105:
            self._instrument.write(f"SOUR:CURR:COMP {comp}")
        else:
            raise RuntimeError("The compliance must be a number from 0.1 V to 105 V.")

    def within_compliance(self):
        ans = self._instrument.query("STAT:MEAS?").strip()
        if int(ans) != 0:
            return f"Something is wrong, ASCII error code is {ans}."
        else:
            pass

    def press_TRIG(self):
        self._instrument.write(f"SYST:KEY 13")

    def press_EXIT(self):
        self._instrument.write(f"SYST:KEY 11")

    def phase_marker(self, state, level=180, line=None):
        if state == 0 or state == 1:
            self._instrument.write(f"SOUR:WAVE:PMAR:STAT {state}")
        else:
            raise RuntimeError(
                "The phase marker state can either be 0 (off) or 1 (on)."
            )
        if 0 <= level <= 360:
            self._instrument.write(f"SOUR:WAVE:PMAR:LEV {level}")
        else:
            raise RuntimeError(
                "The phase marker level can either be between 0 and 360."
            )
        if line in [1, 2, 3, 4, 5, 6]:
            self._instrument.write(f"SOUR:WAVE:PMAR:OLIN {line}")
        elif line == None:
            pass
        else:
            raise RuntimeError(
                "The phase marker can output on trigger link lines 1,2,3,4,5,6."
            )

    def filter_on(self, count=10, type="repeating"):
        self.filter_off()
        if type == "repeating":
            self._instrument.write(f"SENS:AVER:TCON REP")
        elif type == "moving":
            self._instrument.write(f"SENS:AVER:TCON MOV")
        else:
            raise RuntimeError("The averaging type can be 'moving' or 'repeating'.")
        if 2 <= count <= 300:
            self._instrument.write(f"SENS:AVER:COUN {count}")
        else:
            raise RuntimeError("The filter count must be between 2 and 300.")
        self._instrument.write(f"SENS:AVER ON")

    def filter_off(self):
        self._instrument.write(f"SENS:AVER OFF")

    def differential_conductance_sweep(
        self,
        start,
        stop,
        step,
        delta,
        delay=0.05,
        counts=1,
        comp_abort=0,
        receive_data=True,
        include_currents=True,
        include_time=False,
    ):
        self._instrument.write(f"SOUR:SWE:ABOR")
        nanovoltmeter_present = self._instrument.query(f"SOUR:DCON:NVPR?").strip()
        if nanovoltmeter_present == "0":
            raise RuntimeError("The 2182 nanovoltmeter is not detected.")
        elif nanovoltmeter_present == "1":
            pass
        else:
            raise RuntimeError(
                f"There is likely a configuration or connection error. The state of the nanovoltmeter is {nanovoltmeter_present}."
            )
        if -105e-3 <= start <= 105e-3:
            self._instrument.write(f"SOUR:DCON:STAR {start}")
        else:
            raise RuntimeError(
                "The starting current must be between -105E-3 amps and 105E-3 amps."
            )
        if -105e-3 <= stop <= 105e-3:
            self._instrument.write(f"SOUR:DCON:STOP {stop}")
        else:
            raise RuntimeError(
                "The stopping current must be between -105E-3 amps and 105E-3 amps."
            )
        if 0 < step <= 105e-3:
            self._instrument.write(f"SOUR:DCON:STEP {step}")
        else:
            raise RuntimeError(
                "The current step size must be between 0 amps and 105E-3 amps."
            )
        if 0 < delta <= 105e-3:
            self._instrument.write(f"SOUR:DCON:DELT {delta}")
        else:
            raise RuntimeError(
                "The current delta size must be between 0 amps and 105E-3 amps."
            )
        if 1e-3 <= delay <= 9999.999:
            self._instrument.write(f"SOUR:DCON:DEL {delay}")
        else:
            raise RuntimeError(
                "The delay time must be between 1E-3 seconds and 9999.999 seconds."
            )
        if comp_abort == 0:
            self._instrument.write(f"SOUR:DCON:CAB OFF")
        elif comp_abort == 1:
            self._instrument.write(f"SOUR:DCON:CAB ON")
        else:
            raise RuntimeError("Compliance abort must be either 0 (OFF) or 1 (ON).")
        if counts == 1:
            self.filter_off()
        elif 2 <= counts <= 300:
            self.filter_on(count=counts)
        else:
            raise RuntimeError("The filter count must be between 2 and 300.")
        self._instrument.write(f"SOUR:DCON:ARM")
        time.sleep(0.1)
        self._instrument.write(f"INIT:IMM")
        time.sleep(3)

        if receive_data == True:
            while True:
                if int(self._instrument.query("STAT:OPER:EVEN?").strip("\n")) != 0:
                    time.sleep(1)
                else:
                    break
            data = np.fromstring(self._instrument.query(f"TRAC:DATA?"), sep=",\t")
            measurement_data = data[0::2]
            time_data = data[1::2]
            if include_currents == True:
                currents = np.arange(start, stop + step, step)
                if len(currents) > len(measurement_data):
                    currents = currents[:-1]
                elif len(measurement_data) > len(currents):
                    measurement_data = measurement_data[:-1]
            returning_data = [measurement_data]
            if include_currents == True:
                returning_data.append(currents)
            if include_time == True:
                returning_data.append(time_data)
            self._instrument.write(f"SOUR:SWE:ABOR")
            return np.array(returning_data)
        elif receive_data == False:
            pass
        else:
            raise RuntimeError("The receive_data parameter is set incorrectly.")

    def delta_measurement(
        self,
        high,
        low,
        delay=0.005,
        counts=1,
        num_cyc=1,
        comp_abort=1,
        receive_data=True,
    ):
        self._instrument.write(f"SOUR:SWE:ABOR")
        nanovoltmeter_present = self._instrument.query(f"SOUR:DELT:NVPR?").strip()
        if nanovoltmeter_present == "0":
            raise RuntimeError("The 2182 nanovoltmeter is not detected.")
        elif nanovoltmeter_present == "1":
            pass
        else:
            raise RuntimeError(
                f"There is likely a configuration or connection error. The state of the nanovoltmeter is {nanovoltmeter_present}."
            )
        if 0 <= high <= 105e-3:
            self._instrument.write(f"SOUR:DELT:HIGH {high}")
        else:
            raise RuntimeError(
                "The starting current must be between 0 amps and 105E-3 amps."
            )
        if -105e-3 <= low <= 0:
            self._instrument.write(f"SOUR:DELT:LOW {low}")
        else:
            raise RuntimeError(
                "The stopping current must be between -105E-3 amps and 0 amps."
            )
        if (isinstance(delay, float) and 0 <= delay <= 9999.999) or delay == "INF":
            self._instrument.write(f"SOUR:DELT:DEL {delay}")
        else:
            raise RuntimeError(
                "The delay time must be between 1E-3 seconds and 9999.999 seconds, or be INF."
            )
        if (isinstance(num_cyc, int) and 1 <= num_cyc <= 65536) or num_cyc == "INF":
            self._instrument.write(f"SOUR:DELT:COUN {num_cyc}")
        else:
            raise RuntimeError(
                "The number of cycles must be between 1 and 65536, or be INF."
            )
        if comp_abort == 0:
            self._instrument.write(f"SOUR:DELT:CAB OFF")
        elif comp_abort == 1:
            self._instrument.write(f"SOUR:DELT:CAB ON")
        else:
            raise RuntimeError("Compliance abort must be either 0 (OFF) or 1 (ON).")
        if counts == 1:
            self.filter_off()
        elif 2 <= counts <= 300:
            self.filter_on(count=counts)
        else:
            raise RuntimeError("The filter count must be between 2 and 300.")
        self._instrument.write(f"SOUR:DELT:ARM")
        time.sleep(1)
        self._instrument.write(f"INIT:IMM")

        if receive_data == True:
            while True:
                if self.retry_event_status() != 0:
                    time.sleep(1)
                else:
                    break
            data = np.fromstring(self._instrument.query(f"TRAC:DATA?"), sep=",\t")
            measurement_data = data[0::2]
            self._instrument.write(f"SOUR:SWE:ABOR")
            return np.array(measurement_data)
        elif receive_data == False:
            pass
        else:
            raise RuntimeError("The receive_data parameter is set incorrectly.")

    def pulse_delta_measurement(
        self,
        high,
        low,
        pulse_width=200e-6,
        pulse_delay=16e-6,
        count=1,
        pulse_interval=5,
        receive_data=True,
    ):
        self._instrument.write(f"SOUR:SWE:ABOR")
        self._instrument.write(f"SOUR:PDEL:SWE OFF")
        nanovoltmeter_present = self._instrument.query(f"SOUR:PDEL:NVPR?").strip()
        if nanovoltmeter_present == "0":
            raise RuntimeError("The 2182 nanovoltmeter is not detected.")
        elif nanovoltmeter_present == "1":
            pass
        else:
            raise RuntimeError(
                f"There is likely a configuration or connection error. The state of the nanovoltmeter is {nanovoltmeter_present}."
            )
        if -105e-3 <= high <= 105e-3:
            self._instrument.write(f"SOUR:PDEL:HIGH {high}")
        else:
            raise RuntimeError(
                "The high current must be between -105e-3 amps and 105E-3 amps."
            )
        if -105e-3 <= low <= 105e-3:
            self._instrument.write(f"SOUR:PDEL:LOW {low}")
        else:
            raise RuntimeError(
                "The low current must be between -105E-3 amps and 105E-3 amps."
            )
        if 50e-6 <= pulse_width <= 12e-3:
            self._instrument.write(f"SOUR:PDEL:WIDT {pulse_width}")
        else:
            raise RuntimeError(
                "The pulse width must be between 50E-6 seconds and 12E-3 seconds."
            )
        if 16e-6 <= pulse_delay <= 11.996e-3:
            self._instrument.write(f"SOUR:PDEL:SDEL {pulse_delay}")
        else:
            raise RuntimeError(
                "The pulse delay must be between 16E-6 seconds and 11.996E-3 seconds."
            )
        if (
            isinstance(count, (int, np.int32, np.int64)) and 1 <= count <= 65536
        ) or count == "INF":
            self._instrument.write(f"SOUR:PDEL:COUN {count}")
            self._instrument.write(f"TRAC:POIN {count}")
        else:
            raise RuntimeError(
                f"The count must be between 1 and 65536 or be INF. You input {count} which is {type(count)}."
            )
        if 5 <= pulse_interval <= 999999 and isinstance(pulse_interval, int):
            self._instrument.write(f"SOUR:PDEL:INT {pulse_interval}")
        else:
            raise RuntimeError(
                "The pulse interval must be an integer between 5 and 999999."
            )
        self._instrument.write(f"SOUR:PDEL:ARM")
        time.sleep(1)
        self._instrument.write(f"INIT:IMM")

        if receive_data == True:
            while True:
                if self.retry_event_status() != 0:
                    time.sleep(1)
                else:
                    break
            data = np.fromstring(self._instrument.query(f"TRAC:DATA?"), sep=",\t")
            measurement_data = data[0::2]
            self._instrument.write(f"SOUR:SWE:ABOR")
            return np.array(measurement_data)
        elif receive_data == False:
            pass
        else:
            raise RuntimeError("The receive_data parameter is set incorrectly.")

    def pulse_delta_sweep(
        #### NOT FINISHED ####
        self,
        start,
        stop,
        step=None,
        pulse_width=100e-3,
        pulse_delay=100e-6,
        count=1,
    ):
        if step == None:
            step = abs(stop - start) / 50
        self._instrument.write(f"SOUR:SWE:ABOR")
        self._instrument.write(f"SOUR:PDEL:SWE OFF")
        nanovoltmeter_present = self._instrument.query(f"SOUR:PDEL:NVPR?").strip()
        if nanovoltmeter_present == "0":
            raise RuntimeError("The 2182 nanovoltmeter is not detected.")
        elif nanovoltmeter_present == "1":
            pass
        else:
            raise RuntimeError(
                f"There is likely a configuration or connection error. The state of the nanovoltmeter is {nanovoltmeter_present}."
            )
        if -105e-3 <= start <= 105e-3:
            self._instrument.write(f"SOUR:PDEL:LOW {start}")
        else:
            raise RuntimeError(
                "The starting current must be between -105e-3 amps and 105E-3 amps."
            )
        if -105e-3 <= stop <= 105e-3:
            self._instrument.write(f"SOUR:PDEL:HIGH {stop}")
        else:
            raise RuntimeError(
                "The stopping current must be between -105E-3 amps and 105E-3 amps."
            )
        if 50e-6 <= pulse_width <= 12e-3:
            self._instrument.write(f"SOUR:PDEL:WIDT {pulse_width}")
        else:
            raise RuntimeError(
                "The stopping current must be between 50E-6 seconds and 12E-3 seconds."
            )
        if 16e-6 <= pulse_delay <= 11.996e-3:
            self._instrument.write(f"SOUR:PDEL:SDEL {pulse_delay}")
        else:
            raise RuntimeError(
                "The stopping current must be between 16E-6 seconds and 11.996E-3 seconds."
            )
        if 16e-6 <= pulse_delay <= 11.996e-3:
            self._instrument.write(f"SOUR:PDEL:SDEL {pulse_delay}")
        else:
            raise RuntimeError(
                "The stopping current must be between 16E-6 seconds and 11.996E-3 seconds."
            )
        if (isinstance(count, int) and 1 <= count <= 65536) or count == "INF":
            self._instrument.write(f"SOUR:SWE:COUN {count}")
        else:
            raise RuntimeError("The count must be between 1 and 65536 or be INF.")
        self._instrument.write(f"SOUR:PDEL:SWE ON")
        self._instrument.write(f"SOUR:SWE:SPAC LIN")
        self._instrument.write(f"SOUR:CURR:STAR {start}")
        self._instrument.write(f"SOUR:CURR:STOP {stop}")
        self._instrument.write(f"SOUR:CURR:STEP {step}")
        self._instrument.write(f"SOUR:PDEL:ARM")

    def quick_measure(self):
        high = 1e-6
        low = -1e-6
        delay = 0.005
        counts = 5
        num_cyc = 5
        self._instrument.write(f"SOUR:SWE:ABOR")
        nanovoltmeter_present = self._instrument.query(f"SOUR:DELT:NVPR?").strip()
        if nanovoltmeter_present == "0":
            raise RuntimeError("The 2182 nanovoltmeter is not detected.")
        elif nanovoltmeter_present == "1":
            pass
        else:
            raise RuntimeError(
                f"There is likely a configuration or connection error. The state of the nanovoltmeter is {nanovoltmeter_present}."
            )
        self._instrument.write(f"SOUR:SWE:COUN 1")
        self._instrument.write(f"SOUR:DELT:HIGH {high}")
        self._instrument.write(f"SOUR:DELT:LOW {low}")
        self._instrument.write(f"SOUR:DELT:DEL {delay}")
        self._instrument.write(f"SOUR:DELT:COUN {num_cyc}")
        self._instrument.write(f"SOUR:DELT:CAB ON")
        self.filter_on(count=counts)
        self._instrument.write(f"SOUR:DELT:ARM")
        self._instrument.write(f"INIT:IMM")

        while True:
            if self.retry_event_status() != 0:
                time.sleep(1)
            else:
                break
        data = np.fromstring(self._instrument.query(f"TRAC:DATA?"), sep=",\t")
        measurement_data = data[0::2]
        self._instrument.write(f"SOUR:SWE:ABOR")
        return np.array(measurement_data)
