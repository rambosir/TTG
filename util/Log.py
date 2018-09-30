# -*- coding:utf-8 -*-
import wx


class EventLog(wx.Log):
    def __init__(self, textCtrl, logTime=0):
        wx.Log.__init__(self)
        self.tc = textCtrl
        self.logTime = logTime

    def DoLogText(self, message):
        if self.tc:
            self.tc.SetInsertionPoint(0)
            self.tc.WriteText(message + '\n')
            #self.tc.AppendText(message + '\n')

def WriteText(text):
    if text[-1:] == '\n':
        text = text[:-1]
    wx.LogMessage(text)


write = WriteText
