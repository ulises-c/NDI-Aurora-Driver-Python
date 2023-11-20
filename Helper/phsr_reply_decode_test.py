# from Aurora_Driver.AuroraPortStatus import port_status_dict

def phsr_reply_decode(self, reply):
    """
    Interprets PHSR status reply
    """
    # Number of Port Handles
    num_port_handles = int(reply[:2], 16)
    reply = reply[2:]
    # Port Handles and their Status
    port_handles = {}
    for _ in range(num_port_handles):
        port_handle = reply[:2]
        port_status = reply[2:5]
        port_handles[port_handle] = port_status
        reply = reply[5:]
    # CRC16
    crc16 = reply[:4]
    if(True):
        # Printing for debug
        print("\t*** PHSR reply decode ***")
        print(f"\t- Number of Port Handles: {num_port_handles}")
        for port_handle, port_status in port_handles.items():
            print(f"\t- Port Handle: {port_handle} -> Port Handle Status: {port_status}  -> {port_status_dict[port_status]}")
        print(f"\t- CRC16: {crc16}")
        print("\t*** **************** ***")
    # Setting CRC16 and port handles
    # self.set_CRC16 = crc16
    # self.set_port_handles = port_handles
    return num_port_handles, port_handles, crc16


# Test the function with your examples
replies = ["040A0010B0010C0010D001ECFB", "001414", "040A01F0B01F0C01F0D01F2DDB", "010A001C1B5"]
for r in replies:
    phsr_reply_decode(self=None, reply=r)
    print()
