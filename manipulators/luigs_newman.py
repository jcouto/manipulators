#! /usr/bin/env python
# Scripts to control Luigs and Newman manipulators
# Tested on the SM 001
#

from .manipulators import *

class LNmanipulator(manipulator, serial_device):
    port = None
    baudrate = 19200
    name =  'Luigs and Newman'

    def __init__(self, port =  None,
                 axislist = [1, 2, 3],
                 axisname =  ['x', 'y', 'z']):
        '''LN manipulator object.
    Opens a connection through a serial port to a Luigs and Newman manipulator
    Tested with the SM 001 manipulator.
        '''
        self._init_logger()
        if port is None:
            self.log('No port specified')
            raise ValueError
        self.port =  port
        # Open serial connection
        portarguments =  {'bytesize': 8,
                          'parity': serial.PARITY_EVEN,
                          'stopbits': 1,
                          'xonxoff': False,
                          'rtscts': False,
                          'dsrdtr': False,
                          'timeout': None,
                          'writeTimeout': None}
        try: 
            self.open_device( **portarguments)
        except: 
            self.log('Could not open device')
            raise
        # Set the axis labels and position
        self.axislist =  axislist
        self.axisname = axisname
        # Set the last axis to be the approach axis 
        self.approachAxis = axislist[-1]
        naxis = len(axislist)
        self.position = np.empty(naxis)
        self.update_position()
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

    def zero(self):
        self.zero_axis(self.axislist)
            
    def send_command(self, cmd, wait_time = 40.0e-6):
        response = None
        self.flush_device()
        # start communication
        reply = self._write_read(STX)
        if (DLE in reply) or (ACK in reply):
            # send command and data link exchange
            reply = self._write_read(STX + cmd + 
                                     self.computeBCC(cmd)+ 
                                     DLE + ETX)
            if (DLE in reply) or (ACK in reply) :
                response = self._write_read(DLE)
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
            self.log('LNmanipulator: Checksum not correct [{0},{1}].\n'.format(
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
            self.log('LNmanipulator: Could not find axis in reply.\n')
            raise ValueError
        return axis,position

    def update_position(self):
        for j,i in enumerate(self.axislist):
            pos_cmd = lambda axis: '#{0}?Z'.format(axis)
            reply = self.send_command(pos_cmd(i))
            ax,position = self.decode_position(reply)
            self.position[j] = position

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
        self.update_position()
        if rel:
            for ax in range(len(new_position)):
                if new_position[ax] != 0:
                    microsteps = self.convert2stepString(new_position[ax])
                    self.send_command('#{0}!D{1}{2}'.format(self.axislist[ax],
                                                            speed, microsteps))

        else:
            for ax in range(len(new_position)):
                if not new_position[ax] == self.position[ax]:
                    microsteps = self.convert2stepString(new_position[ax])
                    self.send_command('#{0}!G{1}{2}'.format(self.axislist[ax],
                                                            speed, microsteps))


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
