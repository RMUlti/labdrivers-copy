import socket
import time

import pyvisa as visa


class MercuryIps_Teslatron:

    def __init__(
        self,
        mode="visa",
        port=7020,
        resource_name=None,
        ip_address=None,
        timeout=10.0,
        bytes_to_read=2048,
        baudrate=9600,
    ):

        self.mode = mode
        self.resource_name = resource_name
        self.resource_manager = visa.ResourceManager()
        self.ip_address = ip_address
        self.port = port
        self.timeout = timeout
        self.bytes_to_read = bytes_to_read
        self.baudrate = baudrate
        self.instr = self.resource_manager.open_resource(self.resource_name)
        supported_modes = ("ip", "visa")
        if mode.lower().strip() in supported_modes:
            self.mode = mode
        else:
            raise RuntimeError("Mode is not currently supported.")

        if mode == "visa":
            self.instr.baud_rate = self.baudrate

    ###################
    # Query functions #
    ####################

    def query_ip(self, command):
        """Sends a query to the MercuryIps_Teslatron via ethernet.

        :param command: The command, which should be in the NOUN + VERB format
        :type command: string
        :returns str: The MercuryIps_Teslatron response
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.ip_address, self.port))
            s.settimeout(self.timeout)
            s.sendall(command.encode())
            response = s.recv(self.bytes_to_read).decode()

        return response.decode()

    def query_visa(self, command):
        """Sends a query to the MercuryIps_Teslatron via VISA.

        :param command: The command, which should be in the NOUN + VERB format
        :type command: string
        :returns str: The MercuryIps_Teslatron response
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
        :param noun: The part of the query that refers to the NOUN (refer to MercuryIps_Teslatron documentation).
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

    @property
    def field_setpoint(self):
        """The magnetic field set point in Tesla"""
        noun = "DEV:GRPZ:PSU:SIG:FSET"
        command = "READ:" + noun
        response = MercuryIps_Teslatron.QUERY_AND_RECEIVE[self.mode](self, command)
        return self.extract_value(response, noun, "T")

    @field_setpoint.setter
    def field_setpoint(self, value):
        if -12 <= value <= 12:
            setpoint = str(value)
            command = "SET:DEV:GRPZ:PSU:SIG:FSET:" + setpoint
            response = MercuryIps_Teslatron.QUERY_AND_RECEIVE[self.mode](self, command)

            if not response:
                raise RuntimeWarning(
                    "No response from the MercuryIps_Teslatron after querying the field setpoint."
                )
        else:
            raise RuntimeError("The setpoint must be within the proper limits. (+-12T)")

    @property
    def field_ramp_rate(self):
        """The magnetic field ramp rate in Tesla per minute along the magnet axis."""
        noun = "DEV:" + "GRPZ" + ":PSU:SIG:RFST"
        command = "READ:" + noun
        response = MercuryIps_Teslatron.QUERY_AND_RECEIVE[self.mode](self, command)
        return self.extract_value(response, noun, "T/m")

    @field_ramp_rate.setter
    def field_ramp_rate(self, value):
        ramp_rate = str(value)
        command = "SET:DEV:GRPZ:PSU:SIG:RFST:" + ramp_rate
        response = MercuryIps_Teslatron.QUERY_AND_RECEIVE[self.mode](self, command)

        if not response:
            raise RuntimeWarning("No response after setting a field ramp rate.")

    @property
    def current_setpoint(self):
        """The set point of the current for a magnet in Amperes."""
        noun = "DEV:GRPZ:PSU:SIG:CSET"
        command = "READ:" + noun
        response = MercuryIps_Teslatron.QUERY_AND_RECEIVE[self.mode](self, command)
        return self.extract_value(response, noun, "A")

    @current_setpoint.setter
    def current_setpoint(self, value):
        setpoint = str(value)
        command = "SET:DEV:GRPZ:PSU:SIG:CSET" + setpoint
        response = MercuryIps_Teslatron.QUERY_AND_RECEIVE[self.mode](self, command)

        if not response:
            raise RuntimeWarning("No response after setting current set point.")

    @property
    def current_ramp_rate(self):
        """The ramp rate of the current for a magnet in Amperes per minute."""
        noun = "DEV:GRPZ:PSU:SIG:RCST"
        command = "READ:" + noun
        response = MercuryIps_Teslatron.QUERY_AND_RECEIVE[self.mode](self, command)
        return self.extract_value(response, noun, "A/m")

    @current_ramp_rate.setter
    def current_ramp_rate(self, value):
        ramp_rate = str(value)
        command = "SET:DEV:GRPZ:PSU:SIG:RCST" + ramp_rate
        response = MercuryIps_Teslatron.QUERY_AND_RECEIVE[self.mode](self, command)

        if not response:
            raise RuntimeWarning("No response after setting current ramp rate.")

    @property
    def magnetic_field(self):
        """Gets the magnetic field (current) that the iPS is outputting."""
        noun = "DEV:GRPZ:PSU:SIG:FLD"
        command = "READ:" + noun
        response = MercuryIps_Teslatron.QUERY_AND_RECEIVE[self.mode](self, command)
        return self.extract_value(response, noun, "T")

    @property
    def persistent_magnetic_field(self):
        """Gets the physical magnetic field from the magnet itself."""
        noun = "DEV:GRPZ:PSU:SIG:PFLD"
        command = "READ:" + noun
        response = MercuryIps_Teslatron.QUERY_AND_RECEIVE[self.mode](self, command)
        return self.extract_value(response, noun, "T")

    def status(self):
        noun = "DEV:GRPZ:PSU:SIG:ACTN:"
        command = "READ:" + noun
        response = MercuryIps_Teslatron.QUERY_AND_RECEIVE[self.mode](self, command)
        return response.replace("STAT:" + noun, "").strip("\n")

    @property
    def switch_heater(self):
        noun = "DEV:GRPZ:PSU:SIG:SWHT"
        command = "READ:" + noun
        response = MercuryIps_Teslatron.QUERY_AND_RECEIVE[self.mode](self, command)
        return response.replace("STAT:" + noun + ":", "").strip("\n")

    @switch_heater.setter
    def switch_heater(self, value):
        value == str.upper(value)
        if value == "ON" or value == "OFF":
            command = "SET:DEV:GRPZ:PSU:SIG:SWHT:" + value
            response = MercuryIps_Teslatron.QUERY_AND_RECEIVE[self.mode](self, command)
        else:
            raise RuntimeError("The input has to be 'on' or 'off'")

    def persistent_mode(self, value):
        value == str.upper(value)
        if value == "ON":
            self.switch_heater = "OFF"
            print(f"Waiting for the switch heater to turn off and cool.")
            time.sleep(600)
            self.ramp_to_zero()
            print("Waiting for the iPS current to ramp to zero.")
            time.sleep(1)
            holding = False
            while not holding:
                if self.holding() == True:
                    break
                else:
                    time.sleep(1)
            print(
                f"The magnet is now in persistent mode at {self.magnetic_field} T, keep track of the temperature and field."
            )
        if value == "OFF":
            current_field = self.persistent_magnetic_field
            self.ramp_to_setpoint(current_field)
            print(
                "Waiting for the power supply to ramp to the same field/current as the magnet."
            )
            time.sleep(1)
            holding = False
            while not holding:
                if self.holding() == True:
                    break
                else:
                    time.sleep(1)
            self.switch_heater = "ON"
            print(f"Waiting for the switch heater to turn on and warm.")
            time.sleep(600)
            print(
                f"The magnet is no longer in persistent mode, and is at {self.magnetic_field} T."
            )
        else:
            raise RuntimeError("The input has to be 'on' or 'off'.")

    def ramp_to_setpoint(self):
        """Ramps a magnet to the setpoint."""
        noun = "DEV:GRPZ:PSU:ACTN:RTOS"
        command = "SET:" + noun
        while (
            MercuryIps_Teslatron.QUERY_AND_RECEIVE[self.mode](self, command)
            .replace("STAT:SET:" + noun + ":", "")
            .strip("\n")
            == "NOT_RDY"
        ):
            time.sleep(5)

    def ramp_to_zero(self):
        """Ramps a magnet from its current magnetic field to zero field."""
        noun = "DEV:GRPZ:PSU:ACTN:RTOZ"
        command = "SET:" + noun
        while (
            MercuryIps_Teslatron.QUERY_AND_RECEIVE[self.mode](self, command)
            .replace("STAT:SET:" + noun + ":", "")
            .strip("\n")
            == "NOT_RDY"
        ):
            time.sleep(5)

    def ramping(self):
        """Queries if magnet is ramping."""
        # ask if ramping to zero
        # command = 'READ:DEV:' + 'GRPZ' + ':PSU:ACTN:RTOZ\n'
        # ask if ramping to set
        # command = 'READ:DEV:' + 'GRPZ' + ':PSU:ACTN:RTOS\n'
        # TODO: find out what kind of response you expect
        pass

    def hold(self):
        """Puts a magnet in a HOLD state.

        This action does one of the following:
        1) Stops a ramp
        2) Allows the field and current to ramp
        """
        command = "SET:DEV:" + "GRPZ" + ":PSU:ACTN:HOLD"
        response = MercuryIps_Teslatron.QUERY_AND_RECEIVE[self.mode](self, command)

        if not response:
            raise RuntimeWarning("No response after telling Mercury iPS to hold.")

    def holding(self):
        """Queries if magnet is in a HOLD state."""
        command = "READ:DEV:GRPZ:PSU:ACTN"
        response = MercuryIps_Teslatron.QUERY_AND_RECEIVE[self.mode](self, command)
        # TODO: find out what kind of response you expect
        if response == "STAT:DEV:GRPZ:PSU:ACTN:HOLD\n":
            return True
        else:
            return False

    def clamp(self):
        """Puts a magnet in a CLAMP state."""
        command = "SET:DEV:GRPZ:PSU:ACTN:CLMP"
        response = MercuryIps_Teslatron.QUERY_AND_RECEIVE[self.mode](self, command)

        if not response:
            raise RuntimeWarning("No response after telling Mercury iPS to clamp.")

    def clamped(self):
        """Queries if magnet is in a CLAMP state."""
        # command = 'READ:DEV:GRPZ:PSU:ACTN:CLMP'
        # response = MercuryIps_Teslatron.QUERY_AND_RECEIVE[self.mode](self, command)
        # TODO: find out what kind of response you expect
        pass

    def magnet_temp(self):
        """Reads magnet temperature"""
        noun = "DEV:MB1.T1:TEMP:SIG:TEMP"
        command = "READ:" + noun
        response = MercuryIps_Teslatron.QUERY_AND_RECEIVE[self.mode](self, command)
        return self.extract_value(response, noun, "K")

    def pt2_temp(self):
        """Reads magnet temperature"""
        noun = "DEV:DB7.T1:TEMP:SIG:TEMP"
        command = "READ:" + noun
        response = MercuryIps_Teslatron.QUERY_AND_RECEIVE[self.mode](self, command)
        return self.extract_value(response, noun, "K")

    def pt1_temp(self):
        """Reads magnet temperature"""
        noun = "DEV:DB8.T1:TEMP:SIG:TEMP"
        command = "READ:" + noun
        response = MercuryIps_Teslatron.QUERY_AND_RECEIVE[self.mode](self, command)
        return self.extract_value(response, noun, "K")

    def circle_sweep(self, field_radius, number_points):
        pass

    def clear_buffer():
        """Clears the iPS buffer in case of issues with communication."""
