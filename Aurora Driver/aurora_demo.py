import AuroraDriver
import time

os_type = AuroraDriver.HelperFunctions.get_os()

ndi_obj = None
mac_port = "/dev/cu.usbserial-1320"
win_port = "COM7"

if(os_type == "Windows"):
    ndi_obj = AuroraDriver.NDI_Aurora(serial_port=win_port)
elif(os_type == "Mac"):
    ndi_obj = AuroraDriver.NDI_Aurora(serial_port=mac_port)

# for i in range(5):
#     ndi_obj.beep(1)
#     time.sleep(0.25)
# ndi_obj.reset()
# ndi_obj.bx()
# ndi_obj.beep()
# ndi_obj.tstop()
ndi_obj.api_rev()
# ndi_obj.ver()
# ndi_obj.close()