Python drivers for NDI's (Northern Digital Inc.) Aurora system.

Based off of "Aurora Application Program Interface Guide, Revision 4, October 2011" PDF

Project started Nov 3, 2023. Still a work in progress.

Connect an NDI measurement system to the host machine and ensure the device is visible on the OS.
- For serial devices, ensure the USB drivers are installed and the operating system recognizes the serial port.
- - On Windows this will be a COM port listed in the device manager.
- - On Linux this will be a /dev/tty* device (usually /dev/ttyUSBx where x is a number).
- - On macOS this will be /dev/cu.usbserial-xxxxx and /dev/tty.usbserial-xxxxx. Use the /dev/cu.usbserial-xxxxx port as it is the variant that supports blocked reads and writes.
- For ethernet devices, ensure the host machine can ping the hostname or IP address of the NDI device.