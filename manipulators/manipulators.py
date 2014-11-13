#! /usr/bin/env python

import sys
import time
import numpy as np
import re
import serial

from decimal import Decimal

STX = 0x02
ETX = 0x03
EOT = 0x04
ACK = 0x06
CR = serial.CR #\x13
LF = serial.LF #\x10, \n
NAK = 0x15
DLE = 0x10
ETB = 0x17
ESC = 0x1b


class serial_device():
    # 100ms port timeout
    port_timeout =  100e-3
    wait_time =  20e-3
    dev = None
    
    def open_device(self, bytesize = 8, parity = serial.PARITY_NONE,
                    stopbits = 1, xonxoff = False,
                    rtscts = False, dsrdtr = False,
                    timeout = None, writeTimeout=None ):
        try: 
            self.dev = serial.Serial(port = self.port, baudrate = self.baudrate,
                                    bytesize = bytesize, 
                                    parity = parity, 
                                    stopbits = stopbits,
                                    xonxoff = xonxoff,
                                    rtscts = rtscts,
                                    dsrdtr = dsrdtr,
                                    timeout = timeout,
                                    writeTimeout=writeTimeout)
        except ValueError:
            print('Bad parameter. Could not open device')
            raise ValueError
        except serial.SerialException:
            print('Bad port or wrongly configured.' +
                ' Could not open device')
            raise OSError
        except OSError:
            print('Bad port ({0}). Could not open device'.format(self.port))
            raise OSError

    def _write_read(self,string):
        '''Low level write wait and read'''
        self.dev.write(string + CR)
        time.sleep(self.wait_time)
        reply = self.dev.read(self.dev.inWaiting())
        return reply

    def close_device(self):
        if self.dev is None:
            print('Device already closed.')
        else: 
            self.dev.close()
            self.dev = None
            
    def flush_device(self):
        self.dev.flushInput()
        self.dev.flushOutput()
    
class manipulator():
    position =  []
    angle =  []
    name =  ''
    axislist =  []
    axisname =  []
    approachAxis =  None
    
    def _init_logger(self):
        self.log =  lambda(txt):[sys.stdout.write('{0}: {1}.\n'.format(self.name), txt),  sys.stdout.flush()]
                        
