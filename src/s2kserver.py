from machine import UART, Pin
import sys
sys.path.append('modbus')
from uModBusServer import *
from uModBusSerial import *
import _thread
from sun2000 import *

# Below sdm630 import handles communication with an SDM630 electricity meter.
# Simply implement your own module (see sdm630.py) to handle other electricity meters and import it here!
from sdm630 import *


# This callback function gets called by the modbus server for every register which has to be read.
def readRegister(server, starting_addr, quantity):
    #print('read request received. starting_addr=%d, quantity=%d' % (starting_addr, quantity))
    while quantity > 0:
        try:
            value = s2k.registers[starting_addr]
        except:
            value = 0            
        server.sendreg(value)
        starting_addr = starting_addr + 1
        quantity = quantity - 1


# The server thread is run in background and handles queries from an external Sun2000 modbus client
def serverthread():
    while True:
        try:
            server.receive()
        except Exception as e:
            print('serverthread exception occured: '+str(e))
            pass;

# Below 2 lines instantiate a modbus server and client. Adjust pins and uart settings according to your board design
server = uModBusServer(slave_id=11, uart_id = 0, baudrate=9600, data_bits=8, stop_bits=1, parity=None, pins=(Pin(16), Pin(17)), ctrl_pin=None, loopbacked=True, callbackfunction=readRegister)
client = uModBusSerial(uart_id = 1, baudrate=9600, data_bits=8, stop_bits=1, parity=None, pins=(Pin(4), Pin(5)), ctrl_pin=3, loopbacked=True)
s2k = sun2000()
mtr = meter(client, s2k)

_thread.start_new_thread(serverthread, ())

# Below thread does continously read your electricity meter data and push them to sun2000 module registers
while True:
    try:
        mtr.updateRegisters()
    except Exception as e:
        print('clientthread exception occured: '+str(e))
        pass;
    
