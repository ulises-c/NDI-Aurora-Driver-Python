import serial
import binascii

class NDI_Aurora:
    def __init__(self, serial_port, ser=None):
        self.serial_port = "/dev/cu.usbserial-1320"
        if(ser == None):
            self.ser = serial.Serial(serial_port, baudrate=9600)

    def send_command(self, command, cmd_print=True):
        # example -> self.ser.write(b"BEEP 1\r")
        self.ser.write(bytes(command, 'utf-8'))
        reply = self.ser.read_until(b'\r')
        if(cmd_print):
            print(reply.decode())
        return reply.decode()

    def close(self):
        self.ser.close()
        print(f"Closed serial connection to '{self.serial_port}'")
    ß
    def beep(self, num_beeps):
        # Send a beep
        if(num_beeps < 1 or num_beeps > 9):
            print(f"Keep number of beeps within 1-9")
            num_beeps = 9
        beep = self.send_command(f"BEEP {num_beeps}\r", cmd_print=False)
        print(f"Beep = {beep}")

    def reset(self):
        checksum = HelperFunctions.crc16('RESET')
        checksum_str = str(checksum)
        command_str = f"RESET{checksum_str}\r"
        self.send_command(command_str)
        # self.ser.write(command_str.encode())
    
    def api_rev(self):
        api_rev = self.send_command(f"APIREV \r", cmd_print=False)
        print(f"API revision: {api_rev}")

    def bx(self, option=0):
        # Not implemented correctly yet?
        reply_options = [0x0001, 0x0800]
        # self.send_command(f"BX {reply_options[option]}\r")
        self.send_command(f"BX \r")

        # checksum = HelperFunctions.crc16('BX')
        # checksum_str = str(checksum)
        # command_str = f"BX{checksum_str}\r"
        # self.send_command(command_str)

    def comm(self):
        # Sets the serial connection settings for the system
        pass

class HelperFunctions:
    def crc16(data: str, poly=0xA001):
        crc = 0xFFFF
        for b in bytearray(data, 'ascii'):
            crc ^= b
            for _ in range(8):
                crc = (crc >> 1) ^ poly if (crc & 0x0001) else crc >> 1
            print(f"b = {b} | crc = {crc}")
        return crc