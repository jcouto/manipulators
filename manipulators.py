import sys

log =  lambda(txt):sys.stdout.write(txt) 

class serial_commands():
    import serial
    STX = '\x02'
    ETX = '\x03'
    EOT = '\x04'
    ACK = '\x05'
    CR = '\x06'
    LF = '\x0d'
    NAK = '\x15'
    ETB = '\x17'
    # 1 milisecond port timeout
    port_timeout =  1.0e-3
    self.dev = None
    def close_device(self): 
        self.dev.close()
        self.dev = None
    def flush_device(self):
        self.dev.flushInput()
        self.dev.flushOutput()

class manipulator():
    position =  []
    angle =  []

class LNmanipulator(manipulator, serial):
    port = None
    rate = 9600
    def LNmanipulator(self, port =  None):
        if port is None:
            log('LNmanipulator:  No port specified.\n')
            return False
        # Open serial connection
        self.port =  port
        try: 
            self.dev = serial.Serial(self.port, baudrate = 9600,
                                    bytesize = serial.EIGHTBITS,
                                    parity = serial.PARITY_NONE,
                                    stopbits = serial.STOPBITS_ONE,
                                    timeout = self.port_timeout,
                                    writeTimeout=self.port_timeout)
        except ValueError:
            log('LNmanipulator: bad parameter. Could not open device.  \n')
            return False
        except serial.Exception:
            log('LNmanipulator: bad port or wrongly configured. Could not open device.\n')
            return False
        return True

    
    def send_command(self, command, wait_time = 40.0e-6):
        self.flush_device()
        # send STX
        self.dev.write(self.STX)
        time.sleep(wait_time)
        readChar =  self.dev.read(self.dev.inWaiting())
        if (readChar == self.DLE):
            print('Device ready,  sending command')
        else:
            print(readChar)
        return readChar
    
    def update_position(self):
        pass

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
                        'F11': '“!” or “?” missing', 
                        'F12': '“#” missing', 
                        'F13': 'Digit expected at this position', 
                        'F14': 'ditto', 
                        'F15': '“+” or “-“ missing', 
                        'F16': 'Decimal point missing', 
                        'F17': 'Value larger than 30000.00',
                        }
            #F18 .... F1D Internal communication codes of controller (to be neglected)
        if
        return False
