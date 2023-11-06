import AuroraDriver
import time

ndi_obj = AuroraDriver.NDI_Aurora(serial_port="/dev/cu.usbserial-1320")
for i in range(5):
    ndi_obj.beep(1)
    time.sleep(0.25)
# ndi_obj.reset()
ndi_obj.bx()
ndi_obj.api_rev()
ndi_obj.close()