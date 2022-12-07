#Source: https://github.com/pycom/pycom-modbus/tree/master/uModbus (2018-07-16)
#This file has been modified and differ from its source version.

import uModBusFunctions as functions
import uModBusConst as Const
from machine import UART
from machine import Pin
import struct
import time
import machine

class uModBusSerial:

    def __init__(self, uart_id, baudrate=9600, data_bits=8, stop_bits=1, parity=None, pins=None, ctrl_pin=None, loopbacked=True):
        pinsLen=len(pins)
        if pins==None or pinsLen<2 or pinsLen>4 or pinsLen==3:
            raise ValueError('pins should contain pin names/numbers for: tx, rx, [rts, cts]')
        tx=pins[0]
        rx=pins[1]
        if pinsLen==4:
            rts=pins[2]
            cts=pins[3]
            self._uart = UART(uart_id, baudrate=baudrate, bits=data_bits, parity=parity, \
                          stop=stop_bits, timeout=100, timeout_char=2, tx=tx, rx=rx, rts=rts, cts=cts, rxbuf=256)
        else:
            self._uart = UART(uart_id, baudrate=baudrate, bits=data_bits, parity=parity, \
                            stop=stop_bits, timeout=100, timeout_char=2, tx=tx, rx=rx, rxbuf=256)
        #self._uart = UART(uart_id, baudrate=baudrate, bits=data_bits, parity=parity, \
        #                  stop=stop_bits, timeout_chars=10, pins=pins)
        if ctrl_pin is not None:
            self._ctrlPin = Pin(ctrl_pin, mode=Pin.OUT)
            self._ctrlPin(0)
        else:
            self._ctrlPin = None
        self.char_time_ms = (1000 * (data_bits + stop_bits + 2)) / baudrate
        self.loopbacked = loopbacked

    def _calculate_crc16(self, data):
        crc = 0xFFFF

        for char in data:
            crc = (crc >> 8) ^ Const.CRC16_TABLE[((crc) ^ char) & 0xFF]

        return struct.pack('<H',crc)

    def _bytes_to_bool(self, byte_list):
        bool_list = []
        for index, byte in enumerate(byte_list):
            bool_list.extend([bool(byte & (1 << n)) for n in range(8)])

        return bool_list

    def _to_short(self, byte_array, signed=True):
        response_quantity = int(len(byte_array) / 2)
        fmt = '>' + (('h' if signed else 'H') * response_quantity)

        return struct.unpack(fmt, byte_array)
    
    def _to_float(self, byte_array):
        response_quantity = int(len(byte_array) / 4)
        fmt = '>' + ('f' * response_quantity)
        
        return struct.unpack(fmt, byte_array)

    def _exit_read(self, response):
        if response[1] >= Const.ERROR_BIAS:
            if len(response) < Const.ERROR_RESP_LEN:
                return False
        elif (Const.READ_COILS <= response[1] <= Const.READ_INPUT_REGISTER):
            expected_len = Const.RESPONSE_HDR_LENGTH + 1 + response[2] + Const.CRC_LENGTH
            if len(response) < expected_len:
                return False
        elif len(response) < Const.FIXED_RESP_LEN:
            return False

        return True

    def _uart_read(self):
        response = bytearray()
        starttime = time.ticks_ms()        
        for x in range(1, 40):
            if self._uart.any():
                response.extend(self._uart.read())
                #response.extend(self._uart.readall())
                # variable length function codes may require multiple reads
                if self._exit_read(response):
                    break            
            time.sleep(0.05)

        return response

    def _send_receive(self, modbus_pdu, slave_addr, count, expectedlen = 255):
        serial_pdu = bytearray()
        serial_pdu.append(slave_addr)
        serial_pdu.extend(modbus_pdu)

        crc = self._calculate_crc16(serial_pdu)
        serial_pdu.extend(crc)

        # flush the Rx FIFO
        if self._uart.any():
            self._uart.read()
            print('flushed')
        if self._ctrlPin:
            self._ctrlPin(1)
        self._uart.write(serial_pdu)
        if self._ctrlPin:
            time.sleep_ms(int(1 + len(serial_pdu) * self.char_time_ms))
            self._ctrlPin(0)
        if self.loopbacked:
            self._uart.read(len(serial_pdu))

        response = self._uart.read(expectedlen)
        #response = []
        #while len(response) < expectedlen:
        #    response.extend(self._uart.read(expectedlen-len(response)))
        
        print(response)
            
            
        #response = self._uart_read()
        print(expectedlen, response)

        
        return self._validate_resp_hdr(response, slave_addr, modbus_pdu[0], count)

    def _validate_resp_hdr(self, response, slave_addr, function_code, count):

        if len(response) == 0:
            raise OSError('no data received from slave')

        resp_crc = response[-Const.CRC_LENGTH:]
        expected_crc = self._calculate_crc16(response[0:len(response) - Const.CRC_LENGTH])
        if (resp_crc[0] != expected_crc[0]) or (resp_crc[1] != expected_crc[1]):
            raise OSError('invalid response CRC')

        if (response[0] != slave_addr):
            raise ValueError('wrong slave address')

        if (response[1] == (function_code + Const.ERROR_BIAS)):
            raise ValueError('slave returned exception code: {:d}'.format(response[2]))

        hdr_length = (Const.RESPONSE_HDR_LENGTH + 1) if count else Const.RESPONSE_HDR_LENGTH

        return response[hdr_length : len(response) - Const.CRC_LENGTH]

    def read_coils(self, slave_addr, starting_addr, coil_qty):
        modbus_pdu = functions.read_coils(starting_addr, coil_qty)

        resp_data = self._send_receive(modbus_pdu, slave_addr, True)
        status_pdu = self._bytes_to_bool(resp_data)

        return status_pdu

    def read_discrete_inputs(self, slave_addr, starting_addr, input_qty):
        modbus_pdu = functions.read_discrete_inputs(starting_addr, input_qty)

        resp_data = self._send_receive(modbus_pdu, slave_addr, True)
        status_pdu = self._bytes_to_bool(resp_data)

        return status_pdu

    def read_holding_registers(self, slave_addr, starting_addr, register_qty, signed=True):
        modbus_pdu = functions.read_holding_registers(starting_addr, register_qty)

        resp_data = self._send_receive(modbus_pdu, slave_addr, True, expectedlen = register_quantity*2+5)
        register_value = self._to_short(resp_data, signed)

        return register_value
    
    def read_input_registers(self, slave_addr, starting_address, register_quantity, isfloat=True):
        starting_address = starting_address - 30001
        if isfloat:
            register_quantity = register_quantity * 2
        modbus_pdu = functions.read_input_registers(starting_address, register_quantity)

        resp_data = self._send_receive(modbus_pdu, slave_addr, True, expectedlen = register_quantity*2+5)
        if isfloat:
            register_value = self._to_float(resp_data)
        else:
            register_value = self._to_short(resp_data, False)

        return list(register_value)

    def write_single_coil(self, slave_addr, output_address, output_value):
        modbus_pdu = functions.write_single_coil(output_address, output_value)

        resp_data = self._send_receive(modbus_pdu, slave_addr, False)
        operation_status = functions.validate_resp_data(resp_data, Const.WRITE_SINGLE_COIL,
                                                        output_address, value=output_value, signed=False)

        return operation_status

    def write_single_register(self, slave_addr, register_address, register_value, signed=True):
        modbus_pdu = functions.write_single_register(register_address, register_value, signed)

        resp_data = self._send_receive(modbus_pdu, slave_addr, False)
        operation_status = functions.validate_resp_data(resp_data, Const.WRITE_SINGLE_REGISTER,
                                                        register_address, value=register_value, signed=signed)

        return operation_status

    def write_multiple_coils(self, slave_addr, starting_address, output_values):
        modbus_pdu = functions.write_multiple_coils(starting_address, output_values)

        resp_data = self._send_receive(modbus_pdu, slave_addr, False)
        operation_status = functions.validate_resp_data(resp_data, Const.WRITE_MULTIPLE_COILS,
                                                        starting_address, quantity=len(output_values))

        return operation_status

    def write_multiple_registers(self, slave_addr, starting_address, register_values, signed=True):
        modbus_pdu = functions.write_multiple_registers(starting_address, register_values, signed)

        resp_data = self._send_receive(modbus_pdu, slave_addr, False)
        operation_status = functions.validate_resp_data(resp_data, Const.WRITE_MULTIPLE_REGISTERS,
                                                        starting_address, quantity=len(register_values))

        return operation_status

    def close(self):
        if self._uart == None:
            return
        try:
            self._uart.deinit()
        except Exception:
            pass

