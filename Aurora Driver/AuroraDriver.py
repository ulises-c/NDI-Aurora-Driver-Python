import serial
from serial.tools import list_ports
import binascii
import platform

from AuroraErrorCodes import error_codes_dict
from AuroraPortStatus import port_status_dict

class NDI_Aurora:
    # Section 1
    # Functions in this section are generated to help with the creation of the API Driver
    def __init__(self, serial_port, baudrate=9600, ser=None, crc16=None, debug_mode=None):
        """
        Object instantiation
        """
        self.serial_port = "/dev/cu.usbserial-1320"
        if(ser == None):
            self.ser = serial.Serial(serial_port, baudrate)
        else:
            self.ser = ser
        if(crc16 == None):
            self.set_CRC16(0xFFFF)
        else:
            self.set_CRC16(crc16)
        if(debug_mode == None):
            self.set_debug_mode(False)
        else:
            self.set_debug_mode(debug_mode)
        self.init_flag = False # uninitialized
        self.port_handles = None

    def get_CRC16(self):
        return self.crc16
    def set_CRC16(self, crc16):
        self.crc16 = crc16

    def get_debug_mode(self):
        return self.debug_mode
    def set_debug_mode(self, debug_mode):
        self.debug_mode = debug_mode

    def set_init_flag(self, flag_status: bool):
        self.init_flag = flag_status # False for uninitialized, True for initialized
    def get_init_flag(self):
        return self.init_flag
    
    def set_port_handles(self, port_handles):
        self.port_handles = port_handles
    def get_port_handles(self):
        return self.port_handles

    def help(self):
        """
        Prints a list of all commands. Undecided on how to handle this
        """
        pass

    def send_command(self, command):
        """
        Sends commands through serial connection
        """
        # example -> self.ser.write(b"BEEP 1\r")
        self.ser.write(bytes(command, 'utf-8'))
        reply = self.ser.read_until(b'\r')
        if(self.get_debug_mode()):
            self.reply_decoder(reply.decode(), command)
        return reply.decode()

    def close(self):
        """
        Closes connection to the device
        """
        self.ser.close()
        print(f"Closed serial connection to '{self.serial_port}'")

    def reply_decoder(self, reply, command):
        """
        Interprets replies including error codes
        """
        stripped_command = command.strip('\r')
        if("ERROR" in reply):
            error_codes = reply.split("ERROR")[-1]
            # Error codes always come in length 2, so split them into strings of len 2
            error_list = []
            temp = ""
            for i in range(len(error_codes)):
                if(i % 2 == 1):
                    temp += error_codes[i]
                    error_list.append(temp)
                else:
                    temp = error_codes[i]
            print(f"Command: {stripped_command} - Error: {reply}")
            for err in error_list:
                if(err in error_codes_dict):
                    print(f"* Code: {err} - {error_codes_dict[err]}")
                else:
                    print(f"* Code: {err} - Unknown error")
        else:
            print(f"Command: {stripped_command} - Reply: {reply}")

    def phsr_reply_decode(self, reply):
        """
        Interprets PHSR status reply
        Reply structure:
            <Number of Port Handles> - 2 characters
            <1st Port Handle><1st Port Handle Status> - 5 characters, first 2 char are port handle, last 3 char are status
            <2nd Port Handle><2nd Port Handle Status> - 5 characters, first 2 char are port handle, last 3 char are status
            ...
            <nth Port Handle><nth Port Handle Status> - 5 characters, first 2 char are port handle, last 3 char are status
            <CRC16><CR> - 4 characters
        Example reply (1):
            040A0010B0010C0010D001ECFB -> Actual reply encountered so far
            <04><0A 001><0B 001><0C 001><0D 001><ECFB>
        Example reply (2):
            001414 -> In this case, there are no tools connected to the system.
            <00><1414>
        Example reply (3):
            040A01F0B01F0C01F0D01F2DDB -> In this case, four tools are connected to the system and have been assigned port handles 0A, 0B, 0C, and 0D. All four port handles are initialized but not enabled.
            <04><0A 01F><0B 01F><0C 01F><0D 01F><2DDB>
        Example reply (4):
            010A001C1B5 -> In this case, one tool is connected to the system and it has been assigned port handle 0A. This port handle is not initialized or enabled.
            <01><0A 001><C1B5>
        """
        # Number of Port Handles
        num_port_handles = int(reply[:2], 16)
        reply = reply[2:]
        # Port Handles and their Status
        port_handles = []
        for _ in range(num_port_handles):
            port_handle = reply[:2]
            port_status = reply[2:5]
            port_handles.append((port_handle, port_status))
            reply = reply[5:]
        # CRC16
        crc16 = reply[:4]
        if(self.get_debug_mode):
            # Printing for debug
            print("\t*** PHSR reply decode ***")
            print(f"\t- Number of Port Handles: {num_port_handles}")
            for port_handle, port_status in port_handles:
                print(f"\t- Port Handle: {port_handle} -> Port Handle Status: {port_status} -> {port_status_dict[port_status]}")
                self.interpret_status(port_status)
            print(f"\t- CRC16: {crc16}")
            print("\t*** **************** ***")
        # Setting CRC16 and port handles
        self.set_CRC16 = crc16
        self.set_port_handles = port_handles
        return num_port_handles, port_handles, crc16
    
    def interpret_status(self, port_status_hex):
        # Convert the hex string to an integer
        port_status_int = int(port_status_hex, 16)

        # Create a dictionary to store the status of each bit field
        status_dict = {
            'Occupied': bool(port_status_int & (1 << 0)),
            'GPIO line 1 closed': bool(port_status_int & (1 << 1)),
            'GPIO line 2 closed': bool(port_status_int & (1 << 2)),
            'GPIO line 3 closed': bool(port_status_int & (1 << 3)),
            'Initialized': bool(port_status_int & (1 << 4)),
            'Enabled': bool(port_status_int & (1 << 5)),
        }

        # Print the status of each bit field
        for field, status in status_dict.items():
            print(f"\t\t- {field}: {status}")


    # Section 2
    # Functions in this section are direct implementations of the Aurora API
    def api_rev(self):
        """
        Prints the API revision
        """
        api_rev = f"APIREV \r"
        reply = self.send_command(api_rev)
        print(f"API revision: {reply}")

    def beep(self, num_beeps=1):
        """
        Generates a beep
        """
        if(num_beeps < 1 or num_beeps > 9):
            print(f"Keep number of beeps within 1-9")
            num_beeps = 9
        beep = f"BEEP {num_beeps}\r"
        reply = self.send_command(beep)
        # print(f"Beep = {reply}")

    def bx(self, option=0):
        """
        Returns the latest tool transformations and system status in binary format
        """
        # Not implemented correctly yet?
        reply_options = [0x0001, 0x0800]
        # self.send_command(f"BX {reply_options[option]}\r")
        bx = f"BX \r"
        reply = self.send_command(bx)

        # checksum = HelperClass.crc16('BX')
        # checksum_str = str(checksum)
        # command_str = f"BX{checksum_str}\r"
        # self.send_command(command_str)

    def comm(self, baud_rate="0", data_bits="0", parity="0", stop_bits="0", hardware_handshaking="0"):
        """
        Sets the serial connection settings for the system
        Syntax:
            COMM<SPACE><Baud Rate><Data Bits><Parity><Stop Bits><Hardware Handshaking><CR>
        Example command &  reply:
            COMM 30001 -> OKAYA896
        """
        baud_rate_options = {
            # Values in bps (bits per second)
            "0": "9600",   # default
            "1": "14400",
            "2": "19200",
            "3": "38400",
            "4": "57000",
            "5": "115200",
            "6": "921600", #  921600 baud is only available via USB and with combined firmware revision 009 (API Revision D.001.006) or later. A USB port is available on Aurora V2 systems
            "A": "230400"  # Baud rate parameter "A" is available with combined firmware revision 009 (API Revision D.001.006) or later.
        }
        data_bits_options = {
            "0": "8", # default, must be set to 8 in order to use BX command
            "1": "7"
        }
        parity_options = {
            "0": "None", # default
            "1": "Odd",
            "2": "Even"
        }
        stop_bits_options = {
            "0": "1", # default
            "1": "2"
        }
        hardware_handshaking_options = {
            "0": "Off", # default
            "1": "On"
        }

        user_parameters = [baud_rate, data_bits, parity, stop_bits, hardware_handshaking]
        comm_options = [baud_rate_options, data_bits_options, parity_options, stop_bits_options, hardware_handshaking_options]
        parameter_names = ["Baud rate", "Data bits", "Parity", "Stop bits", "Hardware handshaking"]
    
        valid_command = True
        for param, options, name in zip(user_parameters, comm_options, parameter_names):
            if(not param in options):
                print(f"Failure - {name}: {param}")
                print(f"Select an option from {list(options.keys())}")
                valid_command = False
        if(valid_command):
            comm = f"COMM {baud_rate}{data_bits}{parity}{stop_bits}{hardware_handshaking}\r"
            reply = self.send_command(comm)

    def dstart(self):
        """
        Deprecated. Use tstart()
        """
        pass

    def dstop(self):
        """
        Deprecated. Use tstop()
        """
        pass

    def echo(self, reply_str):
        """
        Returns exactly what is sent with the command
        Syntax:
            ECHO<SPACE><Four or more ASCII characters><CR>
        Example command and reply:
            ECHO Testing! -> Testing!A81C
        """
        echo = f"ECHO {reply_str}\r"
        reply = self.send_command(echo)

    def get(self, *user_params):
        """
        Returns the values of user parameters.
        Currently the only user parameter values are timeouts for the API commands.
        Only Info.Timeout is currently supported.
        Syntax:
            GET<SPACE><User Parameter Name><CR>
        Example command and reply:
            GET Info.Timeout.PINIT -> Info.Timeout.PINIT=5<LF>96A7
        """ 
        # Currently just using "GET *" to return all parameters
        get = f"GET *\r"
        reply = self.send_command(get)

    def init(self):
        """
        Initializes the system
        Syntax:
            INIT<SPACE><CR>
        Example command and reply:
            INIT -> OKAYA896
        """
        init = f"INIT \r"
        reply = self.send_command(init)

    def led(self, port_handle="0A", led_number="1", led_state="S"):
        """
        Changes the state of visible LEDs on a tool
        Syntax:
            LED<SPACE><Port Handle><LED Number><State><CR>
        Example command and reply:
            LED 0A1S -> OKAYA896
        """
        port_handle_options = HelperClass.port_handle_options
        led_number_options = ["1", "2", "3"]
        led_state_options = ["B", "F", "S"]
        
        user_parameters = [port_handle, led_number, led_state]
        led_options = [port_handle_options, led_number_options, led_state_options]
        parameter_names = ["Port handle", "LED number", "LED State"]

        valid_command = True
        for param, options, name in zip(user_parameters, led_options, parameter_names):
            if(not param in options):
                print(f"Failure - {name}: {param}")
                print(f"Select an option from {options}")
                valid_command = False
        if(valid_command):
            led = f"LED {port_handle}{led_number}{led_state}"
            reply = self.send_command(led)

    def pdis(self):
        """
        Disables the reporting of transformations fora particular port handle
        """
        pass

    def pena(self):
        """
        Enables reporting of transformations for a particular port handle
        """
        pass

    def phf(self):
        """
        Releases system resources from an unused port handle
        """
        pass

    def phinf(self):
        """
        Returns information about the tool associated with the port handle
        """
        pass

    def phsr(self):
        """
        Returns the number of assigned port handles and the port status for each one
        Assigns a port handle to a tool
        Prerequisite command:
            INIT
        Syntax:
            PHSR<SPACE><Reply Option><CR>
        Example command and reply:
            PHSR -> 001414,                        In this case, there are no tools connected to the system
            PHSR -> 010A001C1B5,                   In this case, one tool is connected to the system and it has been assigned port handle 0A. This port handle is not initialized or enabled.
            PHSR 03 -> 040A01F0B01F0C01F0D01F2DDB, In this case, four tool is connected to the system and have been assigned port handles 0A, 0B, 0C, and 0D. All four port handles are initialized but not enabled
                04-0A-01-F-0B-01-F-0C-01-F-0D-01-F-2D-DB
        """
        # Currently just using "PHSR" to return all port handles and set them too
        # Check if initialized, if not, initialize it
        if(not self.get_init_flag()):
            print(f"Initializing via PHSR")
            self.init()
        phsr = f"PHSR \r"
        reply = self.send_command(phsr)
        if(self.get_debug_mode()):
            reply_decode = self.phsr_reply_decode(reply)

        # TODO: Implement phsr reply interpreter

    def pinit(self):
        """
        Initializes a port handle
        Prerequisite command:
            PHSR
        Syntax:
            PINIT<SPACE><Port Handle><CR>
        Example command and reply:
            PINIT 0A -> OKAYA896
        """
        pass

    def pprd(self):
        """
        Reads data from the SROM device in a tool
        """
        pass

    def ppwr(self):
        """
        Writes data to the SROM device in a tool
        """
        pass

    def psel(self):
        """
        Selects a tool SROM device as the target for reading or writing with pprd() or ppwr()
        """
        pass

    def psout(self):
        """
        Sets the status of the GPIO in the Aurora System
        """
        pass

    def psrch(self):
        """
        Returns a list of valid SROM device IDs for a tool
        Syntax:
            PSRCH<SPACE><Port Handle><CR>
        Example command and reply:
            PPSRCH 0A -> 10B3876530000005B7FFF, In this case, there is one SROM device, with ID 0B3876530000005B.
                1-0B3876530000005B7FFF
        """
        pass

    def purd(self):
        """
        Reads data from the user section of the SROM device in a tool
        """
        pass

    def puwr(self):
        """
        Writes data to the user section of the SROM device in a tool
        """
        pass

    def pvwr(self):
        """
        Override a tool definition file in a tool, and cand be used to test a tool definiton file before permanently recording the tool definition file onto the SROM device
        """
        pass

    def reset(self):
        """
        Resets the system
        """
        # crc16 = HelperClass.crc16('RESET')
        # command_str = f"RESET{str(crc16)}\r"
        # reply = self.send_command(command_str)

        crc16 = HelperClass.calc_crc16('RESET', self)
        command_str = f"RESET{str(self.get_CRC16())}\r"
        reply = self.send_command(command_str)
        # self.ser.write(command_str.encode())

    def serial_break(self):
        """
        Resets the system
        """
        pass

    def sflist(self):
        """
        Returns information about the supported features of the system
        """
        pass

    def tstart(self):
        """
        Starts tracking mode
        """
        pass

    def tstop(self):
        """
        Stops tracking mode
        Replies
            - Upon success:
                - OKAY<CRC16><CR>
            - On error:
                - ERROR<Error Code><CRC16><CR>
        """
        tstop = f"TSTOP \r"
        reply = self.send_command(tstop)
        print(f"TSTOP. Tracking stopped")


    def ttcfg(self):
        """
        Sets up a configuration for a tool, so that you can test the tool without usinga tool definition file
        Reply options
            - 0x0001: Transformation data (default)
            - 0x0800: Transformations not normally reported
        Replies
            - Upon success:
                - <Number of Handles><Handle 1><Reply Option 0001 Data><LF>
                - ...
                - <Handle n><Reply Option 0001><LF>
                - <System Status><CRC16><CR>
            - On error:
                - ERROR<Error Code><CRC16><CR>
        """
        pass

    def tx(self):
        """
        Returns the latest tool transformations and system status in text format
        """
        pass
    
    def ver(self, reply_option=0):
        """
        Returns the latest firmware revision number of critcial processors installed in the system
        """
        reply_options = [0, 4, 5, 7, 8]
        if(reply_option in reply_options):
            print("---")
            ver = f"VER {reply_option}\r"
            self.send_command(ver)
            print("---")
        else:
            print(f"*** Error 'ver' does not have reply option '{reply_option}' as a valid option.\n*** Select one from {reply_options}")

    def vsel(self):
        """
        Selects characterized measurement volume
        """
        pass

