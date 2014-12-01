#! /usr/bin/env python

import sys
import time
import numpy as np
import re
import serial

STX = '\x02'
ETX = '\x03'
EOT = '\x04'
ACK = '\x06'
CR = serial.CR #\x13
LF = serial.LF #\x10, \n
NAK = '\x15'
DLE = '\x10'
ETB = '\x17'
ESC = '\x1b'


class serial_device(object):
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
        try:
            self.dev.write(string + CR)
        except:
            print('An error occurred when writing to serial.')
            print('Closing device.')
            self.close_device()
        time.sleep(self.wait_time)
        reply = self.dev.read(self.dev.inWaiting())
        return reply


    def close_device(self):
        if self.dev is None:
            print('Device already closed.')
        else: 
            print('Closing device ({0}).'.format(self.dev.port))            
            self.dev.close()
            self.dev = None
            
    def flush_device(self):
        self.dev.flushInput()
        self.dev.flushOutput()
    
    def close(self):
        self.close_device()

    
class manipulator():
    position =  []
    angle =  []
    name =  ''
    axislist =  []
    axisname =  []
    approachAxis =  None
    speed = 'slow'
    
    def _init_logger(self):
        def write_flush(txt):
            sys.stdout.write(txt)
            sys.stdout.flush()       
        self.log =  lambda(txt):write_flush('{0}: {1}.\n'.format(self.name, txt))
                                 
    def zeroAxis(self, axis):
        pass

    def setSpeed(self, speed):
        pass
    
    def moveAbs(self, pos):
        pass

    def setSpeed(self, speed = 'slow'):
        pass

        
