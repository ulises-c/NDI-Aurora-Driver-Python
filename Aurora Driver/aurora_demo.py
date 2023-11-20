import AuroraDriver

os_type = AuroraDriver.HelperClass.get_os()

ndi_obj = None
mac_port = "/dev/cu.usbserial-1320"
win_port = "COM6"

if(os_type == "Windows"):
    ndi_obj = AuroraDriver.NDI_Aurora(serial_port=win_port, debug_mode=True)
elif(os_type == "Mac"):
    ndi_obj = AuroraDriver.NDI_Aurora(serial_port=mac_port, debug_mode=True)


### working commands
ndi_obj.comm()
ndi_obj.beep()
# ndi_obj.api_rev()
# ndi_obj.ver()
# ndi_obj.close()
# ndi_obj.echo("Testing!")
ndi_obj.init()
# ndi_obj.get()
ndi_obj.phsr()

### partially working commands 
# ndi_obj.bx()
# ndi_obj.tstop()
# ndi_obj.led()

### not working commands
# ndi_obj.reset()

### untested commands

# AuroraDriver.NDI_Aurora.reply_decoder(self=None, reply="ERROR133A42", command="PINIT 0A")