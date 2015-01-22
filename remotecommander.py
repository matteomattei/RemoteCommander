#!/usr/bin/env python

"""
This program open a simple dialog that allows to issue a command to a remote server using SSH.
It needs a configuration file called remotecommander.ini with the following structure:

[GENERAL]
Host = 127.0.0.1
Port = 22
User = root
Password = xxxxx
Command = shutdown -h now
CommandName = SHUTDOWN
"""

import sys, time, socket, configparser, re
import paramiko
from PySide.QtGui import *
from PySide.QtCore import *


class MySignal(QObject):
    sig = Signal(str)


""" This is a thread used to issue commands """
class CommandThread(QThread):
    def __init__(self, parent = None, host='127.0.0.1', port=22, user='root', password='', command=''):
        QThread.__init__(self, parent)
        self.signal = MySignal()
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.command = command

    def run(self):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            #print('connecting to '+self.host+' '+self.user+' '+self.password)
            ssh.connect(self.host, username=self.user, password=self.password)
            #print('command '+self.command)
            stdin, stdout, stderr = ssh.exec_command(self.command)
            result = stdout.read()+stderr.read()
            ssh.close()
            result = result.strip().decode()
            #print(result)
            if len(result) > 0:
                self.signal.sig.emit(result)
            else:
                self.signal.sig.emit('OK')
        except:
            self.signal.sig.emit('ERROR')


"""This is a thread used to monitor the server status"""
class PingThread(QThread):
    def __init__(self, parent = None, host='127.0.0.1', port=22):
        QThread.__init__(self, parent)
        self.signal = MySignal()
        self.host = host
        self.port = port
        self.thread_close = False

    def run(self):
        while True:
            if self.thread_close == True:
                return
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.connect((self.host, self.port))
                self.signal.sig.emit('ONLINE')
            except socket.error:
                self.signal.sig.emit('OFFLINE')
            sock.close()
            time.sleep(1)

 
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self,parent)
        self.Section = None
        self.Host = None
        self.Port = None
        self.User = None
        self.Password = None
        self.Command = None
        self.CommandName = None
        self.pingthread = None
        self.commandthread = None
        self.isPressed = False

        self.setWindowTitle('RemoteCommander')
        self.centralwidget = QWidget(self)
        self.servername = QLabel()
        self.serverstatus = QLabel('OFFLINE')
        self.cmdbutton = QPushButton('CMD',self)
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.servername)
        self.vbox.addWidget(self.serverstatus)
        self.vbox.addWidget(self.cmdbutton)
        self.setCentralWidget(self.centralwidget)
        self.centralwidget.setLayout(self.vbox)

        self.cmdbutton.clicked.connect(self.cmdoperation)
        self.init()
        self.center()

    def center(self):
        self.setFixedSize(250, 150)
        self.servername.setAlignment(Qt.AlignCenter)
        self.servername.setStyleSheet('font-weight: bold; font-size:22px;')
        self.serverstatus.setAlignment(Qt.AlignCenter)
        self.serverstatus.setStyleSheet('font-weight: bold; font-size:22px;')
        self.cmdbutton.setStyleSheet('font-weight: bold; font-size:22px; padding: 10px 0;')
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())
	
    """ Initialize the interface """
    def init(self):
        try:
            config = configparser.ConfigParser()
            config.read('remotecommander.ini')
            self.Section = config.sections()[0]
            self.Host = config[self.Section]['Host']
            self.Port = config[self.Section]['Port']
            self.User = config[self.Section]['User']
            self.Password = config[self.Section]['Password']
            self.Command = config[self.Section]['Command']
            self.CommandName = config[self.Section]['CommandName']
        except:
            msgBox = QMessageBox()
            msgBox.setText('The configuration file has not been properly loaded')
            ret = msgBox.exec_()
            sys.exit(1)

        regex = re.compile("(^rm\s|.*\srm\s|.*;rm\s)")
        if regex.match(self.Command)!=None:
            msgBox = QMessageBox()
            msgBox.setText('You are trying to issue a potential risky remote command: program aborted.')
            ret = msgBox.exec_()
            sys.exit(1)

        self.cmdbutton.setText(self.CommandName)
        self.servername.setText(self.Section)
        self.pingthread = PingThread(self,host=self.Host,port=int(self.Port))
        self.commandthread = CommandThread(self,host=self.Host,port=int(self.Port),user=self.User,password=self.Password,command=self.Command)
        self.pingthread.signal.sig.connect(self.updatehoststatus)
        self.commandthread.signal.sig.connect(self.cmdoperationcomplete)

        self.cmdbutton.setEnabled(False)
        self.pingthread.start()

    def closeEvent(self,event):
        self.pingthread.thread_close = True
        self.pingthread.wait()


    def updatehoststatus(self,data):
        self.serverstatus.setText(data)
        if data == 'ONLINE':
            self.serverstatus.setStyleSheet('font-weight: bold; font-size:22px; color: green')
            if self.isPressed == False:
                self.cmdbutton.setEnabled(True)
        elif data == 'OFFLINE':
            self.serverstatus.setStyleSheet('font-weight: bold; font-size:22px; color: red')
            self.cmdbutton.setEnabled(False)


    def cmdoperation(self):
        self.commandthread.start()
        self.cmdbutton.setEnabled(False)
        self.isPressed = True


    def cmdoperationcomplete(self,data):
        self.isPressed = False
        self.cmdbutton.setEnabled(True)
        msgBox = QMessageBox()
        if data=='ERROR':
            msgBox.setText('ERROR issuing command!!!')
        elif data=='OK':
            msgBox.setText('Command issued correctly!')
        else:
            msgBox.setText(data)
        ret = msgBox.exec_()

 
if __name__=='__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
