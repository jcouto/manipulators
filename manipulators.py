import sys
import time
import numpy as np
import re
from decimal import Decimal


log =  lambda(txt):sys.stdout.write(txt) 

class serial_device():
    try:
        import serial
    except:
        log('Could not load the serial module (Try pip install pyserial).\n')
    STX = '\x02'
    ETX = '\x03'
    EOT = '\x04'
    ACK = '\x05'
    CR = serial.CR #\x13
    LF = serial.LF #\x10, \n
    NAK = '\x15'
    DLE = '\x10'
    ETB = '\x17'
    # 1 milisecond port timeout
    port_timeout =  100e-3
    wait_time =  20e-3
    dev = None
    def close_device(self): 
        self.dev.close()
        self.dev = None
    def flush_device(self):
        self.dev.flushInput()
        self.dev.flushOutput()
    
class manipulator():
    position =  []
    angle =  []

class LNmanipulator(manipulator, serial_device):
    port = None
    baudrate = 19200
    ESC = '\1B'

    def __init__(self, port =  None, naxis = 3):
        serial = self.serial
        if port is None:
            log('LNmanipulator:  No port specified.\n')
            raise ValueError
        # Open serial connection
        self.port =  port
        try: 
            self.dev = serial.Serial(self.port, baudrate = self.baudrate,
                                     bytesize = 8,
                                     parity = serial.PARITY_EVEN,
                                     stopbits = 1,
                                     xonxoff = False,
                                     rtscts = False,
                                     dsrdtr = False,
                                     timeout = None,
                                     writeTimeout=None)
        except ValueError:
            log('LNmanipulator: bad parameter. Could not open device.  \n')
            raise ValueError
        except serial.SerialException:
            log('LNmanipulator: bad port or wrongly configured.' +
                ' Could not open device.\n')
            raise ValueError
        self.position = np.empty(naxis)
        self.update_position(range(1,naxis + 1))
        return None

    def computeBCC(self,string):
        ''' Compute the BCC for the LN manipulator'''
        xor = reduce(np.bitwise_xor,map(lambda x: ord(x),string))
        # is 8 bit?
        if len(np.binary_repr(xor)) <= 8:
            hiNibble = xor >> 4
            lowNibble = xor & 0x0F
        else:
            log('String XOR is not 8 bit\n')
            raise Exception
        return chr(int('30',16) + hiNibble) + chr(int('30',16)+ lowNibble)
    
    def zero_axis(self,axis = []):
        for ax in axis:
            self.send_command('#{0}!@S'.format(ax))

    def _write_read(self,string):
        '''Low level write wait and read'''
        self.dev.write(string + self.CR)
        time.sleep(self.wait_time)
        reply = self.dev.read(self.dev.inWaiting())
        return reply

    def send_command(self, cmd, wait_time = 40.0e-6):
        response = None
        self.flush_device()
        # start communication
        reply = self._write_read(self.STX)
        if (self.DLE in reply) or (self.ACK in reply):
            # send command and data link exchange
            reply = self._write_read(self.STX + cmd + 
                                     self.computeBCC(cmd)+ 
                                     self.DLE + self.ETX)
            if (self.DLE in reply) or (self.ACK in reply) :
                response = self._write_read(self.DLE)
                # print self._write_read(self.ACK)
            else:
                log('Device not ready to send data.\n')
        else:
            log('Device was not ready.\n')
        return response

    def find_axis(self,string):
        tmp = re.findall('#(\d+)',string)
        if len(tmp) > 0:
            return int(tmp[0])
        else:
            log('LNmanipulator: Could not find axis in reply.\n')
            raise ValueError

    def decode_position(self, string):
        # Check code
        if not (self.computeBCC(string[:-4])==string[:-2][-2:]):
            log('LNmanipulator: Checksum not correct [{0},{1}].\n'.format(
                string[:-4],string[:-2][-2:]))
            raise ValueError
        axis = self.find_axis(string[:-4])
        
        tmp = re.findall('[A-Z]([+-]?\d*.\d+)',string[:-4])
        if len(tmp) > 0:
            # Convert microsteps
            microsteps = float(tmp[0])
            tmp = [int(i) for i in tmp[0].split('.')]
            if microsteps >= 0:
                position = tmp[0]*5.0 + tmp[1]*0.1
            else:
                position = (tmp[0] + 1)*5.0 + (50 - tmp[1])*0.1            
        else:
            log('LNmanipulator: Could not find axis in reply.\n')
            raise ValueError
        return axis,position

    def update_position(self,axislist=[1,2,3]):
        for i in axislist:
            pos_cmd = lambda axis: '#{0}?Z'.format(axis)
            reply = self.send_command(pos_cmd(i))
            ax,position = self.decode_position(reply)
            self.position[ax-1] = position

    def convert2stepString(self, X):
        if not X%5.0:
            microsteps = X/5.0
        else:
            x,y = str(X/5.0).split('.')
            microsteps = np.round(int(y)/2.0)/10.0 + float(x)
        # There has to be a better way to do this...
        return '{0:0=+9.2f}'.format(microsteps)

    def moveXYZ(self,new_position = None, rel = True, speed = 'F'):
        if new_position is None:
            log('LNmanipulator: Must specify new position.\n')
            return
        if rel:
            for ax in range(len(new_position)):
                if new_position[ax] != 0:
                    microsteps = self.convert2stepString(new_position[ax])
                    self.send_command('#{0}!D{1}{2}'.format(ax+1, speed, microsteps))

        else:
            for ax in range(len(new_position)):
                if new_position[ax] != self.position[ax]:
                    microsteps = self.convert2stepString(new_position[ax])
                    self.send_command('#{0}!G{1}{2}'.format(ax+1, speed, microsteps))
        self.update_position()
        return self.position

    def handle_error(self, code):
        errorcodes =  { 'F01': 'Invalid character detected', 
                        'F02': 'BCC not correct', 
                        'F03': 'Device number not valid',
                        'F04': 'Command string for reset not correct',
                        'F05': 'Command string for single step not correct', 
                        'F06': 'Command string for fast speed not correct', 
                        'F07': 'Command string for slow speed not correct', 
                        'F08': 'Command string for Home not correct', 
                        'F09': 'Command string for key lock/unlock not correct',
                        'F0A': 'Command string for Piezo on/off not correct', 
                        'F0B': 'Command string for device on/off not correct', 
                        'F0C': 'Command string for relative distance not correct', 
                        'F0D': 'Command string for absolute distance not correct', 
                        'F0E': 'Command code not recognized', 
                        'F0F': 'Command code not recognized', 
                        'F10': 'String for request not correct',
                        'F11': '"!" or "?" missing',
                        'F12': '"#" missing',
                        'F13': 'Digit expected at this position',
                        'F14': 'ditto',
                        'F15': '"+" or "-" missing',
                        'F16': 'Decimal point missing',
                        'F17': 'Value larger than 30000.00',
                        }
            #F18 .... F1D Internal communication codes of controller (to be neglected)
        return False
