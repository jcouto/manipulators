#! /usr/bin/env python
from argparse import ArgumentParser
import sys
import os
from .luigs_newman import LNmanipulator 
from PyQt4 import QtGui, QtCore 
import atexit
from functools import partial
import socket 
import time

global manipulator
manipulator = None
description = 'Script to interface with the manipulator and create a socket link.'
manipulators = ['LN','sensapex','scientifica']



if sys.platform.startswith('win'):
    default_port = 'COM1'
else:
    default_port = '/dev/usb0'
    
default_socket = 7777
def appendIndependentArguments(parser):
    parser.add_argument('manipulator',metavar='manipulator',
                        choices=manipulators,
                        type=str, 
                        help='Name of the manipulator [{0}]'.format(
                            ','.join(manipulators))
    )
    parser.add_argument('-p','--device-port',
                        type=str,
                        default=default_port,
                        help='Device port [{0}]'.format(default_port))
    parser.add_argument('-s','--server-port',
                        type=int,
                        help='Server socket port number (for example: {0})'.format(
                            default_socket))
@atexit.register
def terminate():
    global manipulator
    if not manipulator is None:
        manipulator.close()

pos_str = lambda(txt):'<font size=30 weight=bold>{0}</font>'.format(str(txt))
class handle_connection(QtCore.QThread):
    def __init__(self, server_socket, manipul_control):
        QtCore.QThread.__init__(self)
        self.function = self.listen
        self.server_socket = server_socket
        self.status = 'listen'
        self.manipulator = manipul_control
    def listen(self):
        (self.client_socket,self.client_address) = self.server_socket.accept()
        self.status = 'connected'
    def echo(self):
        msg  = self.client_socket.recv(1024)
        print(msg)
    def msg_handler(self):
        global manipulator
        msg  = self.client_socket.recv(1024)
        if 'position' in msg:
            reply = []
            axisname = manipulator.axisname
            for name,pos in zip(axisname,manipulator.position):
                reply.append('{0}={1}'.format(name,pos))
            self.client_socket.sendall(','.join(reply))
        
    def run(self):
        while True:
            if self.status == 'listen':
                self.function = self.listen
            elif self.status == 'connected':
                self.function = self.msg_handler
            self.function()
        return

