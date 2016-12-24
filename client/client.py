# coding="utf-8"
# -*- coding: utf-8 -*-
import socket
import sys
import wx
import thread
import json
import os
import datetime
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append("../")
from definations import *

class Client(object):

    def __init__(self, host=None, port=None, ip=None):
        self.host = host
        self.port = port
        self.mySocket = None
        self.room = None
        self.threads = None
        self.name = None
        self.ip = ip

    def connectToServer(self):
        try:
            self.mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.mySocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.mySocket.bind( ('127.0.0.1', int(self.ip)) )
            print 'success'
        except socket.error, msg:
            print 'Open socket fail %s' % msg
            sys.exit()

        self.mySocket.connect((self.host, self.port))
        self.mySocket.settimeout(5)
        os.mkdir('/Users/mac/Desktop/计算机网络/chat/file/client/' + self.ip)

    def enter_room(self):

        prepare_mess = {}
        prepare_mess['room'] = self.room
        prepare_mess['name'] = self.name
        prepare_mess['type'] = str(INFO)
        prepare_mess['check'] = hash(str(self.room + self.name)) & 0xffff
        length = str(len(str(prepare_mess))).rjust(4,'0')
        self.mySocket.sendall(length + str(prepare_mess))

    def get_log(self):

        prepare_mess = {}
        prepare_mess['type'] = str(GET_LOG)
        prepare_mess['check'] = hash(str(GET_LOG)) & 0xffff
        length = str(len(str(prepare_mess))).rjust(4,'0')
        self.mySocket.sendall(length + str(prepare_mess))

    def sendMessageToServer(self, message=None):
        self.mySocket.sendall(message)

    def reciverMessageFromServer(self):
        return self.mySocket.recv(4)

    def disconnect(self):
        thread.exit()
        sys.exit()
        self.mySocket.close()

    def leave_room(self):
        prepare_mess = {}
        prepare_mess['type'] = str(LEAVE_ROOM)
        prepare_mess['check'] = hash(str(LEAVE_ROOM)) & 0xffff
        length = str(len(str(prepare_mess))).rjust(4,'0')
        self.mySocket.sendall(length + str(prepare_mess))

    def get_file(self):
        prepare_mess = {}
        prepare_mess['type'] = str(GET_FILE)
        prepare_mess['check'] = hash(str(GET_FILE)) & 0xffff
        length = str(len(str(prepare_mess))).rjust(4,'0')
        self.mySocket.sendall(length + str(prepare_mess))
