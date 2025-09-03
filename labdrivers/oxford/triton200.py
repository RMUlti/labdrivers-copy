import socket

# If you are getting a socket error
# Check that the port is listening by typing in command prompt 'netstat -ona | findstr <port_number>'
# If the port is already established or is otherwise in use, you can end the connection with 'taskkill /F /pid <process_ID>'


class Triton200:
    """
    Create an instance of the Triton200 class.

    Supported modes: IP

    :param str ip_address: The IP address of the Triton 200.
    :param int port_number: The associated port number of the Triton 200 (default: 33576)
    :param int timeout: How long to wait for a response (default: 10000)
    :param int bytes_to_read: How many bytes to accept from the response (default: 2048)
    """

    def __init__(
        self,
        ip_address,
        port_number=33576,
        timeout=10,
        bytes_to_read=2048,
        temperature_channel=5,
    ):
        self._address = (str(ip_address), int(port_number))
        self._timeout = timeout
        self._bytes_to_read = bytes_to_read
        self._temperature_channel = temperature_channel
        self._temperature_setpoint = 0.0
        self._heater_range = 0.0

        self._heater_channel = "1"
        self._turbo_channel = "1"

        # Initialize the socket once
        self._socket = None

    @property
    def temperature_channel(self):
        self._temperature_channel = self.control_channel
        return self._temperature_channel

    @temperature_channel.setter
    def temperature_channel(self, value):
        self._temperature_channel = str(value)
        self.control_channel = value

    def enable_or_disable_channel(self, enab_disab, channel):
        if channel in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]:
            pass
        else:
            RuntimeError("Channel number must be an integer from 1-15.")

        if enab_disab.lower() == "enable":
            command = "SET:DEV:" + str(channel) + ":TEMP:MEAS:ENAB:ON\r\n"
        elif enab_disab.lower() == "disable":
            command = "SET:DEV:" + str(channel) + ":TEMP:MEAS:ENAB:OFF\r\n"
        else:
            raise RuntimeError("You must either 'enable' or 'disable'.")

        response = self.query_and_receive(command)

        if not response:
            raise RuntimeError("Toggling the channel was unsuccessful.")

    @property
    def control_channel(self):
        response = self.query_and_receive("READ:DEV:H1:HTR:LOOP:SENS\r\n")
        return int(response.strip("READ:DEV:H1:HTR:LOOP:SENS").strip("\n"))

    @control_channel.setter
    def control_channel(self, value):
        response = self.query_and_receive(f"SET:DEV:T{value}:TEMP:LOOP:HTR:H1\r\n")
        return response

    @property
    def temperature_setpoint(self):
        noun = f"DEV:T{int(self.temperature_channel)}:TEMP:LOOP:TSET"
        command = "READ:DEV:T" + str(self.temperature_channel) + ":TEMP:LOOP:TSET\r\n"
        response = self.query_and_receive(command)
        return self.extract_value(response, noun, "K")

    @temperature_setpoint.setter
    def temperature_setpoint(self, value):
        if not isinstance(value, float):
            raise RuntimeError("Make sure the temperature set point is a number.")
        elif 0 <= value < 10:
            self._temperature_setpoint = value
            command = (
                "SET:DEV:T"
                + str(self.temperature_channel)
                + ":TEMP:LOOP:TSET:"
                + str(value)
                + "\r\n"
            )
            response = self.query_and_receive(command)
        else:
            print("Keep an eye on the turbo pump if you ramp!!!")
            self._temperature_setpoint = value
        return response

    def check_loop(self):
        while True:
            response = self.query_and_receive(
                f"READ:DEV:T{int(self.temperature_channel)}:TEMP:LOOP:MODE\r\n"
            )
            if "ON" in response:
                state = 1
                break
            elif "OFF" in response:
                state = 0
                break
            else:
                pass
        return state

    def close_loop(self):
        command = "SET:DEV:T" + str(self.temperature_channel) + ":TEMP:LOOP:MODE:ON\r\n"
        response = self.query_and_receive(command)

        if not response:
            raise RuntimeError("Turning on Loop mode was unsuccessful.")

    def open_loop(self):
        command = (
            "SET:DEV:T" + str(self.temperature_channel) + ":TEMP:LOOP:MODE:OFF\r\n"
        )
        response = self.query_and_receive(command)

        if not response:
            raise RuntimeError("Turning off loop mode was unsuccessful.")

    # @property
    def temperature(self, channel):
        noun = "DEV:T" + str(channel) + ":TEMP:SIG:TEMP"
        command = "READ:" + noun + "\r\n"
        response = self.query_and_receive(command)

        return self.extract_value(response, noun, "K")

    def update_heater(self):
        """
        Associates the heater with the current temperature channel and changes the heater current to
        preset values given the temperature set point.
        """
        heater_range = ["0.316", "1", "3.16", "10", "31.6", "100"]
        command = (
            "SET:DEV:T"
            + str(self.temperature_channel)
            + ":TEMP:LOOP:HTR:H"
            + str(self._heater_channel)
            + "\r\n"
        )
        response = self.query_and_receive(command)

        if not response:
            raise RuntimeError("Changing of heater focus unsuccessful.")

        heater_index = (
            (self.temperature_setpoint > 0.030)
            + (self.temperature_setpoint > 0.050)
            + (self.temperature_setpoint > 0.170)
            + (self.temperature_setpoint > 0.240)
            + (self.temperature_setpoint > 1)
        )
        heater_current = heater_range[heater_index]

        command = (
            "SET:DEV:T"
            + str(self.temperature_channel)
            + ":TEMP:LOOP:RANGE:"
            + heater_current
            + "\r\n"
        )
        response = self.query_and_receive(command)

        if not response:
            raise RuntimeError("Changing of heater range unsuccessful.")

    def update_heater_while_V4_open(self):
        """
        Associates the heater with the current temperature channel and changes the heater current to
        preset values given the temperature set point.
        """
        heater_range = ["0.316", "1", "3.16", "10", "31.6", "100"]
        command = (
            "SET:DEV:T"
            + str(self.temperature_channel)
            + ":TEMP:LOOP:HTR:H"
            + str(self._heater_channel)
            + "\r\n"
        )
        response = self.query_and_receive(command)

        if not response:
            raise RuntimeError("Changing of heater focus unsuccessful.")
        heater_index = (
            (self.temperature_setpoint > 0.05)
            + (self.temperature_setpoint > 0.2)
            + (self.temperature_setpoint > 0.5)
            + (self.temperature_setpoint > 1)
            + (self.temperature_setpoint > 10)
        )
        heater_current = heater_range[heater_index]

        command = (
            "SET:DEV:T"
            + str(self.temperature_channel)
            + ":TEMP:LOOP:RANGE:"
            + heater_current
            + "\r\n"
        )
        response = self.query_and_receive(command)

        if not response:
            raise RuntimeError("Changing of heater range unsuccessful.")

    @property
    def ramp_rate(self):
        command = (
            "READ:DEV:T" + str(self.temperature_channel) + ":TEMP:LOOP:RAMP:RATE\r\n"
        )
        response = self.query_and_receive(command)

        if not response:
            raise RuntimeError("Unable to read ramp rate.")

        return float(
            response.strip(
                f"SET:DEV:T" + str(self.temperature_channel) + ":TEMP:LOOP:RAMP:RATE:"
            ).strip("K/min\n")
        )

    @ramp_rate.setter
    def ramp_rate(self, value):
        command = (
            "SET:DEV:T"
            + str(self.temperature_channel)
            + f":TEMP:LOOP:RAMP:RATE: {value}\r\n"
        )
        response = self.query_and_receive(command)

        if not response:
            raise RuntimeError("Unable to set ramp rate.")

    def controlled_ramp_on(self):
        """Starts a temperature sweep for the current temperature channel."""
        command = (
            "SET:DEV:T" + str(self.temperature_channel) + ":TEMP:LOOP:RAMP:ENAB:ON\r\n"
        )
        response = self.query_and_receive(command)

        if not response:
            raise RuntimeError("Enabling of temperature ramp unsuccessful.")

    def controlled_ramp_off(self):
        """Stops a temperature sweep for the current temperature channel."""
        command = (
            "SET:DEV:T" + str(self.temperature_channel) + ":TEMP:LOOP:RAMP:ENAB:OFF\r\n"
        )
        response = self.query_and_receive(command)

        if not response:
            raise RuntimeError("Disabling of temperature ramp unsuccessful.")

    def open_close_toggle_valve(self, valve_num, state):
        if valve_num in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
            pass
        else:
            raise RuntimeError("The valve number can be 1-9.")
        if state in ["OPEN", "CLOSE", "TOGGLE"]:
            pass
        else:
            raise RuntimeError("The valve state can be 'OPEN', 'CLOSE', or 'TOGGLE'.")
        command = (
            "SET:DEV:V" + str(valve_num) + ":VALV:SIG:STATE:" + str(state) + "\r\n"
        )
        response = self.query_and_receive(command)
        if not response:
            raise RuntimeError("The valve state change was unsuccessful.")

    def turbo_on(self):
        """Turns on a turbo pump.

        WARNING: Do not use this unless you know what you are doing."""
        command = "SET:DEV:TURB" + self._turbo_channel + ":PUMP:SIG:STATE:ON\r\n"
        response = self.query_and_receive(command)

        if not response:
            raise RuntimeError("Enabling of turbo pump unsuccessful.")

    def turbo_off(self):
        """Turns off the turbo pump.

        WARNING: Do not use this unless you know what you are doing."""
        command = "SET:DEV:TURB" + self._turbo_channel + ":PUMP:SIG:STATE:OFF\r\n"
        response = self.query_and_receive(command)

        if not response:
            raise RuntimeError("Disabling of turbo pump unsuccessful.")

    def query_and_receive(self, command):
        """
        Queries the Oxford Triton 200 with the given command using the persistent socket.

        :param command: Specifies a read/write of a property.
        """
        self._ensure_socket_open()  # Ensure the socket is open

        # Send the command and receive the response
        self._socket.sendall(command.encode())
        response = self._socket.recv(self._bytes_to_read).decode()

        return response

    @staticmethod
    def extract_value(response, noun, unit):
        expected_response = "STAT:" + noun + ":"
        value = float(
            response.replace(expected_response, "").strip("\n").replace(unit, "")
        )
        return value

    def _ensure_socket_open(self):
        """Ensure the socket is open and connected."""
        if self._socket is None:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.connect(self._address)
            self._socket.settimeout(self._timeout)

    def close_socket(self):
        """Close the socket when done."""
        if self._socket:
            self._socket.close()
            self._socket = None
