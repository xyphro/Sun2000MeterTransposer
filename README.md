# Sun2000MeterTransposer

-> Enable other Smartmeters like SDM630 to connect to Huawei Sun2000 and look like DTSU-666.

This was my solution to address the fact, that DTSU-666 and its variants availability was "null".

<img src="https://github.com/xyphro/Sun2000MeterTransposer/raw/main/photos/Installed%20in%20meter%20cabinet.jpg" width="50%"/>

It works rock solid since several months without a single interruption.

The project is based on RP2040 Raspberry pi Zero module. It will work on the Wifi variant too, but there is no network access enabled.

Note: I did not document the HW very well (yet), but want to share it still with the community. Build it at your own risk. The pinning of the 2 UART channels can be seen in s2kserver.py module (or schematic).

Warning: This project works with high voltage AC supply. You risk killing yourself, your family and friends, your pets. Take care and only work with line voltages when you are experienced in how much pain it causes to touch 230V :-)

# Folder structure

- hw: contains schematic / PCB in Eagle format.
- src: Micropython sourcecode - can be directly uploaded to RP2040 module using e.g. Thony IDE
- DinRainHousing: STL files for the 3D printed Dinrail housing
- photos: Some pictures of the actual build as inspiration

# Adjustments to other meters

Copy file sdm630.py and rename it to your meter name. Adjust it, such that the equivalent registers of your meter are read out and written to s2k module registers.
Within file s2kserver.py:
- You might need to change the UART settings like baudrate, parity in s2kserver during instatiation of uModBusSerial module.
- change ```from sdm630 import *``` to your module name

# Sourcecode orientation

main.py purpose is only to start s2kserver.py.
s2kserver instantiates 2 threads to server requests from Sun2000 inverter and poll SDM630 meter continously.

# Credits

Credits go to:
- uModbus [1] project. I changed the file slightly and included all dependencies within the src folder. Main modifications were done for speed/latency purposes
- DTSU666-Modbus [2] project: This project was of major support for the idea and to get register details. 
- GitHub user salakrzy


[1] https://github.com/pycom/pycom-modbus/tree/master/uModbus

[2] https://github.com/elfabriceu/DTSU666-Modbus
