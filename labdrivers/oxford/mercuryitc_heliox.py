import socket
import time

import numpy as np
import pyvisa as visa


class mercuryitc_heliox:
    def __init__(
        self,
        mode="visa",
        resource_name=None,
        ip_address=None,
        port=7020,
        timeout=10.0,
        bytes_to_read=1024,
        baudrate=9600,
    ):
        """
        Parameters:
        :param str mode: The connection to the iPS, either 'ip' or 'visa'
        :param str resource_name: VISA resource name of the Mercury iPS
        :param str ip_address: IP address of the Mercury iPS
        :param port: Port number of the Mercury iPS
        :type port: integer
        :param timeout: Time in seconds to wait for command acknowledgment
        :type timeout: float
        :param bytes_to_read: Number of bytes to read from query
        :type bytes_to_read: integer
        """
        self.mode = mode
        self.resource_name = resource_name
        self.resource_manager = visa.ResourceManager()
        self.ip_address = ip_address
        self.port = port
        self.timeout = timeout
        self.bytes_to_read = bytes_to_read
        self.baudrate = baudrate
        supported_modes = ("ip", "visa")
        self.instr = self.resource_manager.open_resource(self.resource_name)

        self.temp_sensor = {"probe_low": "DB8.T1", "VTI": "MB1.T1", "He3Pot": "DB7.T1"}

        if mode.lower().strip() in supported_modes:
            self.mode = mode
        else:
            raise RuntimeError("Mode is not currently supported.")

        if mode == "visa":
            self.instr.baud_rate = self.baudrate

    def query_ip(self, command):
        """Sends a query to the MercuryIPS via ethernet.
        :param command: The command, which should be in the NOUN + VERB format
        :type command: string
        :returns str: The MercuryItc response
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.ip_address, self.port))
            s.settimeout(self.timeout)
            s.sendall(command.encode())
            response = s.recv(self.bytes_to_read).decode()

        return response.decode()

    def query_visa(self, command):
        """Sends a query to the MercuryIPS via VISA.
        :param command: The command, which should be in the VERB + NOUN format
        :type command: string
                :returns str: The MercuryIPS response
        """
        instr = self.resource_manager.open_resource(self.resource_name)
        response = instr.query(command)
        instr.close()

        return response

    @staticmethod
    def extract_value(response, noun, unit):
        """Finds the value that is contained within the response to a previously sent query.

        :param response: The response from a query.
                :type response: string
                :param noun: The part of the query that refers to the NOUN (refer to MercuryIPS documentation).
                :param unit: The measurement unit (e.g. K for Kelvin, T for Tesla).
                :returns float: The value of the response, but without units.
        """
        expected_response = "STAT:" + noun + ":"
        value = float(
            response.replace(expected_response, "").strip("\n").replace(unit, "")
        )
        return value

    # Employing hash tables instead of if-else trees
    QUERY_AND_RECEIVE = {"ip": query_ip, "visa": query_visa}

    def temp(self, sensor):
        """Reads temperature of the temperature sensor.
        :param temp_sensor: Probe(DB8.T1) or VTI(MB0.T1)
        """
        dev = self.temp_sensor[sensor]
        noun = "DEV:" + dev + ":TEMP:SIG:TEMP"
        command = "READ:" + noun
        response = MercuryItc.QUERY_AND_RECEIVE[self.mode](self, command)
        return self.extract_value(response, noun, "K")

    def autoPID(self, sensor, value):
        dev = self.temp_sensor[sensor]
        noun = "DEV:" + dev + ":TEMP:LOOP:ENAB:" + str(value).upper()
        command = "SET:" + noun
        if value.upper() == "ON" or value.upper() == "OFF":
            response = MercuryItc.QUERY_AND_RECEIVE[self.mode](self, command)
        else:
            return 'The argument must be either "on" or "off"'

    def autoFlow(self, sensor, value):
        dev = self.temp_sensor[sensor]
        noun = "DEV:" + dev + ":TEMP:LOOP:FAUT:" + str(value).upper()
        command = "SET:" + noun
        if value.upper() == "ON" or value.upper() == "OFF":
            response = MercuryItc.QUERY_AND_RECEIVE[self.mode](self, command)
        else:
            return 'The argument must be either "on" or "off"'

    def rampmode(self, sensor, value):
        dev = self.temp_sensor[sensor]
        noun = "DEV:" + dev + ":TEMP:LOOP:RENA:" + str(value).upper()
        command = "SET:" + noun
        if value.upper() == "ON" or value.upper() == "OFF":
            response = MercuryItc.QUERY_AND_RECEIVE[self.mode](self, command)
        else:
            return 'The argument must be either "on" or "off"'

    @property
    def ramprate(self):
        noun = "DEV:DB8.T1:TEMP:LOOP:RSET"
        command = "READ:" + noun
        response = MercuryItc.QUERY_AND_RECEIVE[self.mode](self, command)
        return self.extract_value(response, noun, "K/m")

    @ramprate.setter
    def ramprate(self, value):
        noun = "DEV:DB8.T1:TEMP:LOOP:RSET:" + str(value)
        command = "SET:" + noun
        response = MercuryItc.QUERY_AND_RECEIVE[self.mode](self, command)

    @property
    def VTI_temp_setpoint(self):
        dev = self.temp_sensor["VTI"]
        noun = "DEV:" + dev + ":TEMP:LOOP:TSET"
        command = "READ:" + noun
        response = MercuryItc.QUERY_AND_RECEIVE[self.mode](self, command)
        return self.extract_value(response, noun, "K")

    @VTI_temp_setpoint.setter
    def VTI_temp_setpoint(self, value):
        dev = self.temp_sensor["VTI"]
        noun = "DEV:" + dev + ":TEMP:LOOP:TSET:" + str(value)
        command = "SET:" + noun
        if 0 <= value <= 300:
            response = MercuryItc.QUERY_AND_RECEIVE[self.mode](self, command)
        else:
            return "Temperature range must be between 0 and 300 K"

    @property
    def probe_temp_setpoint(self):
        dev = self.temp_sensor["probe"]
        noun = "DEV:" + dev + ":TEMP:LOOP:TSET"
        command = "READ:" + noun
        response = MercuryItc.QUERY_AND_RECEIVE[self.mode](self, command)
        return self.extract_value(response, noun, "K")

    @probe_temp_setpoint.setter
    def probe_temp_setpoint(self, value):
        dev = self.temp_sensor["probe"]
        noun = "DEV:" + dev + ":TEMP:LOOP:TSET:" + str(value)
        command = "SET:" + noun
        if 0 <= value <= 300:
            response = MercuryItc.QUERY_AND_RECEIVE[self.mode](self, command)
        else:
            return "Temperature range must be between 0 and 300 K"

    @property
    def probe_temp_ramprate(self):
        dev = self.temp_sensor["probe"]
        noun = "DEV:" + dev + ":TEMP:LOOP:RSET"
        command = "READ:" + noun
        response = MercuryItc.QUERY_AND_RECEIVE[self.mode](self, command)
        return self.extract_value(response, noun, "K/m")

    @probe_temp_ramprate.setter
    def probe_temp_ramprate(self, sensor, value):
        dev = self.temp_sensor["probe"]
        noun = "DEV:" + dev + ":TEMP:LOOP:RSET:" + str(value)
        command = "SET:" + noun
        if 0 <= value:
            response = MercuryItc.QUERY_AND_RECEIVE[self.mode](self, command)
        else:
            return "Ramp rate has to be a positive number"

    @property
    def pressure(self):
        noun = "DEV:DB5.P1:PRES:LOOP:PRST"
        command = "READ:" + noun
        response = MercuryItc.QUERY_AND_RECEIVE[self.mode](self, command)
        return self.extract_value(response, noun, "mB")

    @pressure.setter
    def pressure(self, value):
        noun = "DEV:DB5.P1:PRES:LOOP:PRST:" + str(value)
        command = "SET:" + noun
        response = MercuryItc.QUERY_AND_RECEIVE[self.mode](self, command)

    def pressure_now(self):
        noun = "DEV:DB5.P1:PRES:SIG:PRES"
        command = "READ:" + noun
        response = MercuryItc.QUERY_AND_RECEIVE[self.mode](self, command)
        return self.extract_value(response, noun, "mB")

    @property
    def pressure_auto_flow(self):
        noun = "DEV:DB5.P1:PRES:LOOP:FAUT"
        command = "READ:" + noun
        response = MercuryItc.QUERY_AND_RECEIVE[self.mode](self, command)
        return response.replace("STAT:DEV:DB5.P1:PRES:LOOP:FAUT:", "").replace("\n", "")

    @pressure_auto_flow.setter
    def pressure_auto_flow(self, input):
        noun = "DEV:DB5.P1:PRES:LOOP:FAUT:"
        command = "SET:" + noun + input
        if input in ["OFF", "ON"]:
            response = MercuryItc.QUERY_AND_RECEIVE[self.mode](self, command)
        else:
            raise RuntimeError("Pressure autoflow can be either 'ON' or 'OFF'.")

    @property
    def pressure_flow(self):
        noun = "DEV:DB5.P1:PRES:LOOP:FSET"
        command = "READ:" + noun
        response = MercuryItc.QUERY_AND_RECEIVE[self.mode](self, command)
        return float(
            response.replace("STAT:DEV:DB5.P1:PRES:LOOP:FSET:", "").replace("\n", "")
        )

    @pressure_flow.setter
    def pressure_flow(self, input):
        noun = "DEV:DB5.P1:PRES:LOOP:FSET:"
        command = "SET:" + noun + str(input)
        if 0 <= input <= 100:
            if self.pressure_auto_flow == "OFF":
                response = MercuryItc.QUERY_AND_RECEIVE[self.mode](self, command)
            else:
                self.pressure_auto_flow = "OFF"
                response = MercuryItc.QUERY_AND_RECEIVE[self.mode](self, command)
                print("Pressure auto flow has been turned 'OFF'.")
        else:
            raise RuntimeError("Manual flow percentage can be between 0 and 100.")

    def wait_for_temp(self, sensor, value):
        dev = self.temp_sensor[sensor]
        there_yet = False
        T_avg = []
        while not there_yet:
            T_avg.append(self.temp(sensor))
            time.sleep(0.2)
            if (
                abs(np.average(T_avg[-50:]) - value) < value * 2e-4
                and np.var(T_avg[-50:]) < value * 1e-5
            ):
                there_yet = True