class HelperClass:
    # Hex numbers 0A-FF, in 2 character format, upper case
    port_handle_options = [hex(i)[2:].zfill(2).upper() for i in range(0x0A, 0x100)]

    def crc16(data: str, ndi_obj: NDI_Aurora, poly=0xA001):
        """
        16-bit Cyclical Redundancy Check
        """
        crc = ndi_obj.get_CRC16()
        for b in bytearray(data, 'ascii'):
            crc ^= b
            for _ in range(8):
                crc = (crc >> 1) ^ poly if (crc & 0x0001) else crc >> 1
            # print(f"b = {b} | crc = {crc}")
        ndi_obj.set_CRC16(crc)
        return crc
    
    def calc_crc16(data_str: str, ndi_obj: NDI_Aurora):
        """
        Refer to Helper/CalcCRC16.cpp to double check that the CRC values are matching.

        data_str: Data value to add to running CRC16.
        crc16   : Running value always updated to double check that messages are matching.

        This routine calculates a running CRC16 using the polynomial: X^16 + X^15 + X^2 + 1.
        """
        oddparity = [0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0]
        crc16 = ndi_obj.get_CRC16()
        for ch in data_str:
            data = ord(ch)
            data = (data ^ (crc16 & 0xff)) & 0xff
            crc16 >>= 8
            if(oddparity[data & 0x0f] ^ oddparity[data >> 4]):
                crc16 ^= 0xc001
            data <<= 6
            crc16 ^= data
            data <<= 1
            crc16 ^= data
        
        ndi_obj.set_CRC16(crc16)
        return crc16

    def get_os():
        """
        Returns OS type (Windows, Mac, Linux)
        """
        os_type = "Unknown"
        os = platform.system()
        if(os == "Windows"):
            os_type = "Windows"
        elif(os == "Darwin"):
            os_type = "Mac"
        elif(os == "Linux"):
            os_type = "Linux"
        print(f"Operating System = {os_type}")
        port = HelperClass.find_com_port()
        return os_type
    
    def find_com_port():
        """
        Helper function to find out which COM port the Aurora device is connected to on Windows machines.
        """
        try:
            ports = list_ports.comports()
            for port, desc, hwid in sorted(ports):
                print(f"{port} | {desc} | [{hwid}]")
            return ports
        except Exception as e:
            print(f"Error: {e}")
        