class manipulator_control(QtGui.QDialog):
    def __init__(self,opts):
        global manipulator
        if manipulator is None:
            print('Manipulator not initialized.')
            raise
        super(manipulator_control,self).__init__()
        self.init_window()

        if not opts.server_port is None:
            self.server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.server_socket.bind((socket.gethostname(),opts.server_port))
            self.server_socket.listen(1)
            print('return')
            connection = handle_connection(self.server_socket,self)
            connection.start()
        # To constantly probe position
        self.position_timer = QtCore.QTimer()
        QtCore.QObject.connect(self.position_timer,QtCore.SIGNAL('timeout()'),
                               self.update_position)
        self.timer_period = 1.2*manipulator.wait_time
        self.position_timer.start(self.timer_period)
        self.setFocus()
        self.show()
    def server_socket(self):
        print('Finished.')
    def init_window(self):
        global manipulator
        # Create window programatically
        gax_box = QtGui.QGroupBox('Axis position')
        gcmd_box = QtGui.QGroupBox('Commands')
        moveTab = QtGui.QTabWidget()

        gax_moveAbsBox = QtGui.QWidget()
        gax_moveRelBox = QtGui.QWidget()
        moveTab.addTab(gax_moveAbsBox,'Move absolute')
        moveTab.addTab(gax_moveRelBox,'Move relative')
        self.ax_box = gax_box
        gax_form = QtGui.QFormLayout()
        gcmd_form = QtGui.QFormLayout()
        gax_moveAbsForm = QtGui.QFormLayout()
        gax_moveRelForm = QtGui.QFormLayout()
        self.ax = []
        self.ax_edit = []
        self.ax_rel_edit = []
        self.cmd = []
        font = QtGui.QFont()
        for i,ax in enumerate(manipulator.axisname):
            self.ax_edit.append(QtGui.QLineEdit(str(manipulator.position[i])))
            self.ax_rel_edit.append(QtGui.QLineEdit(str(0.0)))
            self.ax.append(QtGui.QLabel(pos_str(manipulator.position[i])))
            gax_form.addRow(QtGui.QLabel('<font size=30>{0}</font>: '.format(ax)),
                            self.ax[-1])
            gax_moveAbsForm.addRow(QtGui.QLabel('{0}: '.format(ax)),
                                   self.ax_edit[-1])
            gax_moveRelForm.addRow(QtGui.QLabel('{0}: '.format(ax)),
                                   self.ax_rel_edit[-1])
        move_abs_button = QtGui.QPushButton('Go to position')
        move_abs_button.clicked.connect(self.move_absolute_position)
        gax_moveAbsForm.addRow(move_abs_button)
        move_rel_button = QtGui.QPushButton('Advance')
        move_rel_button.clicked.connect(self.move_relative_position)
        gax_moveRelForm.addRow(move_rel_button)

        self.cmd.append(QtGui.QPushButton('ZERO'))
        self.cmd[-1].clicked.connect(manipulator.zero)
        gcmd_form.addRow(self.cmd[-1])
        self.cmd.append(QtGui.QPushButton('Switch speed - (using: {0})'.format(manipulator.speed)))
        self.cmd[-1].clicked.connect(partial(self.switch_speed,self.cmd[-1]))
        gcmd_form.addRow(self.cmd[-1])

        gax_box.setLayout(gax_form)
        gcmd_box.setLayout(gcmd_form)
        gax_moveAbsBox.setLayout(gax_moveAbsForm)
        gax_moveRelBox.setLayout(gax_moveRelForm)
        layout = QtGui.QGridLayout()
        layout.addWidget(gax_box,0,0)
        layout.addWidget(moveTab,0,1)
        layout.addWidget(gcmd_box,1,0)

        self.setLayout(layout)
        self.setWindowTitle('{0} manipulator control'.format(manipulator.name))

    def switch_speed(self, obj):
        global manipulator
        manipulator.switchSpeed()
        obj.setText('Switch speed - (using {0})'.format(manipulator.speed))


    def update_position(self):
        global manipulator
        manipulator.update_position()
        for i,ax in enumerate(self.ax):
            ax.setText(pos_str(manipulator.position[i]))

    def move_absolute_position(self,pos=None):
        self.position_timer.stop()
        global manipulator
        new_pos = manipulator.position.copy()
        if type(pos) is list:
            new_pos = pos
        else:
            for i,ax in enumerate(self.ax_edit):
                try:
                    new_pos[i] = float(ax.text())
                except:
                    print('Invalid position! '+ ax.text())
                    return
        manipulator.move(position=new_pos,relative=False)
        self.position_timer.start(self.timer_period)

    def move_relative_position(self,pos = None):
        self.position_timer.stop()
        global manipulator
        new_pos = manipulator.position.copy()
        if type(pos) is list:
            new_pos = pos
        else:
            for i,ax in enumerate(self.ax_rel_edit):
                try:
                    new_pos[i] = float(ax.text())
                except:
                    print('Invalid position! '+ ax.text())
                    return
        manipulator.move(position=new_pos,relative=True)
        self.position_timer.start(self.timer_period)

def main():
    parser = ArgumentParser(add_help=False)
    appendIndependentArguments(parser)    
    args,unknown = parser.parse_known_args()
    
    parser = ArgumentParser(add_help=True,
                            description = description)
    appendIndependentArguments(parser)

    if args.manipulator.lower() == 'ln':
        parser.add_argument('-l','--axis-list',nargs='+',
                            type=int, default=[1, 2, 3],
                            help='List of axis (for use with LN manipulator)')
        parser.add_argument('-n','--axis-name',nargs='+',
                            type=str, default=['x','y','z'],
                            help='List of axis names (for use with LN manipulator)')
    args = parser.parse_args()
    # Defining it as a global so that I can close it atexit
    global manipulator
    if args.manipulator.lower() == 'ln':
        manipulator = LNmanipulator(port=args.device_port,
                            axislist=args.axis_list,
                            axisname=args.axis_name)
    mainApp = QtGui.QApplication(sys.argv)
    app = manipulator_control(opts = args)
    sys.exit(mainApp.exec_())


if __name__ == '__main__':
    main()
