
#! /usr/bin/env python
# Python scripts to control sensapex manipulators
# Adapted from the code of:
#   Brendan Callahan, Alex Chubykin
#   The Picower Institute for Learning and Memory Massachusetts Institute of Technology
#

# SensaPex Serial Comamnds
DEF_DEV_ID = 0x31
DEF_CU_ID = 0x0F

STX = 0x02
ETX = 0x03
# Functions
WRITE_COMMAND_REG = 0x30   # '0'
READ_STATUS_REG = 0x31	   # '1'
WRITE_SPEED_REG = 0x32	   #'2'
WRITE_DATA_REG = 0x33	   #'3'
READ_DATA_REG = 0x34       #'4'
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

class sensapex_manipulator(manipulator, serial_device):
    port = None
    port_timeout = 500
    baudrate = 115200
    name = 'SensaPEX'

    def __init__(self, port =  None,
                 axislist = [1, 2, 3],
                 axisname =  ['x', 'y', 'z']):
        '''sensapex manipulator object.
    Opens a connection through a serial port to a Luigs and Newman manipulator
    Tested with the SM 001 manipulator.
        '''
        self.name =  'SensaPEX manipulator'
        self._init_logger()
        
        if port is None:
            self.log('No port specified')
            raise ValueError
        self.port =  port
        
        serial = self.serial
        # Open serial connection
        # Set the axis labels and position
        self.axislist =  axislist
        self.axisname = axisname
        # Set the last axis to be the approach axis 
        self.approachAxis = axislist[-1]

        self.position = np.empty(naxis)
#        self.update_position(range(1,naxis + 1))
        return None

