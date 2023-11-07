import serial
from serial.tools import list_ports
import binascii
import platform

from AuroraErrorCodes import error_codes_dict

class NDI_Aurora:
    # Section 1
    # Functions in this section are generated to help with the creation of the API Driver
    def __init__(self, serial_port, ser=None):
        """
        Object instantiation
        """
        self.serial_port = "/dev/cu.usbserial-1320"
        if(ser == None):
            self.ser = serial.Serial(serial_port, baudrate=9600)

    def help(self):
        """
        Prints a list of all commands
        """
        pass

    def send_command(self, command, cmd_print=True):
        """
        Sends commands through serial connection
        """
        # example -> self.ser.write(b"BEEP 1\r")
        self.ser.write(bytes(command, 'utf-8'))
        reply = self.ser.read_until(b'\r')
        if(cmd_print):
            self.error_decoder(reply.decode(), command)
        return reply.decode()

    def close(self):
        """
        Closes connection to the device
        """
        self.ser.close()
        print(f"Closed serial connection to '{self.serial_port}'")

    def error_decoder(self, reply, command):
        """
        Interprets error code
        """
        if "ERROR" in reply:
            error_codes = reply.split("ERROR")[-1]
            # Error codes always come in length 2, so split them into strings of len 2
            error_list = []
            temp = ""
            for i in range(len(error_codes)):
                if i % 2 == 1:
                    temp += error_codes[i]
                    error_list.append(temp)
                else:
                    temp = error_codes[i]

            print(command)
            print(f"Command: {command} - Error: {reply}")
            for err in error_list:
                if err in error_codes_dict:
                    print(f"* Code: {err} - {error_codes_dict[err]}")
                else:
                    print(f"* Code: {err} - Unknown error")

    # Section 2
    # Functions in this section are direct implementations of the Aurora API
    def api_rev(self):
        """
        Prints the API revision
        """
        api_rev = f"APIREV \r"
        reply = self.send_command(api_rev, cmd_print=False)
        print(f"API revision: {reply}")

    def beep(self, num_beeps=1):
        """
        Generates a beep
        """
        if(num_beeps < 1 or num_beeps > 9):
            print(f"Keep number of beeps within 1-9")
            num_beeps = 9
        beep = f"BEEP {num_beeps}\r"
        reply = self.send_command(beep, cmd_print=False)
        # print(f"Beep = {reply}")

    def bx(self, option=0):
        """
        Returns the latest tool transformations and system status in binary format
        """
        # Not implemented correctly yet?
        reply_options = [0x0001, 0x0800]
        # self.send_command(f"BX {reply_options[option]}\r")
        bx = f"BX \r"
        reply = self.send_command(bx, cmd_print=True)

        # checksum = HelperFunctions.crc16('BX')
        # checksum_str = str(checksum)
        # command_str = f"BX{checksum_str}\r"
        # self.send_command(command_str)

    def comm(self):
        """
        Sets the serial connection settings for the system
        """
        pass

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

    def echo(self):
        """
        Returns exactly what is sent with the command
        """
        pass

    def get(self):
        """
        Returns the values of user parameters
        """
        pass

    def init(self):
        """
        Initializes the system
        """
        pass

    def led(self):
        """
        Changes the state of visible LEDs on a tool
        """
        pass

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
        """
        pass

    def pinit(self):
        """
        Initializes a port handle
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
        checksum = HelperFunctions.crc16('RESET')
        checksum_str = str(checksum)
        command_str = f"RESET{checksum_str}\r"
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
        reply = self.send_command(tstop, cmd_print=True)
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
        if reply_option in reply_options:
            print("---")
            ver = f"VER {reply_option}\r"
            self.send_command(ver, cmd_print=True)
            print("---")
        else:
            print(f"*** Error 'ver' does not have reply option '{reply_option}' as a valid option.\n*** Select one from {reply_options}")

    def vsel(self):
        """
        Selects characterized measurement volume
        """
        pass

class HelperFunctions:
    def crc16(data: str, poly=0xA001):
        """
        16-bit Cyclical Redundancy Check
        """
        crc = 0xFFFF
        for b in bytearray(data, 'ascii'):
            crc ^= b
            for _ in range(8):
                crc = (crc >> 1) ^ poly if (crc & 0x0001) else crc >> 1
            print(f"b = {b} | crc = {crc}")
        return crc
    
    def get_os():
        """
        Returns OS type (Windows, Mac, Linux)
        """
        os = platform.system()
        os_type = "Unknown"
        if os == "Windows":
            HelperFunctions.find_com_port()
            os_type = "Windows"
        elif os == "Darwin":
            os_type = "Mac"
        elif os == "Linux":
            os_type = "Linux"
        print(f"OS = {os_type}")
        return os_type
    
    def find_com_port():
        """
        Helper function to find out which COM port the Aurora device is connected to on Windows machines.
        """
        ports = list_ports.comports()
        for port, desc, hwid in sorted(ports):
                print("{}: {} [{}]".format(port, desc, hwid))