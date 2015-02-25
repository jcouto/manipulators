#! /usr/bin/env python
# Python scripts to control sensapex manipulators
# Adapted from the code of:
#   Brendan Callahan, Alex Chubykin
#   The Picower Institute for Learning and Memory Massachusetts Institute of Technology
#
#Joao Couto 2015

# SensaPex Serial Commands; these are in hexadecimal so that bitwise operations are easier...
DEF_DEV_ID = 0x31
DEF_CU_ID = 0x0F
# Functions
WRITE_COMMAND_REG = 0x30   # '0'
READ_STATUS_REG = 0x31     # '1'
WRITE_SPEED_REG = 0x32     # '2'
WRITE_DATA_REG = 0x33	   # '3'
READ_DATA_REG = 0x34       # '4'
# Commands
GO_ZERO_POSITION = 1
CALIBRATE = 2
VOLTAGE_CALIBRATE = 7

MEM_1 = 10
RET_1 = 11
MEM_2 = 12
RET_2 = 13
MEM_3 = 14
RET_3 = 15

NORMAL_DRIVE_MODE = 18
SNAIL_DRIVE_MODE = 19
PENETRATION_DRIVE_MODE = 20

CALIBRATE_X_AXIS = 21
CALIBRATE_Y_AXIS = 22
CALIBRATE_Z_AXIS = 23

V3_SPEED5_INCREMENT = 500
V3_SPEED4_INCREMENT = 400
V3_SPEED3_INCREMENT = 300
V3_SPEED2_INCREMENT = 64
V3_SPEED1_INCREMENT = 8
V3_SNAIL_INCREMENT = 2

V2_SPEED5_INCREMENT = 128
V2_SPEED4_INCREMENT = 64
V2_SPEED3_INCREMENT = 16
V2_SPEED2_INCREMENT = 8
V2_SPEED1_INCREMENT = 2
V2_SNAIL_INCREMENT = 1

GOING_TO_SLEEP = 24

MEM_3_INCR_X = 31
MEM_3_INCR_Y = 32
MEM_3_INCR_Z = 33
MEM_3_DECR_X = 34
MEM_3_DECR_Y = 35
MEM_3_DECR_Z = 36

# Register addresses
STATUS_REG = 0x01
# Some mode bits in status reg
STATUS_SNAIL_MODE = 0x0100
STATUS_PEN_MODE = 0x0200
STATUS_VIRTUAL_Z = 0x0400

X_SPEED_REG = 0x02
Y_SPEED_REG = 0x03
Z_SPEED_REG = 0x04

INCREMENT_REG = 0x05

X_POSITION_REG = 0x08
Y_POSITION_REG = 0x09
Z_POSITION_REG = 0x0A # 10

MEM_3_STEP = 0x0F # 15

X_AXIS_POS_MEM_1 = 0x10 # 16
Y_AXIS_POS_MEM_1 = 0x11 # 17
Z_AXIS_POS_MEM_1 = 0x12 # 18
X_AXIS_POS_MEM_2 = 0x13 # 19
Y_AXIS_POS_MEM_2 = 0x14 # 20
Z_AXIS_POS_MEM_2 = 0x15 # 21

X_AXIS_POS_MEM_3 = 0x16 # 22, these mem pos registers
Y_AXIS_POS_MEM_3 = 0x17 # 23  for PC usage and
Z_AXIS_POS_MEM_3 = 0x18 # 24, thus not stored permanently

STEP_LENGHT = 0x1F # 31

DEVICE_ID = 0x2B # 43

VERSION_MAJOR_REG = 0x2E # 46
VERSION_MINOR_REG = 0x2F # 47

#typedef struct msg_frame_s
#{
#	unsigned char start;      // 0
#	unsigned char device;     // 1
#	unsigned char function;   // 2
#	unsigned char address[2]; // 3 4
#	unsigned char data[4];    // 5 6 7 8
#	unsigned char crc[4];     // 9 10 11 12
#	unsigned char end;        // 13
#} msg_frame_t;

#define msg_frame_size sizeof(msg_frame_t)
#define msg_frame_data_size (msg_frame_size-6)

class sensapex(manipulator, serial_device):
    port = None
    port_timeout = 500
    baudrate = 115200
    name = 'SensaPEX'

    def __init__(self, port =  None,
                 device = 1,
                 axisname =  ['x', 'y', 'z']):
        '''SensaPEX manipulator object.
    Opens a connection through a serial port to a SENSAPEX manipulator
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
        
        # Open serial connection
        # Set the axis labels and position
        self.axislist =  [1, 2, 3]
        self.axisname = axisname
        self.device = device
        self.position = np.empty(naxis)
        self.update_position(range(1,naxis + 1))
        return None

    def update_position(self):
        for i in self.axislist:
            pos_cmd = lambda axis: '#{0}?Z'.format(axis)
            reply = self.send_command(pos_cmd(i))
            ax,position = self.decode_position(reply)
            self.position[ax-1] = position

ret = umanipulatorctl_read(hndl,dev, X_POSITION_REG);

    def send_command(self, cmd, wait_time = 40e-6):
        self.flush_device()
        msg = STX + cmd + self.checksum(cmd) + ETX
        msg = STX + cmd + self.computeBCC(cmd) + ETX
        reply = self._write_read(msg)

        try:
            del msg
            msg['device'] = reply[1]
            msg['command'] = reply[2]
            msg['address'] = reply[3:5]
            msg['data'] = reply[5:9]
        except:
            print('Could not read message from device {0}.'.format(reply))
            return False
        print msg
        return msg

    def update_position(self):
        for motor in range(0,3):
            if motor == 0:
                address = "0A"
            elif motor == 1:
                address = "08"
            elif motor == 2:
                address = "09"
                
                
            message = int(''.join(self.talk(str(dev)+"4"+address+"0000")[5:9]),16)*self.stepLengthUM
            print "MESSAGE: ",message
            
            if self.parent != None:
                print "##################MESSAGE#########################"
                print self.parent.motorcoordinates
                self.parent.motorcoordinates[self.unitID][dev-1][motor]=copy.deepcopy(message)
                
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

    def checksum(self, message):
        # Compute checksum for sensapex
        # Can be simplified and improved!!
        crc = 0xFFFF
        
        for msgchar in range (0,len(message)):
            crc = ((0xFF00 & crc) | (ord(message[msgchar]) & 0x00FF) ^ (crc & 0x00FF))
            for lask in range (8,0,-1):
                if (crc & 0x0001) == 0:
                    crc >>=1
                else:
                    crc >>=1
                    crc ^= 0xA001
                    
        crcstr = hex(crc)[2:]
        crcupper = ""
        for charnum in range (0,len(crcstr)):
            crcupper += crcstr[charnum].upper()
            
        if len(crcupper) != 4:
            for i in range (len(crcupper),4):
                crcupper = "0"+crcupper
        
        return crcupper
