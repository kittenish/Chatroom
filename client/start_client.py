# coding="utf-8"
# -*- coding: utf-8 -*-
from client import Client
import sys
import select
import wx
import thread

sys.path.append("../")
import ui

def output(data) :
    sys.stdout.write(data)
    sys.stdout.flush()

class start_client(ui.MyFrame1):

    def __init__(self,parent):
        ui.MyFrame1.__init__(self, parent)

app = wx.App(False)
ChatRoom = start_client(None)
ChatRoom.Show(True)
app.MainLoop()
