import uModBusFunctions as functions
import uModBusConst as Const
from machine import UART
from machine import Pin
import struct
import time
import machine

class uModBusServer:

    def __init__(self, uart_id=0, uart = None, baudrate=9600, data_bits=8, stop_bits=1, parity=None, pins=None, ctrl_pin=None, loopbacked=True, slave_id=1, callbackfunction=None):
        pinsLen=len(pins)
        if pins==None or pinsLen<2 or pinsLen>4 or pinsLen==3:
            raise ValueError('pins should contain pin names/numbers for: tx, rx, [rts, cts]')
        tx=pins[0]
        rx=pins[1]
        if uart is None:
            if pinsLen==4:
                rts=pins[2]
                cts=pins[3]
                self._uart = UART(uart_id, baudrate=baudrate, bits=data_bits, parity=parity, \
                              stop=stop_bits, timeout=1, timeout_char=1, tx=tx, rx=rx, rts=rts, cts=cts, rxbuf=16)
            else:
                self._uart = UART(uart_id, baudrate=baudrate, bits=data_bits, parity=parity, \
                                stop=stop_bits, timeout=1, timeout_char=1, tx=tx, rx=rx, rxbuf=16)
        else:
            self._uart = uart
        if ctrl_pin is not None:
            self._ctrlPin = Pin(ctrl_pin, mode=Pin.OUT)
            self._ctrlPin(0)
        else:
            self._ctrlPin = None
        self.char_time_ms = (1000 * (data_bits + stop_bits + 2)) / baudrate
        self.loopbacked = loopbacked
        self.slave_id = slave_id
        self._callbackfunction = callbackfunction
        self._txdata = bytearray(256)
        self._txlen = 0

    def _calculate_crc16(self, data):
        crc = 0xFFFF

        for char in data:
            crc = (crc >> 8) ^ Const.CRC16_TABLE[((crc) ^ char) & 0xFF]

        return struct.pack('<H',crc)
    
    def _dispatch(self, rxdata):
        # check with Function code was received
        if (rxdata[0] == 0x03) or (rxdata[0] == 0x04): # read holding registers
            if len(rxdata) >= 5:
                (starting_addr, quantity) = struct.unpack('>HH', rxdata[1:])
                if quantity*2 > (256-5): # illegal amount of registersrequested.
                    self._txdata[self._txlen] = self.slave_id
                    self._txlen = self._txlen+1
                    self._txdata[self._txlen] = rxdata[0] | 0x80 
                    self._txlen = self._txlen+1
                    self._txdata[self._txlen] = 0
                    self._txlen = self._txlen+1
                    crc = self._calculate_crc16(self._txdata[0:self._txlen])
                    self._txdata[self._txlen] = crc[0]
                    self._txlen = self._txlen+1
                    self._txdata[self._txlen] = crc[1]
                    self._txlen = self._txlen+1
                    
                    if self._ctrlPin:
                        self._ctrlPin(1)
                    self._uart.write(self._txdata[0:self._txlen])
                    if self._ctrlPin:
                        #while not self._uart.wait_tx_done(2):
                        #    machine.idle()
                        time.sleep_ms(int(1 + self._txlen*self.char_time_ms))
                        self._ctrlPin(0)
                    
                    if self.loopbacked:
                        self._uart.read(self._txlen) # flush echoed data
                elif self._callbackfunction is not None:
                    self._txdata[self._txlen] = self.slave_id
                    self._txlen = self._txlen+1
                    self._txdata[self._txlen] = rxdata[0]
                    self._txlen = self._txlen+1
                    self._txdata[self._txlen] = quantity*2
                    self._txlen = self._txlen+1
                    startcount = self._txlen
                    self._callbackfunction(self, rxdata[0]*10000 + starting_addr + 1, quantity)
                    regcount = (self._txlen - startcount)/2
                    if regcount < quantity:
                        raise OSError('%d registers requested but only %d written in callback function.' % (regcount, quantity))
                    crc = self._calculate_crc16(self._txdata[0:self._txlen])
                    self._txdata[self._txlen] = crc[0]
                    self._txlen = self._txlen+1
                    self._txdata[self._txlen] = crc[1]
                    self._txlen = self._txlen+1
                    
                    if self._ctrlPin:
                        self._ctrlPin(1)
                    self._uart.write(self._txdata[0:self._txlen])
                    if self._ctrlPin:
                        #while not self._uart.wait_tx_done(2):
                        #    machine.idle()
                        time.sleep_ms(int(1 + self._txlen*self.char_time_ms))
                        self._ctrlPin(0)
                    
                    if self.loopbacked:
                        self._uart.read(self._txlen) # flush echoed data
                    #print(bytearray(self._txdata))
                else:
                    raise OSError('no callback function defined, cannot handle received request')
        

    def receive(self):
        self._txlen=0
        data = self._uart.read()
        if data is not None:
            if data[0] == self.slave_id:  # check if the right slave is addressed
                if self._calculate_crc16(data) == b'\x00\x00': # check if CRC is correct
                    data = data[1:-2]
                    if len(data) > 0:
                        self._dispatch(data) # interpret the received package (with stripped off slaveID and CRC)
    
    def sendreg(self, value):
        self._txdata[self._txlen] = value >> 8
        self._txlen = self._txlen+1
        self._txdata[self._txlen] = value & 0xff
        self._txlen = self._txlen+1
        pass
        
        