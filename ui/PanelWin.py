# -*- coding:utf-8 -*-

import wx


# 窗体
class PanelWin(wx.Window):
    def __init__(self, parent):
        wx.Window.__init__(self, parent, -1, style=wx.SIMPLE_BORDER)
