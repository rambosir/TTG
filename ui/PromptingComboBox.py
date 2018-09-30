# -*- coding: utf-8 -*-
import wx

# 车次站点auto
class PromptingComboBox(wx.ComboBox):
    def __init__(self, parent, value, choices=[], style=0, **par):
        wx.ComboBox.__init__(self, parent, wx.ID_ANY, value, style=style | wx.CB_DROPDOWN, choices=choices)

        self.choices = par['stations']
        self.sale_time_lbl = par.get('sale_time_lbl')
        self.sale_times = par.get('sale_times')
        # 分别绑定多个事件，文本内容变化，字符输入
        self.Bind(wx.EVT_TEXT, self.EvtText)
        # self.Bind(wx.EVT_CHAR, self.EvtChar)
        self.Bind(wx.EVT_COMBOBOX, self.EvtCombobox)
        self.ignoreEvtText = False

        self.InitChoice()

    # 下拉选择事件
    def EvtCombobox(self, event):

        self.ignoreEvtText = True
        event.Skip()

    def EvtChar(self, event):
        # 这里需要注意一点事，回车键如果不过滤掉的话，EvtText会类似于进入死循环，这里还不太清楚到底是为什么
        if event.GetKeyCode() == 8:
            self.ignoreEvtText = True
        event.Skip()

    def EvtText(self, event):
        #设置鼠标样式
        self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        currentText = self.GetValue()
        if self.sale_time_lbl:
            self.sale_time_lbl.SetLabel(self.sale_times.get(currentText, ''))
            self.sale_time_lbl.SetForegroundColour((0, 0, 255))
            self.sale_time_lbl.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, True, wx.EmptyString))

        # #这里先判断内容是否为空，如果为空的话，需要让下拉菜单隐藏起来
        if not currentText:
            self.InitChoice()
            self.ignoreEvtText = False
            return

        if self.ignoreEvtText:
            self.ignoreEvtText = False
            return

        choiceTemp = []
        found = False

        for choice in self.choices:
            list_choice = list(choice)
            list_choice[0] = list_choice[0].decode('utf-8')
            if currentText in list_choice[0] or currentText in list_choice[2] or currentText in list_choice[3]:
                choiceTemp.append(list_choice[0])

        if choiceTemp:
            self.ignoreEvtText = True
            found = True

        # 进行文本匹配后，如果存在的话，就将combobox的内容置为匹配到的列表,再弹出下拉菜单
        if found:
            self.SetItems(choiceTemp)
            self.Popup()
            self.SetValue(currentText)
            self.SetInsertionPoint(len(currentText))
            # self.ignoreEvtText = True
        if not found:
            self.Dismiss()
            self.SetInsertionPoint(len(currentText))
            event.Skip()

    def InitChoice(self):
        choiceTemp = []
        for choice in self.choices:
            choiceTemp.append(choice[0].decode('utf-8'))

        self.SetItems(choiceTemp)
        self.SetSelection(0)
        self.Dismiss()
