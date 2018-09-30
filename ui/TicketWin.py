# -*- coding:utf-8 -*-

# python lib
import cStringIO
import json
import time, threading, thread

# wx lib
import wx
import wx.dataview
import wx.lib.delayedresult
import wx.lib.agw.genericmessagedialog as GMD
import wx.lib.agw.labelbook as LB
from wx.lib.mixins.listctrl import CheckListCtrlMixin
from wx.lib.delayedresult import startWorker

# user lib
import PanelWin
import PopupWin
import OrderWin, ContactsWin
import PromptingComboBox as cb
from TrainTicketGo.util import Req, Common, Log

F = 0


# ----------------------------------------------------------------------------

class Init(LB.LabelBook):
    def __init__(self, parent, *args, **kwargs):
        # headers, passenger_data
        # wx.Listbook.__init__(self, parent=parent, style=wx.BK_DEFAULT)
        LB.LabelBook.__init__(self, parent, -1,
                              agwStyle=LB.INB_BORDER | LB.INB_DRAW_SHADOW | LB.INB_BOLD_TAB_SELECTION | LB.INB_NO_RESIZE)
        self.SetColour(LB.INB_TAB_AREA_BACKGROUND_COLOUR, wx.Colour(240, 240, 240))
        # self.SetColour(LB.INB_TABS_BORDER_COLOUR, wx.Colour(48,165,255))


        imagelist = wx.ImageList(32, 32)
        imagelist.Add(Common.trainBook.Bitmap)
        imagelist.Add(Common.myOrder.Bitmap)
        imagelist.Add(Common.myConcacts.Bitmap)
        self.AssignImageList(imagelist)

        # 赋值给全局变量
        # global HEADERS
        # HEADERS = kwargs['headers']

        # 车票预订Tab
        ticket_win = self.ticket_win = self.makePanel()

        # 判断是否存在12306 CDN
        Common.isExistCdnIp()

        # 我的订单Tab
        orders_win = self.orders_win = self.makePanel()
        OrderWin.Init(parent=orders_win, headers=Common.headers)

        # 用户账户中的联系人集合
        self.passenger_or_msg = kwargs['passenger_data']

        # 我的联系人Tab
        contacts_win = self.contacts_win = self.makePanel()
        ContactsWin.Init(contacts_win, *args, **kwargs)

        # 选择的乘客
        self.passengers, self.passengerTicketStr, self.oldPassengerStr = [], [], []
        # 选择的坐席
        self.seatTypes = []
        # 选择的车次
        self.trains = ticket_win.trains = []

        self.threads = []

        # 所有類型車次、高鐵城軌、動車、直達、特快、快速、其他車（普快、旅游、臨時客車）
        self.ALL, self.GC, self.D, self.Z, self.T, self.K, self.YLP = [], [], [], [], [], [], []

        # 所有席别
        self.SWZ_Col_Width = 50
        self.TDZ_Col_Width = 50
        self.YDZ_Col_Width = 50
        self.EDZ_Col_Width = 50
        self.GJRW_Col_Width = 60
        self.RW_Col_Width = 40
        self.YW_Col_Width = 40
        self.RZ_Col_Width = 40
        self.YZ_Col_Width = 40
        self.WZ_Col_Width = 40
        self.QT_Col_Width = 40

        self.AddPage(ticket_win, Common.tabList[0], True, 0)
        self.AddPage(orders_win, Common.tabList[1], False, 1)
        self.AddPage(contacts_win, Common.tabList[2], False, 2)

        self.gbSizer = ticket_win.gbSizer = gbSizer = wx.GridBagSizer(1, 1)

        # 获取起售时间
        self.saleTimes = Common.GetCitySaleTimeFromLocal()
        # 获取全国站点信息
        self.stations = stations = Common.GetStationFromLocal()

        # 起售時間显示,默认显示北京北
        ticket_win.sale_lbl = self.sale_lbl = wx.StaticText(ticket_win, wx.ID_ANY,
                                                            self.saleTimes[u'北京北'],
                                                            wx.DefaultPosition, wx.DefaultSize,
                                                            wx.ALIGN_LEFT | wx.ALL)
        # 设置字体颜色
        self.sale_lbl.SetForegroundColour((0, 0, 255))
        # 设置字体样式
        self.sale_lbl.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, True, wx.EmptyString))

        ticket_win.start_lbl = wx.StaticText(ticket_win, wx.ID_ANY, u"出发", wx.DefaultPosition, wx.DefaultSize, 0)
        gbSizer.Add(ticket_win.start_lbl, wx.GBPosition(0, 0), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)

        # 出發站點框
        self.start_station = cb.PromptingComboBox(ticket_win, "", [], style=wx.CB_DROPDOWN, stations=stations,
                                                  sale_time_lbl=self.sale_lbl, sale_times=self.saleTimes)
        gbSizer.Add(self.start_station, wx.GBPosition(0, 1), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)

        # 出发站点和目的站点切换
        ticket_win.switch_lbl = self.switch_lbl = wx.StaticBitmap(ticket_win, wx.ID_ANY,
                                                                  Common.switchImage.getBitmap(),
                                                                  wx.DefaultPosition,
                                                                  wx.DefaultSize, 0)
        ticket_win.switch_lbl.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        ticket_win.switch_lbl.Bind(wx.EVT_LEFT_DOWN, self.SwitchStation)
        gbSizer.Add(ticket_win.switch_lbl, wx.GBPosition(0, 2), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)

        ticket_win.arrival_lbl = wx.StaticText(ticket_win, wx.ID_ANY, u"目的", wx.DefaultPosition, wx.DefaultSize, 0)
        gbSizer.Add(ticket_win.arrival_lbl, wx.GBPosition(0, 3), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)

        self.arrival_station = cb.PromptingComboBox(ticket_win, "", [], style=wx.CB_DROPDOWN, stations=stations)
        gbSizer.Add(self.arrival_station, wx.GBPosition(0, 4), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)

        ticket_win.m_staticText6 = wx.StaticText(ticket_win, wx.ID_ANY, u"出发日", wx.DefaultPosition, wx.DefaultSize, 0)
        gbSizer.Add(ticket_win.m_staticText6, wx.GBPosition(0, 5), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)

        ticket_win.departureDay = self.departureDay = wx.DatePickerCtrl(ticket_win, wx.ID_ANY, wx.DefaultDateTime,
                                                                        wx.DefaultPosition,
                                                                        wx.DefaultSize, wx.DP_DROPDOWN,
                                                                        validator=Common.DateValidator())

        nowDate = wx.DateTime().Now()
        maxDate = wx.DateTime().Now().AddDS(wx.DateSpan(0, 0, 0, 60))
        self.departureDay.SetRange(dt1=nowDate, dt2=maxDate)
        gbSizer.Add(ticket_win.departureDay, wx.GBPosition(0, 6), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)

        m_radioBox1Choices = [u"成人", u"学生"]
        self.rd_box = wx.RadioBox(ticket_win, wx.ID_ANY, u"票种", wx.DefaultPosition, wx.DefaultSize, m_radioBox1Choices,
                                  1, wx.RA_SPECIFY_ROWS)
        self.rd_box.SetSelection(0)
        gbSizer.Add(self.rd_box, wx.GBPosition(0, 7), wx.GBSpan(1, 3), wx.ALIGN_CENTER | wx.EXPAND, 5)

        ticket_win.m_staticText7 = wx.StaticText(ticket_win, wx.ID_ANY, u"车次类型", wx.DefaultPosition, wx.DefaultSize, 0)
        gbSizer.Add(ticket_win.m_staticText7, wx.GBPosition(1, 0), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)

        self.list_cc = list_cc = []
        # 車次字典
        self.trainTypeDic = trainTypeDic = dict()

        # 车次
        self.cc_cbs = wx.CheckBox(ticket_win, 1, u'全选', wx.DefaultPosition, wx.DefaultSize, 0)
        self.cc_cbs.SetValue(True)
        gbSizer.Add(self.cc_cbs, wx.GBPosition(1, 1), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)
        self.cc_cbs.Bind(wx.EVT_CHECKBOX, self.onSelectALL)

        ticket_win.gc_cb = wx.CheckBox(ticket_win, wx.ID_ANY, u"GC-高铁/城际", wx.DefaultPosition, wx.DefaultSize, 0)
        ticket_win.gc_cb.SetValue(True)
        gbSizer.Add(ticket_win.gc_cb, wx.GBPosition(1, 2), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)
        list_cc.append(ticket_win.gc_cb)
        trainTypeDic['G,C'] = ticket_win.gc_cb

        ticket_win.dc_cb = wx.CheckBox(ticket_win, wx.ID_ANY, u"D-动车", wx.DefaultPosition, wx.DefaultSize, 0)
        ticket_win.dc_cb.SetValue(True)
        gbSizer.Add(ticket_win.dc_cb, wx.GBPosition(1, 3), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)
        list_cc.append(ticket_win.dc_cb)
        trainTypeDic['D'] = ticket_win.dc_cb

        ticket_win.dc_cb = wx.CheckBox(ticket_win, wx.ID_ANY, u"Z-直达", wx.DefaultPosition, wx.DefaultSize, 0)
        ticket_win.dc_cb.SetValue(True)
        gbSizer.Add(ticket_win.dc_cb, wx.GBPosition(1, 4), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)
        list_cc.append(ticket_win.dc_cb)
        trainTypeDic['Z'] = ticket_win.dc_cb

        ticket_win.tk_cb = wx.CheckBox(ticket_win, wx.ID_ANY, u"T-特快", wx.DefaultPosition, wx.DefaultSize, 0)
        ticket_win.tk_cb.SetValue(True)
        gbSizer.Add(ticket_win.tk_cb, wx.GBPosition(1, 5), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)
        list_cc.append(ticket_win.tk_cb)
        trainTypeDic['T'] = ticket_win.tk_cb

        ticket_win.ks_cb = wx.CheckBox(ticket_win, wx.ID_ANY, u"K-快速", wx.DefaultPosition, wx.DefaultSize, 0)
        ticket_win.ks_cb.SetValue(True)
        gbSizer.Add(ticket_win.ks_cb, wx.GBPosition(1, 6), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)
        list_cc.append(ticket_win.ks_cb)
        trainTypeDic['K'] = ticket_win.ks_cb

        ticket_win.qt_cb = wx.CheckBox(ticket_win, wx.ID_ANY, u"其他", wx.DefaultPosition, wx.DefaultSize, 0)
        ticket_win.qt_cb.SetValue(1)
        gbSizer.Add(ticket_win.qt_cb, wx.GBPosition(1, 7), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)
        list_cc.append(ticket_win.qt_cb)
        trainTypeDic['Y,L,P,S,0,1,2,3,4,5,6,7,8,9'] = ticket_win.qt_cb

        ticket_win.m_fcsj = wx.StaticText(ticket_win, wx.ID_ANY, u"发车时间", wx.DefaultPosition, wx.DefaultSize, 0)
        ticket_win.m_fcsj.Wrap(-1)
        gbSizer.Add(ticket_win.m_fcsj, wx.GBPosition(1, 8), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)

        train_times = [u"00:00--24:00", u"00:00--06:00", u"06:00--12:00", u"12:00--18:00", u"18:00--24:00"]
        ticket_win.train_times_combobox = self.train_times_combobox = wx.ComboBox(ticket_win, wx.ID_ANY,
                                                                                  u"00:00--24:00", wx.DefaultPosition,
                                                                                  wx.DefaultSize,
                                                                                  train_times, wx.CB_READONLY)
        ticket_win.train_times_combobox.Bind(wx.EVT_COMBOBOX, self.TrainTimesComboBox)
        gbSizer.Add(ticket_win.train_times_combobox, wx.GBPosition(1, 9), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)

        # 车次类型点击事件
        for trainShort, trainType in trainTypeDic.items():
            trainType.Bind(wx.EVT_CHECKBOX, lambda evt, ky=trainShort: self.TrainNumberCheck(evt, ky))

        # 席别
        ticket_win.m_staticText9 = wx.StaticText(ticket_win, wx.ID_ANY, u"席别", wx.DefaultPosition, wx.DefaultSize, 0)
        gbSizer.Add(ticket_win.m_staticText9, wx.GBPosition(2, 0), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)

        self.m_xbqx = wx.CheckBox(ticket_win, 2, u"全选", wx.Point(-1, -1), wx.DefaultSize, 0)
        self.m_xbqx.SetValue(True)
        gbSizer.Add(self.m_xbqx, wx.GBPosition(2, 1), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)
        self.m_xbqx.Bind(wx.EVT_CHECKBOX, self.onSelectALL)

        self.dict_seatType = dict_seatType = dict()
        ticket_win.m_swz = wx.CheckBox(ticket_win, wx.ID_ANY, u"商务座", wx.DefaultPosition, wx.DefaultSize, 0)
        ticket_win.m_swz.SetValue(True)
        gbSizer.Add(ticket_win.m_swz, wx.GBPosition(2, 2), wx.GBSpan(1, 1), wx.ALIGN_LEFT, 5)
        dict_seatType[(4, self.SWZ_Col_Width)] = ticket_win.m_swz

        ticket_win.m_tdz = wx.CheckBox(ticket_win, wx.ID_ANY, u"特等座", wx.DefaultPosition, wx.DefaultSize, 0)
        ticket_win.m_tdz.SetValue(True)
        gbSizer.Add(ticket_win.m_tdz, wx.GBPosition(2, 3), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)
        dict_seatType[5, self.TDZ_Col_Width] = ticket_win.m_tdz

        ticket_win.m_ydz = wx.CheckBox(ticket_win, wx.ID_ANY, u"一等座", wx.DefaultPosition, wx.DefaultSize, 0)
        ticket_win.m_ydz.SetValue(True)
        gbSizer.Add(ticket_win.m_ydz, wx.GBPosition(2, 4), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)
        dict_seatType[6, self.YDZ_Col_Width] = ticket_win.m_ydz

        ticket_win.m_edz = wx.CheckBox(ticket_win, wx.ID_ANY, u"二等座", wx.DefaultPosition, wx.DefaultSize, 0)
        ticket_win.m_edz.SetValue(True)
        gbSizer.Add(ticket_win.m_edz, wx.GBPosition(2, 5), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)
        dict_seatType[7, self.EDZ_Col_Width] = ticket_win.m_edz

        ticket_win.m_gjrw = wx.CheckBox(ticket_win, wx.ID_ANY, u"高级软卧", wx.DefaultPosition, wx.DefaultSize, 0)
        ticket_win.m_gjrw.SetValue(True)
        gbSizer.Add(ticket_win.m_gjrw, wx.GBPosition(2, 6), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)
        dict_seatType[8, self.GJRW_Col_Width] = ticket_win.m_gjrw

        ticket_win.m_rw = wx.CheckBox(ticket_win, wx.ID_ANY, u"软卧", wx.DefaultPosition, wx.DefaultSize, 0)
        ticket_win.m_rw.SetValue(True)
        gbSizer.Add(ticket_win.m_rw, wx.GBPosition(2, 7), wx.GBSpan(1, 1), wx.ALIGN_LEFT, 5)
        dict_seatType[9, self.RW_Col_Width] = ticket_win.m_rw

        ticket_win.m_yw = wx.CheckBox(ticket_win, wx.ID_ANY, u"硬卧", wx.DefaultPosition, wx.DefaultSize, 0)
        ticket_win.m_yw.SetValue(True)
        gbSizer.Add(ticket_win.m_yw, wx.GBPosition(2, 8), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)
        dict_seatType[10, self.YW_Col_Width] = ticket_win.m_yw

        # ticket_win.m_dw = wx.CheckBox(ticket_win, wx.ID_ANY, u"动卧", wx.DefaultPosition, wx.DefaultSize, 0)
        # ticket_win.m_dw.SetValue(True)
        # gbSizer.Add(ticket_win.m_dw, wx.GBPosition(2, 9), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)
        # dict_seatType['11'] = ticket_win.m_dw
        #
        # ticket_win.m_gjdw = wx.CheckBox(ticket_win, wx.ID_ANY, u"高级动卧", wx.DefaultPosition, wx.DefaultSize, 0)
        # ticket_win.m_gjdw.SetValue(True)
        # gbSizer.Add(ticket_win.m_gjdw, wx.GBPosition(2,10), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)
        # dict_seatType['12'] = ticket_win.m_gjdw

        ticket_win.m_rz = wx.CheckBox(ticket_win, wx.ID_ANY, u"软座", wx.DefaultPosition, wx.DefaultSize, 0)
        ticket_win.m_rz.SetValue(True)
        gbSizer.Add(ticket_win.m_rz, wx.GBPosition(2, 9), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)
        dict_seatType[11, self.RZ_Col_Width] = ticket_win.m_rz

        ticket_win.m_yz = wx.CheckBox(ticket_win, wx.ID_ANY, u"硬座", wx.DefaultPosition, wx.DefaultSize, 0)
        ticket_win.m_yz.SetValue(True)
        gbSizer.Add(ticket_win.m_yz, wx.GBPosition(2, 10), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)
        dict_seatType[12, self.YZ_Col_Width] = ticket_win.m_yz

        ticket_win.m_wz = wx.CheckBox(ticket_win, wx.ID_ANY, u"无座", wx.DefaultPosition, wx.DefaultSize, 0)
        ticket_win.m_wz.SetValue(True)
        gbSizer.Add(ticket_win.m_wz, wx.GBPosition(2, 11), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)
        dict_seatType[13, self.WZ_Col_Width] = ticket_win.m_wz

        ticket_win.m_qt = wx.CheckBox(ticket_win, wx.ID_ANY, u"其他", wx.DefaultPosition, wx.DefaultSize, 0)
        ticket_win.m_qt.SetValue(True)
        gbSizer.Add(ticket_win.m_qt, wx.GBPosition(2, 12), wx.GBSpan(1, 1), wx.ALIGN_CENTER, 5)
        dict_seatType[14, self.QT_Col_Width] = ticket_win.m_qt

        # 坐席类型点击事件
        for tuple_key, seatType_cb in dict_seatType.items():
            seatType_cb.Bind(wx.EVT_CHECKBOX, lambda evt, key=tuple_key: self.SeatTypeCheck(evt, key))

        self.query_btn = ticket_win.btn = wx.Button(ticket_win, wx.ID_ANY, u"查询", wx.DefaultPosition, wx.DefaultSize, 0)
        gbSizer.Add(ticket_win.btn, wx.GBPosition(0, 10), wx.GBSpan(2, 3), wx.ALIGN_CENTER | wx.EXPAND, 5)
        ticket_win.Bind(wx.EVT_BUTTON, self.QueryTicket, ticket_win.btn)

        # 分割线
        ticket_win.split_line = wx.StaticLine(ticket_win, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                              wx.LI_HORIZONTAL)
        gbSizer.Add(ticket_win.split_line, wx.GBPosition(3, 0), wx.GBSpan(1, 13), wx.EXPAND | wx.ALL, 5)

        # 显示相关站点起售时间
        ticket_win.sale_time_lbl = wx.StaticText(ticket_win, wx.ID_ANY, u"起售时间：", wx.DefaultPosition, wx.DefaultSize,
                                                 wx.ALIGN_CENTER | wx.ALL)
        gbSizer.Add(ticket_win.sale_time_lbl, wx.GBPosition(4, 0), wx.GBSpan(1, 1), wx.ALIGN_CENTER | wx.ALL, 5)

        # 根据选择站点显示起售时间
        gbSizer.Add(ticket_win.sale_lbl, wx.GBPosition(4, 1), wx.GBSpan(1, 1), wx.ALIGN_CENTER | wx.ALL, 5)

        gbSizer.AddSpacer((0, 0), wx.GBPosition(4, 2), wx.GBSpan(1, 1), wx.EXPAND, 5)
        gbSizer.AddSpacer((0, 0), wx.GBPosition(4, 3), wx.GBSpan(1, 1), wx.EXPAND, 5)

        # 高级软卧票价显示
        ticket_win.price_lbl = price_lbl = wx.StaticText(ticket_win, wx.ID_ANY, wx.EmptyString,
                                                         wx.DefaultPosition, wx.DefaultSize,
                                                         wx.ALIGN_CENTER | wx.ALL)
        # 设置字体颜色
        price_lbl.SetForegroundColour('#fc8302')
        gbSizer.Add(price_lbl, wx.GBPosition(4, 4), wx.GBSpan(1, 8), wx.ALL | wx.EXPAND, 5)

        # 订票乘车人
        ticket_win.passenger_lbl = wx.StaticText(ticket_win, wx.ID_ANY, u"乘车人：", wx.DefaultPosition, wx.DefaultSize,
                                                 wx.ALIGN_CENTER | wx.ALL)
        gbSizer.Add(ticket_win.passenger_lbl, wx.GBPosition(6, 0), wx.GBSpan(1, 1), wx.ALIGN_CENTER | wx.ALL, 5)

        ticket_win.passenger_txt = wx.TextCtrl(ticket_win, -1, '',
                                               size=(-1, 30), style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)
        # ticket_win.passenger_txt.Enable(False)
        arrowCursor = wx.StockCursor(wx.CURSOR_ARROW)
        # ticket_win.passenger_txt.SetEditable(False)
        ticket_win.passenger_txt.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT))
        ticket_win.passenger_txt.SetCursor(arrowCursor)
        gbSizer.Add(ticket_win.passenger_txt, wx.GBPosition(6, 1), wx.GBSpan(1, 11), wx.EXPAND, 5)

        ticket_win.passenger_btn = wx.StaticText(ticket_win, wx.ID_ANY, u"选择乘客", wx.DefaultPosition, wx.DefaultSize, 0)
        ticket_win.passenger_btn.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, True, wx.EmptyString))
        ticket_win.passenger_btn.SetForegroundColour(wx.Colour(0, 0, 255))
        ticket_win.passenger_btn.SetToolTipString(u"选择需要订票的联系人")

        myCursor = wx.StockCursor(wx.CURSOR_HAND)
        ticket_win.passenger_btn.SetCursor(myCursor)
        ticket_win.passenger_btn.Bind(wx.EVT_LEFT_DOWN, self.ChoicePassenger)
        gbSizer.Add(ticket_win.passenger_btn, wx.GBPosition(6, 12), wx.GBSpan(1, 1), wx.ALIGN_CENTER | wx.ALL, 5)

        ticket_win.train_lbl = wx.StaticText(ticket_win, wx.ID_ANY, u"车次号：", wx.DefaultPosition, wx.DefaultSize,
                                             wx.ALIGN_CENTER | wx.ALL)
        gbSizer.Add(ticket_win.train_lbl, wx.GBPosition(7, 0), wx.GBSpan(1, 1), wx.ALIGN_CENTER | wx.ALL, 5)

        ticket_win.train_txt = self.train_txt = wx.TextCtrl(ticket_win, -1, '',
                                                            size=(-1, 30),
                                                            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)
        ticket_win.train_txt.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT))
        # ticket_win.train_txt.Enable(False)
        ticket_win.train_txt.SetCursor(arrowCursor)
        gbSizer.Add(ticket_win.train_txt, wx.GBPosition(7, 1), wx.GBSpan(1, 11), wx.EXPAND, 5)

        ticket_win.clear_train_btn = wx.StaticText(ticket_win, wx.ID_ANY, u"清空", wx.DefaultPosition, wx.DefaultSize, 0)
        ticket_win.clear_train_btn.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, True, wx.EmptyString))
        ticket_win.clear_train_btn.SetForegroundColour(wx.Colour(0, 0, 255))
        ticket_win.clear_train_btn.SetToolTipString(u"清空已选车次")

        myCursor = wx.StockCursor(wx.CURSOR_HAND)
        ticket_win.clear_train_btn.SetCursor(myCursor)
        ticket_win.clear_train_btn.Bind(wx.EVT_LEFT_DOWN, self.ClearTrain)
        gbSizer.Add(ticket_win.clear_train_btn, wx.GBPosition(7, 12), wx.GBSpan(1, 1), wx.ALIGN_CENTER | wx.ALL, 5)

        ticket_win.train_seat_lbl = wx.StaticText(ticket_win, wx.ID_ANY, u"坐席：", wx.DefaultPosition, wx.DefaultSize,
                                                  wx.ALIGN_CENTER | wx.ALL)
        gbSizer.Add(ticket_win.train_seat_lbl, wx.GBPosition(8, 0), wx.GBSpan(1, 1), wx.ALIGN_CENTER | wx.ALL, 5)

        ticket_win.train_seat_txt = wx.TextCtrl(ticket_win, -1, '',
                                                size=(-1, 30), style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)
        # ticket_win.train_seat_txt.Enable(False)
        ticket_win.train_seat_txt.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT))
        ticket_win.train_seat_txt.SetCursor(arrowCursor)
        gbSizer.Add(ticket_win.train_seat_txt, wx.GBPosition(8, 1), wx.GBSpan(1, 11), wx.EXPAND, 5)

        ticket_win.clear_train_btn = wx.StaticText(ticket_win, wx.ID_ANY, u"选择坐席", wx.DefaultPosition, wx.DefaultSize,
                                                   0)
        ticket_win.clear_train_btn.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, True, wx.EmptyString))
        ticket_win.clear_train_btn.SetForegroundColour(wx.Colour(0, 0, 255))
        ticket_win.clear_train_btn.SetToolTipString(u"选择乘坐车次席别")

        myCursor = wx.StockCursor(wx.CURSOR_HAND)
        ticket_win.clear_train_btn.SetCursor(myCursor)
        ticket_win.clear_train_btn.Bind(wx.EVT_LEFT_DOWN, self.ChoiceSeatType)
        gbSizer.Add(ticket_win.clear_train_btn, wx.GBPosition(8, 12), wx.GBSpan(1, 1), wx.ALIGN_CENTER | wx.ALL, 5)

        ticket_win.log_lbl = wx.StaticText(ticket_win, wx.ID_ANY, u"日志输出：", wx.DefaultPosition, wx.DefaultSize,
                                           wx.ALIGN_CENTER | wx.ALL)
        gbSizer.Add(ticket_win.log_lbl, wx.GBPosition(9, 0), wx.GBSpan(1, 1), wx.ALIGN_CENTER | wx.ALL, 5)

        ticket_win.log_txt = wx.TextCtrl(ticket_win, -1, '',
                                         size=(500, 100), style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH)
        gbSizer.Add(ticket_win.log_txt, wx.GBPosition(9, 1), wx.GBSpan(1, 11), wx.ALIGN_LEFT | wx.ALL, 5)

        wx.Log_SetActiveTarget(Log.EventLog(ticket_win.log_txt))
        wx.LogMessage(u'初始化完毕')

        self.order_btn = ticket_win.order_btn = wx.Button(ticket_win, wx.ID_ANY, u"开始订票", wx.DefaultPosition,
                                                          wx.DefaultSize,
                                                          wx.ALIGN_CENTER | wx.ALL)
        gbSizer.Add(ticket_win.order_btn, wx.GBPosition(9, 12), wx.GBSpan(1, 1), wx.ALIGN_LEFT | wx.ALL, 5)
        ticket_win.Bind(wx.EVT_BUTTON, self.StartBuyTicket, ticket_win.order_btn)

        # # 设置可排序
        # for c in self.dvlc.Columns:
        #     c.Sortable = True
        #     c.Reorderable = False
        #     c.Resizeable = False
        #

        self.list = list = CheckListCtrl(ticket_win)

        list.InsertColumn(0, u'车次', wx.LIST_FORMAT_CENTER, 65)
        list.InsertColumn(1, u'出站-到站', wx.LIST_FORMAT_CENTER, 110)
        list.InsertColumn(2, u'出发-到达(时间)', wx.LIST_FORMAT_CENTER, 100)
        list.InsertColumn(3, u'历时', wx.LIST_FORMAT_CENTER, 50)
        list.InsertColumn(4, u'商务座', wx.LIST_FORMAT_CENTER, self.SWZ_Col_Width)
        list.InsertColumn(5, u'特等座', wx.LIST_FORMAT_CENTER, self.TDZ_Col_Width)
        list.InsertColumn(6, u'一等座', wx.LIST_FORMAT_CENTER, self.YDZ_Col_Width)
        list.InsertColumn(7, u'二等座', wx.LIST_FORMAT_CENTER, self.EDZ_Col_Width)
        list.InsertColumn(8, u'高级软卧', wx.LIST_FORMAT_CENTER, self.GJRW_Col_Width)
        list.InsertColumn(9, u'软卧', wx.LIST_FORMAT_CENTER, self.RW_Col_Width)
        list.InsertColumn(10, u'硬卧', wx.LIST_FORMAT_CENTER, self.YW_Col_Width)
        list.InsertColumn(11, u'软座', wx.LIST_FORMAT_CENTER, self.RZ_Col_Width)
        list.InsertColumn(12, u'硬座', wx.LIST_FORMAT_CENTER, self.YZ_Col_Width)
        list.InsertColumn(13, u'无座', wx.LIST_FORMAT_CENTER, self.WZ_Col_Width)
        list.InsertColumn(14, u'其他', wx.LIST_FORMAT_CENTER, self.QT_Col_Width)
        list.InsertColumn(15, u'备注', wx.LIST_FORMAT_CENTER, 80)
        list.InsertColumn(16, u'车次编号', wx.LIST_FORMAT_CENTER, 0)
        list.InsertColumn(17, u'Web可否购买', wx.LIST_FORMAT_CENTER, 0)
        list.InsertColumn(18, u'车次密钥', wx.LIST_FORMAT_CENTER, 0)
        list.InsertColumn(19, u'坐席类型', wx.LIST_FORMAT_CENTER, 0)
        list.InsertColumn(20, u'出发站编号', wx.LIST_FORMAT_CENTER, 0)
        list.InsertColumn(21, u'到达站编号', wx.LIST_FORMAT_CENTER, 0)
        list.InsertColumn(22, u'出发站电报码', wx.LIST_FORMAT_CENTER, 0)
        list.InsertColumn(23, u'到达站电报码', wx.LIST_FORMAT_CENTER, 0)
        list.InsertColumn(24, u'车次是否受控', wx.LIST_FORMAT_CENTER, 0)

        gbSizer.Add(self.list, wx.GBPosition(5, 0), wx.GBSpan(1, 13), wx.EXPAND, 5)

        ticket_win.SetSizer(gbSizer)
        ticket_win.Layout()

        self.Bind(wx.EVT_LISTBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_LISTBOOK_PAGE_CHANGING, self.OnPageChanging)

    # 开始订票
    def StartBuyTicket(self, event):

        if not self.passengerTicketStr or not self.oldPassengerStr or not self.trains:
            wx.MessageBox(u'请检查乘客、坐席、车次是否已设置ok')
            return

        if not self.threads:
            ticketThread = Common.TicketThread(self.BuyingTicket)
            self.threads.append(ticketThread)

        global F
        if F:
            F = 0
            self.order_btn.SetLabel(u'开始订票')
            wx.LogMessage(u'取消订票...')
            for t in self.threads:
                t.Stop()
                self.threads.remove(t)
            # 清除订单验证码dialog
            childs = self.GetChildren()
            if childs:
                for c in childs:
                    if c.GetId() == 99:
                        c.Destroy()
        else:
            F = 1
            self.order_btn.SetLabel(u'停止订票')
            wx.LogMessage(u'开始订票...')
            for t in self.threads:
                t.Start()

                # self.BuyingTicket()
                # 订票中

    def BuyingTicket(self):
        global F

        # print(self.passengerTicketStr)
        # print(self.oldPassengerStr)
        # print(self.passengers)
        # self.train_txt.Clear()
        # print(self.seatTypes)

        # 获取子窗体，判断是否存在验证码窗体，存在则销毁
        childs = self.GetChildren()
        if childs:
            for c in childs:
                if c.GetId() == 99:
                    c.Destroy()

        # 旅程类型，如：tour_flag:表示单程[dc]/往程[wc]/返程[fc]/改签[gc]
        tour_flag = 'dc'
        train_date = self.departureDay.GetValue()
        train_date = train_date.Format('%Y-%m-%d')

        # 成人 or 学生
        purpose_codes = 'ADULT' if self.rd_box.GetSelection() == 0 else '0X00'
        # 起始站
        # query_from_station_name = self.start_station.GetValue()
        # 目的站
        # query_to_station_name = self.arrival_station.GetValue()
        #
        cancel_flag = '2'
        bed_level_order_num = '000000000000000000000000000000'

        # 订单提交请求参数
        auto_submit_params, queue_params, ticket_count_params = {}, {}, {}
        auto_submit_params['train_date'] = train_date
        auto_submit_params['tour_flag'] = tour_flag
        auto_submit_params['purpose_codes'] = purpose_codes
        auto_submit_params[''] = ''
        auto_submit_params['cancel_flag'] = cancel_flag
        auto_submit_params['bed_level_order_num'] = bed_level_order_num

        # 获取当前时间时分秒
        nowtime = time.localtime()
        concact_datetime = train_date + str(nowtime[3]) + ':' + str(nowtime[4]) + ':' + str(nowtime[5])
        # 转换时间类型
        new_time = time.strptime(concact_datetime, '%Y-%m-%d%H:%M:%S')
        # 格式化
        fmt_time = time.strftime('%a %b %d %Y %H:%M:%S GMT+0800 (中国标准时间)', new_time)
        queue_params['train_date'] = fmt_time
        queue_params['purpose_codes'] = purpose_codes

        # 查票
        ret_data = self.QueryTicketData()
        data = ret_data.get('data')
        if data:
            for d in data:
                # 密令
                secretStr = d.get('secretStr')
                # 预订按钮
                bti = u'可预订' if d.get('buttonTextInfo') == u'预订' else d.get('buttonTextInfo')
                dto = d.get('queryLeftNewDTO')
                # 车次编号
                train_no = dto.get('train_no')
                # 车次编码
                station_train_code = dto.get('station_train_code')

                # 出发地电报码
                start_station_telecode = dto.get('start_station_telecode')
                # 出发地
                start_station_name = dto.get('start_station_name')
                # 目的地电报码
                end_station_telecode = dto.get('end_station_telecode')
                # 目的地
                end_station_name = dto.get('end_station_name')

                # 出发地电报码
                from_station_telecode = dto.get('from_station_telecode')

                # 目的地电报码
                to_station_telecode = dto.get('to_station_telecode')

                # 出发时间
                start_time = dto.get('start_time')
                # 到达时间
                arrive_time = dto.get('arrive_time')
                # 历时
                lishi = dto.get('lishi')
                # 是否web页面可购买
                canWebBuy = dto.get('canWebBuy')

                # 坐席类型
                seat_types = dto.get('seat_types')

                # 出发站编号
                from_station_no = dto.get('from_station_no')

                # 到达站编号
                to_station_no = dto.get('to_station_no')
                # ticket
                yp_info = dto.get('yp_info')

                # "gg_num": "--",
                # "yb_num": "--",
                # 商务座
                swz_num = self.isZero(dto.get('swz_num'))
                ticket_count_params['9'] = swz_num
                # 特等座
                tz_num = self.isZero(dto.get('tz_num'))
                ticket_count_params['P'] = tz_num
                # 一等座
                zy_num = self.isZero(dto.get('zy_num'))
                ticket_count_params['M'] = zy_num
                # 二等座
                ze_num = self.isZero(dto.get('ze_num'))
                ticket_count_params['O'] = ze_num
                # 高级软卧
                gr_num = self.isZero(dto.get('gr_num'))
                ticket_count_params['6'] = gr_num
                # 软卧
                rw_num = self.isZero(dto.get('rw_num'))
                ticket_count_params['4'] = rw_num
                # 硬卧
                yw_num = self.isZero(dto.get('yw_num'))
                ticket_count_params['3'] = yw_num
                # 软座
                rz_num = self.isZero(dto.get('rz_num'))
                ticket_count_params['2'] = rz_num
                # 硬座
                yz_num = self.isZero(dto.get('yz_num'))
                ticket_count_params['1'] = yz_num
                # 无座
                wz_num = self.isZero(dto.get('wz_num'))
                ticket_count_params['WZ'] = wz_num
                # 其他
                qt_num = self.isZero(dto.get('qt_num'))

                # 所选车次
                for train in self.trains:
                    if station_train_code == train:
                        auto_submit_params['secretStr'] = Req.unquote(secretStr)
                        auto_submit_params['query_from_station_name'] = start_station_name
                        auto_submit_params['query_to_station_name'] = end_station_name

                        for index, seattype in enumerate(self.seatTypes):
                            for k, v in seattype.items():
                                if k in seat_types and ticket_count_params[k]:
                                    print(ticket_count_params[k])

                                    auto_submit_params['passengerTicketStr'] = self.passengerTicketStr[index]
                                    auto_submit_params['oldPassengerStr'] = self.oldPassengerStr[index]
                                    auto_submit_params = Common.encoded_dict(auto_submit_params)
                                    # 发起订单提交请求
                                    auto_submit_rs = Req.post(Common.auto_submit_url, auto_submit_params,
                                                              Common.headers)
                                    auto_submit_uzipped = Req.zippedDecompress(auto_submit_rs)
                                    print('auto_submit_uzipped:')
                                    print(auto_submit_uzipped)
                                    if auto_submit_uzipped:
                                        # 获取订单请求响应内容并转换成json对象
                                        auto_submit_json = json.loads(auto_submit_uzipped)
                                        auto_submit_status = auto_submit_json.get('status')
                                        auto_submit_message = auto_submit_json.get('messages')
                                        auto_submit_data = auto_submit_json.get('data')

                                        if auto_submit_message:
                                            wx.LogMessage(u'订票失败，原因【%s】' % auto_submit_message[0])
                                            self.order_btn.SetLabel(u'开始订票')
                                            for t in self.threads:
                                                t.Stop()
                                                self.threads.remove(t)
                                            F = 0
                                            return

                                        # 请求成功
                                        if auto_submit_status and not auto_submit_message:
                                            auto_submit_result = auto_submit_data['result']
                                            print(auto_submit_data)
                                            # auto_submit_isNeedPassCode = auto_submit_data['isNeedPassCode']
                                            ifShowPassCode = auto_submit_data['ifShowPassCode']
                                            auto_submit_submitStatus = auto_submit_data['submitStatus']
                                            canChooseBeds = auto_submit_data.get('canChooseBeds')
                                            canChooseSeats = auto_submit_data.get('canChooseSeats')
                                            choose_Seats = auto_submit_data.get('choose_Seats')
                                            isCanChooseMid = auto_submit_data.get('isCanChooseMid')

                                            auto_submit_result_list = auto_submit_result.split('#')
                                            print(auto_submit_result_list)

                                            queue_params['train_no'] = train_no
                                            queue_params['stationTrainCode'] = station_train_code
                                            queue_params['seatType'] = k
                                            queue_params['fromStationTelecode'] = from_station_telecode
                                            queue_params['toStationTelecode'] = to_station_telecode
                                            queue_params['leftTicket'] = yp_info
                                            # queue_params['_json_att'] = ''
                                            queue_params['isCheckOrderInfo'] = ''
                                            queue_params = Common.encoded_dict(queue_params)

                                            # 发起查询提交订单当前队列人数请求
                                            queue_rs = Req.post(Common.queue_url, queue_params, Common.headers)
                                            queue_uzipped = Req.zippedDecompress(queue_rs)
                                            print('queue_uzipped:')
                                            print(queue_uzipped)
                                            if queue_uzipped:
                                                queue_json = json.loads(queue_uzipped)
                                                queue_status = queue_json.get('status')
                                                queue_messages = queue_json.get('messages')
                                                queue_data = queue_json.get('data')
                                                # 正常返回
                                                if queue_status and queue_data:
                                                    # 当前队列排队count数
                                                    queue_data_count = queue_data.get('count')

                                                    # 暫停當前列表中的綫程
                                                    for t in self.threads:
                                                        t.Stop()
                                                        self.threads.remove(t)

                                                    # 如果需要验证码，显示订单验证码框
                                                    if auto_submit_submitStatus and ifShowPassCode == 'Y':

                                                        wx.CallAfter(self.showPassengerCode, yp_info=yp_info,
                                                                     auto_submit_params=auto_submit_params,
                                                                     auto_submit_result_list=auto_submit_result_list,
                                                                     queue_data=queue_data)
                                                    else:

                                                        wx.CallAfter(self.TicketGo4NCode, auto_submit_params,
                                                                     auto_submit_result_list)

                                                        # 输出日志 系统繁忙，请稍候再试！

    # 直接提交订单，无需验证码
    def TicketGo4NCode(self, submit_params, submit_result_list):
        wx.LogMessage(u'①开始提交订单...')
        # 组装：提交订单确认队列参数
        confirm_single_params = {'passengerTicketStr': submit_params['passengerTicketStr'],
                                 'oldPassengerStr': submit_params['oldPassengerStr'], 'randCode': '',
                                 'purpose_codes': submit_params['purpose_codes'],
                                 'key_check_isChange': submit_result_list[1],
                                 'leftTicketStr': submit_result_list[2],
                                 'train_location': submit_result_list[0],
                                 'choose_seats': '',
                                 'seatDetailType': '',
                                 '_json_att': ''
                                 }
        # 提交是否可以排队请求
        confirm_single_rs = Req.post(Common.confirm_single_for_queue_url, confirm_single_params, Common.headers)
        confirm_single_unzipped = Req.zippedDecompress(confirm_single_rs)
        print('confirm_single_unzipped:')
        print(confirm_single_unzipped)
        if confirm_single_unzipped:
            wx.LogMessage(u'订单提交成功')
            wx.LogMessage(u'②开始获取订单...')
            confirm_single_json = json.loads(confirm_single_unzipped)
            confirm_single_status = confirm_single_json.get('status')
            confirm_single_messages = confirm_single_json.get('messages')
            confirm_single_data = confirm_single_json.get('data')
            # 订单确认成功返回
            if confirm_single_status and confirm_single_data.get('submitStatus'):
                # 获取订单号
                order_time_params = {'random': str(time.mktime(time.localtime())),
                                     'tourFlag': submit_params['tour_flag'], '_json_att': ''}
                order_time_rs = Req.post(Common.query_order_waittime_url, order_time_params, Common.headers)
                order_time_unzipped = Req.zippedDecompress(order_time_rs)
                if order_time_unzipped:
                    order_time_json = json.loads(order_time_unzipped)
                    order_time_status = order_time_json.get('status')
                    order_time_data = order_time_json.get('data')
                    # 判断是否成功响应
                    if order_time_status and order_time_data and order_time_data.get(
                            'queryOrderWaitTimeStatus'):
                        # wx.LogMessage(u'正在获取订单号...')
                        # order_time_status = order_time_data.get('queryOrderWaitTimeStatus')
                        request_id = order_time_data.get('requestId')
                        msg = order_time_data.get('msg')
                        # 获取订单号
                        order_id = order_time_data.get('orderId')
                        if msg:
                            wx.LogMessage(u'获取订单号失败，原因：【%s】' % msg)
                            # self.OnCloseWindow(None, win_obj)
                            self.endOrder()
                            return

                        # 获取订单如果失败，继续获取
                        if not order_id:
                            count = 0
                            while count < 3:
                                time.sleep(3)
                                count += 1
                                print('order_time_params----%s' % order_time_params)
                                order_time_rs = Req.post(Common.query_order_waittime_url,
                                                         order_time_params, Common.headers)
                                order_time_unzipped = Req.zippedDecompress(order_time_rs)
                                print(order_time_unzipped)
                                order_time_json = json.loads(order_time_unzipped)
                                order_time_data = order_time_json.get('data')
                                wx.LogMessage(u'正在获取订单号...')

                                if order_time_data.get('orderId'):
                                    order_id = order_time_data.get('orderId')
                                    break

                        if order_id:
                            wx.LogMessage(u'获取订单号成功，订单号为：%s' % (order_id))
                            # 查询订单结果
                            data = {'orderSequence_no': order_id, '_json_att': ''}
                            order_for_dcqueue_rs = Req.post(Common.order_for_dcqueue_url, data, Common.headers)
                            order_for_dcqueue_unzipped = Req.zippedDecompress(order_for_dcqueue_rs)
                            print('order_for_dcqueue_unzipped:', order_for_dcqueue_unzipped)
                            if order_for_dcqueue_unzipped:
                                order_for_dcqueue_json = json.loads(order_for_dcqueue_unzipped)
                                status = order_for_dcqueue_json.get('status')
                                data = order_for_dcqueue_json.get('data')
                                if status and data and data.get('submitStatus'):
                                    # f = 0
                                    wx.LogMessage(u'恭喜您，订票成功，赶紧去支付吧')
                                    try:
                                        sound = wx.Sound(Common.opj(u'../TrainTicketGo/media/TheSmurfs.wav'))
                                        sound.Play(wx.SOUND_ASYNC)
                                        self.sound = sound
                                        wx.YieldIfNeeded()
                                    except NotImplementedError, v:
                                        wx.LogMessage(v)

                                    dlg = GMD.GenericMessageDialog(self, u'订票成功，订单号为：' + order_id,
                                                                   u"恭喜您啦~~",
                                                                   wx.OK | GMD.GMD_USE_GRADIENTBUTTONS | wx.ICON_INFORMATION)
                                    dlg.ShowModal()
                                    dlg.Destroy()
                                    self.endOrder()
                        else:
                            wx.LogMessage(u'获取订单号，原因【乘车人可能存在订单】，请前往12306处理')
                            self.endOrder()

    # 结束订票
    def endOrder(self):
        global F
        F = 0
        self.order_btn.SetLabel(u'开始订票')

    # 弹出订单提交验证码
    def showPassengerCode(self, **kwargs):
        auto_submit_params = kwargs['auto_submit_params']
        auto_submit_result_list = kwargs['auto_submit_result_list']
        queue_data = kwargs['queue_data']
        yp_info = kwargs['yp_info']
        # 提交订单验证码框
        win = PassCodeFrame(self, u'提交订单验证码（可按空格键、右键快速提交）',
                            win=self,
                            yp_info=yp_info,
                            auto_submit_params=auto_submit_params,
                            auto_submit_result_list=auto_submit_result_list,
                            queue_data=queue_data)

        win.SetSize((353, 300))
        win.CenterOnParent(wx.BOTH)
        win.Show(True)

    # 判断是否有票
    def isZero(self, num):
        if num in ('--', u'无', '0', u'*'):
            return None
        else:
            return num

    # 出发地、目的地切换
    def SwitchStation(self, event):
        start_val = self.start_station.GetValue()
        arrival_val = self.arrival_station.GetValue()
        self.start_station.SetValue(arrival_val)
        self.arrival_station.SetValue(start_val)

        self.switch_lbl.SetFocus()

    # 发车时间选择过滤车次
    def TrainTimesComboBox(self, event):

        self.list.DeleteAllItems()

        cbValue = self.train_times_combobox.GetValue()
        cb_time_pre = time.strptime(cbValue[:5], '%H:%M')
        cb_time_suf = time.strptime('23:59' if cbValue[7:] == '24:00' else cbValue[7:], '%H:%M')

        for item in self.ALL:
            # 获取列表车次发车时间和到达时间
            train_time = item[2][:5]
            train_time_pre = time.strptime('23:59' if train_time == '24:00' else train_time, '%H:%M')
            # train_time_suf = item[2][6:]
            if train_time_pre >= cb_time_pre and train_time_pre <= cb_time_suf:
                self.list.Append(item)

        pass

    # 车次类型选择事件
    def TrainNumberCheck(self, event, train_pre_param):
        cbObj = event.GetEventObject()
        tmp_list = sorted(range(self.list.ItemCount), reverse=True)

        # 默认删除选择的车次类型
        for i in tmp_list:
            train_no = self.list.GetItemText(i)
            train_no_pre = train_no[:1]

            if train_no_pre in train_pre_param:
                self.list.DeleteItem(i)

        if cbObj.IsChecked():

            # 高铁、城轨
            if train_pre_param in 'G,C':
                for itemGC in self.GC:
                    self.list.Append(itemGC)
            # 动车
            elif train_pre_param == 'D':
                for itemD in self.D:
                    self.list.Append(itemD)
            # 直达
            elif train_pre_param == 'Z':
                for itemZ in self.Z:
                    self.list.Append(itemZ)
            # 特快
            elif train_pre_param == 'T':
                for itemT in self.T:
                    self.list.Append(itemT)
            # 快速
            elif train_pre_param == 'K':
                for itemK in self.K:
                    self.list.Append(itemK)
            else:
                # 其他车次
                for itemYLP in self.YLP:
                    self.list.Append(itemYLP)

    # 坐席选择事件
    def SeatTypeCheck(self, event, tuple_key):

        cbObj = event.GetEventObject()
        # cWidth = self.list.GetColumnWidth(int(col_index))

        if cbObj.IsChecked():
            self.list.SetColumnWidth(tuple_key[0], tuple_key[1])
        else:
            self.list.SetColumnWidth(tuple_key[0], 0)

    # 选择乘客
    def ChoicePassenger(self, event):
        lst = []
        self.passengers = []
        if self.passenger_or_msg and isinstance(self.passenger_or_msg, (str, unicode)):
            wx.MessageBox(self.passenger_or_msg)
            return

        for passenger in self.passenger_or_msg:
            lst.append(passenger['passenger_name'])

        dlg = wx.MultiChoiceDialog(self.ticket_win, u"选择乘客", u"联系人列表", lst)
        if (dlg.ShowModal() == wx.ID_OK):
            selections = dlg.GetSelections()
            ret_passengers = [lst[x] for x in selections]
            # =
            passengerTicketStr = []
            oldPassengerStr = []
            for x in selections:
                # n_passenger = {}
                # # 乘客姓名
                # n_passenger['passenger_name'] = (self.passenger_or_msg[x]['passenger_name'])
                # # 证件类型
                # n_passenger['passenger_id_type_code'] = self.passenger_or_msg[x]['passenger_id_type_code']
                # # 证件号
                # n_passenger['passenger_id_no'] = self.passenger_or_msg[x]['passenger_id_no']
                # # 手机号
                # n_passenger['mobile_no'] = self.passenger_or_msg[x]['mobile_no']
                # # 保存常用联系人
                # n_passenger['comm_used'] = 'Y' if self.passenger_or_msg[x]['index_id'] == '0' else 'N'
                # # 乘客类型
                # n_passenger['passenger_type'] = self.passenger_or_msg[x]['passenger_type']
                self.passengers.append(self.passenger_or_msg[x])

            if self.seatTypes:
                for st in self.seatTypes:
                    for k, v in st.items():
                        tmp_passengerTicketStr = []
                        tmp_oldPassengerStr = []
                        for index, pas in enumerate(self.passengers):
                            passenger_name = pas['passenger_name']
                            passenger_id_type_code = pas['passenger_id_type_code']
                            passenger_id_no = pas['passenger_id_no']
                            passenger_type = pas['passenger_type']
                            mobile_no = pas['mobile_no']
                            # 是否常用联系人
                            comm_used = 'Y' if pas['index_id'] == '0' else 'N'
                            comm_used = comm_used if index + 1 == len(self.passengers) else comm_used + '_'
                            tmp_passengerTicketStr.append(','.join((k, '0', '1', passenger_name, passenger_id_type_code
                                                                    , passenger_id_no
                                                                    , mobile_no,
                                                                    comm_used)))
                            tmp_oldPassengerStr.append(','.join((passenger_name,
                                                                 passenger_id_type_code,
                                                                 passenger_id_no,
                                                                 passenger_type + '_')))
                        passengerTicketStr.append(tmp_passengerTicketStr)
                        oldPassengerStr.append(tmp_oldPassengerStr)

            self.passengerTicketStr, self.oldPassengerStr = [], []
            for ptickstr in passengerTicketStr:
                self.passengerTicketStr.append(''.join(pstr for pstr in ptickstr))
            for oldstr in oldPassengerStr:
                self.oldPassengerStr.append(''.join(ostr for ostr in oldstr))

            self.ticket_win.passenger_txt.SetValue(' '.join(passenger for passenger in ret_passengers))

        dlg.Destroy()

    # 清空车次
    def ClearTrain(self, event):
        self.train_txt.Clear()
        # self.trains = []
        # for index in range(self.list.ItemCount):
        #     self.list.CheckItem(index, False)
        self.list.CancelAllTrain(None)

    # 坐席选择
    def ChoiceSeatType(self, event):
        self.seatTypes = []
        if self.passenger_or_msg and isinstance(self.passenger_or_msg, (str, unicode)):
            wx.MessageBox(self.passenger_or_msg)
            return

        lst = Common.GetSeatType()
        dlg = wx.MultiChoiceDialog(self.ticket_win, u"选择席别", u"席别类型列表", lst)
        if (dlg.ShowModal() == wx.ID_OK):
            selections = dlg.GetSelections()
            ret_seat = [lst[x] for x in selections]

            for x in selections:
                self.seatTypes.append(Common.seat_types[x])

            passengerTicketStr = []
            oldPassengerStr = []
            # 处理订单提交数据（乘客、坐席）
            if self.passengers:
                for st in self.seatTypes:
                    for k, v in st.items():
                        tmp_passengerTicketStr = []
                        tmp_oldPassengerStr = []
                        for index, pas in enumerate(self.passengers):
                            passenger_name = pas['passenger_name']
                            passenger_id_type_code = pas['passenger_id_type_code']
                            passenger_id_no = pas['passenger_id_no']
                            passenger_type = pas['passenger_type']
                            mobile_no = pas['mobile_no']
                            # 是否常用联系人
                            comm_used = 'Y' if pas['index_id'] == '0' else 'N'
                            comm_used = comm_used if index + 1 == len(self.passengers) else comm_used + '_'
                            tmp_passengerTicketStr.append(','.join((k, '0', '1', passenger_name, passenger_id_type_code
                                                                    , passenger_id_no
                                                                    , mobile_no,
                                                                    comm_used)))
                            tmp_oldPassengerStr.append(','.join((passenger_name,
                                                                 passenger_id_type_code,
                                                                 passenger_id_no,
                                                                 passenger_type + '_')))
                        passengerTicketStr.append(tmp_passengerTicketStr)
                        oldPassengerStr.append(tmp_oldPassengerStr)

            self.passengerTicketStr, self.oldPassengerStr = [], []
            for ptickstr in passengerTicketStr:
                self.passengerTicketStr.append(''.join(pstr for pstr in ptickstr))
            for oldstr in oldPassengerStr:
                self.oldPassengerStr.append(''.join(ostr for ostr in oldstr))

            self.ticket_win.train_seat_txt.SetValue(' '.join(seat for seat in ret_seat))

        dlg.Destroy()

    # 车次、坐席全选/反选
    def onSelectALL(self, event):
        sel_obj = event.GetEventObject()

        if sel_obj.GetId() == 1:
            self.list.DeleteAllItems()
            for xb_cb in self.list_cc:
                xb_cb.SetValue(self.cc_cbs.GetValue())

            if sel_obj.IsChecked():
                for itemALL in self.ALL:
                    self.list.Append(itemALL)

        if sel_obj.GetId() == 2:
            for tuple_key, seatType in self.dict_seatType.items():
                seatType.SetValue(self.m_xbqx.GetValue())

                if sel_obj.IsChecked():
                    self.list.SetColumnWidth(tuple_key[0], tuple_key[1])
                else:
                    self.list.SetColumnWidth(tuple_key[0], 0)

    # 查票
    def QueryTicket(self, event):

        Common.headers['Referer'] = Common.left_ticket_url
        self.ClearTrain(None)

        # 清空已绑定值
        self.ALL, self.GC, self.D, self.Z, self.T, self.K, self.YLP = [], [], [], [], [], [], []
        self.list.DeleteAllItems()

        # 发车时间
        cbValue = self.train_times_combobox.GetValue()
        cb_time_pre = time.strptime(cbValue[:5], '%H:%M')
        # python 中24:00就是00:00，将24:00转换成23:59
        cb_time_suf = time.strptime(('23:59' if cbValue[7:] == '24:00' else cbValue[7:]), '%H:%M')

        # 获取12306查询车票返回数据
        Common.startWorkFunc(self.QueryTicketData, self.QueryTicketDataSuccess, (cb_time_pre, cb_time_suf))

    def makePanel(self):
        win = PanelWin.PanelWin(self)
        return win

    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        event.Skip()

    def QueryTicketDataSuccess(self, delayedResult, *args, **kwargss):

        self.query_btn.Enable()
        self.query_btn.SetLabel(u'查询')
        try:
            data_json = delayedResult.get()
        except Exception, e:
            print(u'查询车次 %s 异常:%s' % (delayedResult.getJobID, e))

        cb_time_pre = args[0]
        cb_time_suf = args[1]

        if data_json:
            status = data_json.get('status')
            message = data_json.get('message')
            data = data_json.get('data')
            if status and not message and data:
                # 得到返回数据，并排序（将不可预订车次放到列表最后），同时排序发车时间
                data = sorted(data, key=lambda o: o['queryLeftNewDTO']['canWebBuy'], reverse=True)
                data = sorted(data, key=lambda o: o['queryLeftNewDTO']['start_time'])
                for d in data:
                    secretStr = d.get('secretStr')
                    # 预订按钮
                    bti = u'可预订' if d.get('buttonTextInfo') == u'预订' else d.get('buttonTextInfo')
                    dto = d.get('queryLeftNewDTO')
                    # 车次编号
                    train_no = dto.get('train_no')

                    # 车次编码
                    station_train_code = dto.get('station_train_code')
                    # 出发地电报码
                    start_station_telecode = dto.get('start_station_telecode')
                    # 出发地
                    start_station_name = dto.get('start_station_name')
                    # 目的地电报码
                    end_station_telecode = dto.get('end_station_telecode')
                    # 目的地
                    end_station_name = dto.get('end_station_name')

                    # 出发地电报码
                    from_station_telecode = dto.get('from_station_telecode')

                    # 目的地电报码
                    to_station_telecode = dto.get('to_station_telecode')

                    # 出发时间
                    start_time = dto.get('start_time')
                    # 到达时间
                    arrive_time = dto.get('arrive_time')
                    # 历时
                    lishi = dto.get('lishi')
                    # 是否web页面可购买
                    canWebBuy = dto.get('canWebBuy')

                    # 坐席类型
                    seat_types = dto.get('seat_types')

                    # 出发站编号
                    from_station_no = dto.get('from_station_no')

                    # 到达站编号
                    to_station_no = dto.get('to_station_no')
                    # 车次是否受控
                    controlled_train_flag = dto.get('controlled_train_flag')

                    # "gg_num": "--",
                    # "yb_num": "--",

                    # 商务座
                    swz_num = dto.get('swz_num')
                    # 特等座
                    tz_num = dto.get('tz_num')
                    # 一等座
                    zy_num = dto.get('zy_num')
                    # 二等座
                    ze_num = dto.get('ze_num')
                    # 高级软卧
                    gr_num = dto.get('gr_num')
                    # 软卧
                    rw_num = dto.get('rw_num')
                    # 硬卧
                    yw_num = dto.get('yw_num')
                    # 软座
                    rz_num = dto.get('rz_num')
                    # 硬座
                    yz_num = dto.get('yz_num')
                    # 无座
                    wz_num = dto.get('wz_num')
                    # 其他
                    qt_num = dto.get('qt_num')

                    # 组合车次详细信息
                    info = (station_train_code,
                            '-'.join(name for name in (start_station_name, end_station_name)),
                            '-'.join(t for t in (start_time, arrive_time)), lishi, swz_num, tz_num, zy_num,
                            ze_num, gr_num, rw_num, yw_num, rz_num, yz_num, wz_num, qt_num, bti, train_no,
                            canWebBuy, secretStr, seat_types, from_station_no, to_station_no,
                            from_station_telecode, to_station_telecode, controlled_train_flag)

                    # 车次前缀首字母
                    station_train_code_first = station_train_code[:1]
                    # python 中24:00就是00:00，将24:00转换成23:59
                    train_start_time = time.strptime(('23:59' if start_time == '24:00' else start_time),
                                                     '%H:%M')
                    # train_arrive_time = time.strptime(('23:59' if arrive_time == '24:00' else arrive_time),
                    #                                   '%H:%M')

                    if train_start_time >= cb_time_pre and train_start_time <= cb_time_suf:

                        if station_train_code_first in 'G,C':
                            # 高铁和城轨
                            self.GC.append(info)
                        elif station_train_code_first == 'D':
                            # 动车
                            self.D.append(info)
                        elif station_train_code_first == 'Z':
                            # 直达客车
                            self.Z.append(info)
                        elif station_train_code_first == 'T':
                            # 特快
                            self.T.append(info)
                        elif station_train_code_first == 'K':
                            # 快速
                            self.K.append(info)
                        else:
                            # 其他车次（临客、旅游车、普快）
                            self.YLP.append(info)

                        # 所有类型车次
                        self.ALL.append(info)
                        # 列表页数据展示
                        self.list.Append(info)

        # 设置选择车次
        self.train_txt.Clear()
        for ic in range(self.list.ItemCount):
            for tr in self.trains:
                if self.list.GetItemText(ic) == tr:
                    self.list.CheckItem(ic)

    # 查询
    def QueryTicketData(self, *args, **kwargs):
        self.query_btn.Disable()
        self.query_btn.SetLabel(u'正在查询...')

        # 起始站
        start_station = self.start_station.GetValue()
        start_tgc, arrival_tgc = '', ''
        # 终点站
        arrival_station = self.arrival_station.GetValue()
        # 出发日
        departureDay = self.departureDay.GetValue()
        departureDay_format = departureDay.Format('%Y-%m-%d')

        wx.LogMessage(u'开始查询---> （%s：%s－%s）' % (departureDay_format, start_station, arrival_station) + u' 车次，请稍后...')

        # 返程日
        now = wx.DateTime().Now()
        now_format = now.Format('%Y-%m-%d')

        # 设置起始站和目的站电报码
        for station in self.stations:
            list_choice = list(station)
            list_choice[0] = list_choice[0].decode('utf-8')
            if start_station == list_choice[0]:
                start_tgc = list_choice[1]
            if arrival_station == list_choice[0]:
                arrival_tgc = list_choice[1]

        # 查询参数组装
        query_params = [';_jc_save_fromStation=', Req.quote(start_station.encode('utf-8') + ','), start_tgc,
                        ';_jc_save_toStation=',
                        Req.quote(arrival_station.encode('utf-8') + ','),
                        arrival_tgc, ';_jc_save_fromDate=', departureDay_format, ';_jc_save_toDate=',
                        now_format,
                        ';_jc_save_wfdc_flag=dc']

        params = ''.join(p for p in query_params)

        if str(Common.headers['Cookie']).find('_jc_save_fromStation') == -1:
            Common.headers['Cookie'] += params
        purpose_codes = 'ADULT' if self.rd_box.GetSelection() == 0 else '0X00'

        # 查询车票log参数
        log_params = [Common.query_ticket_log_url, 'leftTicketDTO.train_date=', departureDay_format,
                      '&leftTicketDTO.from_station=',
                      start_tgc,
                      '&leftTicketDTO.to_station=', arrival_tgc, '&purpose_codes=', purpose_codes]
        query_url_log = ''.join(l for l in log_params)
        # 查詢車票log，如果正常返回，則進行車票查詢
        try:
            log_rs = Req.get(query_url_log, Common.headers)
            log_unzipped = Req.zippedDecompress(log_rs)
            # 如果正常返回 status:true
            if log_unzipped:
                log_json = json.loads(log_unzipped)
                log_status = log_json.get('status')
                log_message = log_json.get('message')
                if log_status == True and log_message is None:

                    for t_url in Common.query_ticket_url:
                        # 查询车票参数
                        to_query_params = [Common.otn_url + t_url, 'leftTicketDTO.train_date=',
                                           departureDay_format,
                                           '&leftTicketDTO.from_station=',
                                           start_tgc,
                                           '&leftTicketDTO.to_station=', arrival_tgc, '&purpose_codes=', purpose_codes]

                        query_url = ''.join(d for d in to_query_params)
                        rs = Req.get(query_url, Common.headers)
                        # 获取12306查询车票返回数据
                        rs_uzipped = Req.zippedDecompress(rs)
                        json_data = json.loads(rs_uzipped)
                        # 判断是否正常返回状态，没有正常返回，则切换url再查
                        if json_data and not json_data.get('status'):
                            continue

                        if json_data:
                            r_data = json_data.get('data')
                            count = 0
                            for r_d in r_data:
                                if r_d.get('buttonTextInfo') == u'预订':
                                    count += 1

                            wx.LogMessage(u'查询结果：可订车次【%d' % count + u'】列')
                        else:
                            wx.LogMessage(u'未查询到可订车次')

                        return json_data
        except Exception, e:
            wx.LogMessage(u'查询超时，请重新查询')

        return {}


class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, wx.DefaultPosition, wx.Size(-1, 250), style=wx.LC_REPORT)
        CheckListCtrlMixin.__init__(self)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_LIST_COL_BEGIN_DRAG, self.OnColumnDrag)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnContextMenu)
        self.tick_win = parent

    # 列表标题禁用可拉伸
    def OnColumnDrag(self, evt):
        evt.Veto()
        return

    # 列表数据右键选项
    def OnContextMenu(self, event):

        # cur_index = event.m_itemIndex
        # train_no = self.GetItemText(cur_index)

        menu = wx.Menu()

        self.popupBookCurTrain = wx.NewId()
        self.popupCancelCurTrain = wx.NewId()
        self.popupBookAllTrain = wx.NewId()
        self.popupCancelAllTrain = wx.NewId()
        self.popupViewTrain = wx.NewId()

        self.Bind(wx.EVT_MENU,
                  lambda evt: self.BookCurrentTrain(event=event),
                  id=self.popupBookCurTrain)
        self.Bind(wx.EVT_MENU,
                  lambda evt: self.CancelCurrentTrain(event=event),
                  id=self.popupCancelCurTrain)
        self.Bind(wx.EVT_MENU, lambda evt: self.BookAllTrain(event=event),
                  id=self.popupBookAllTrain)
        self.Bind(wx.EVT_MENU, lambda evt: self.CancelAllTrain(event=event),
                  id=self.popupCancelAllTrain)
        self.Bind(wx.EVT_MENU, lambda evt: self.ViewTrain(event=event), id=self.popupViewTrain)

        # 添加右键菜单项
        item = wx.MenuItem(menu, self.popupBookCurTrain, u"预订此车次")
        menu.AppendItem(item)
        menu.Append(self.popupCancelCurTrain, u"取消此车次")
        menu.Append(self.popupBookAllTrain, u"预订所有车次")
        menu.Append(self.popupCancelAllTrain, u"取消所有车次")
        menu.Append(self.popupViewTrain, u'查看停靠站及票价')

        # 生成右键菜单
        self.PopupMenu(menu)
        menu.Destroy()

    # 右键查看所选车次停靠站及票价
    def ViewTrain(self, event):

        train_date = self.tick_win.departureDay.GetValue()
        train_date = train_date.Format('%Y-%m-%d')

        train_no = self.GetItemText(event.m_itemIndex, 16)
        seat_types = self.GetItemText(event.m_itemIndex, 19)
        from_station_no = self.GetItemText(event.m_itemIndex, 20)
        to_station_no = self.GetItemText(event.m_itemIndex, 21)
        from_station_telecode = self.GetItemText(event.m_itemIndex, 22)
        to_station_telecode = self.GetItemText(event.m_itemIndex, 23)

        # 查询车次票价
        ticketPrice_FL_url = Common.ticket_price_FL_url + train_no + '&from_station_no=' + from_station_no + '&to_station_no=' + to_station_no + '&seat_types=' + seat_types + '&train_date=' + train_date
        ticketPrice_url = Common.ticket_price_url + train_no + '&from_station_no=' + from_station_no + '&to_station_no=' + to_station_no + '&seat_types=' + seat_types + '&train_date=' + train_date

        train_detail_url = Common.train_detail_url + train_no + '&from_station_telecode=' + from_station_telecode + '&to_station_telecode=' + to_station_telecode + '&depart_date=' + train_date

        Common.startWorkFunc(self.ViewTrainDetail, self.ViewTrainDetailSuccess, cargs=(self, event.GetPosition()),
                             wargs=(ticketPrice_FL_url,
                                    ticketPrice_url,
                                    train_detail_url))

    # 查看车次停靠站及票价
    def ViewTrainDetail(self, *args, **kwargs):

        ticketPrice_FL_url = args[0]
        ticketPrice_url = args[1]
        train_detail_url = args[2]

        # 查询票价
        Req.get(ticketPrice_FL_url, Common.headers)
        res = Req.get(ticketPrice_url, Common.headers)
        # 返回票价数据
        res_data = Req.zippedDecompress(res)

        # 查询停靠站
        train_detail_rs = Req.get(train_detail_url, Common.headers)
        train_detail_rs_data = Req.zippedDecompress(train_detail_rs)

        return res_data, train_detail_rs_data

    def ViewTrainDetailSuccess(self, delayedResult, *args, **kwargs):

        try:
            rs = delayedResult.get()
        except Exception, e:
            print(u'查询未完成订单 %s 异常:%s' % (delayedResult.getJobID, e))

        res_data = rs[0]
        train_detail_rs_data = rs[1]
        paretn_obj = args[0]
        pos = args[1]

        if res_data and train_detail_rs_data:
            # 转换成json
            price_json = json.loads(res_data)
            status = price_json.get('status')
            message = price_json.get('messages')
            # 获取车次坐席票价
            price_data = price_json.get('data')

            # 车次停靠站明细
            train_detail_json = json.loads(train_detail_rs_data)
            train_detail_data = train_detail_json.get('data').get('data')

            if status and not message and price_data and train_detail_data:
                win = PopupWin.Popup(paretn_obj.GetTopLevelParent(), wx.SIMPLE_BORDER, price_data, train_detail_data)
                win.SetPosition(pos)
                win.Popup()
            else:
                wx.LogMessage(u'获取数据失败')
        else:
            wx.LogMessage(u'查询停靠站及票价超时，请稍后再试')

    # 取消所有车次
    def CancelAllTrain(self, event):
        for i in range(self.ItemCount):
            controlled_train_flag = self.GetItemText(i, 24)
            if controlled_train_flag == '0':
                self.CheckItem(i, False)
                # cur_last_column = self.GetItemText(i, 15)
                # if cur_last_column == u'可预订':
                #     self.CheckItem(i, False)

    # 預訂所有車次
    def BookAllTrain(self, event):
        for i in range(self.ItemCount):
            controlled_train_flag = self.GetItemText(i, 24)
            if controlled_train_flag == '0':
                self.CheckItem(i)
                # cur_last_column = self.GetItemText(i, 15)
                # if cur_last_column == u'可预订':
                #     self.CheckItem(i)

    # 預訂當前車次
    def BookCurrentTrain(self, event):
        last_column = self.GetItemText(event.m_itemIndex, 15)
        controlled_train_flag = self.GetItemText(event.m_itemIndex, 24)
        # if last_column == u'可预订':
        #     self.CheckItem(event.m_itemIndex)
        # else:
        #     # u'当前车次不可预订，请选择其他车次'
        #     wx.MessageBox(last_column)
        if controlled_train_flag == '1':
            wx.MessageBox(last_column)
            return
        self.CheckItem(event.m_itemIndex)

    # 取消當前車次
    def CancelCurrentTrain(self, event):
        self.CheckItem(event.m_itemIndex, False)

    # 双击选中列表数据事件
    def OnItemActivated(self, evt):

        # 获取车次状态
        last_column = self.GetItemText(evt.m_itemIndex, 15)
        controlled_train_flag = self.GetItemText(evt.m_itemIndex, 24)

        # if last_column == u'可预订':
        #     self.ToggleItem(evt.m_itemIndex)
        # else:
        #     wx.MessageBox(last_column)

        if controlled_train_flag == '1':
            wx.MessageBox(last_column)
            return

        self.ToggleItem(evt.m_itemIndex)

    # this is called by the base class when an item is checked/unchecked
    def OnCheckItem(self, index, flag):
        # 获取车次编码
        station_train_code = self.GetItemText(index)
        last_column = self.GetItemText(index, 15)
        # secretStr = self.GetItemText(index, 18)
        controlled_train_flag = self.GetItemText(index, 24)

        # if last_column != u'可预订':
        #     wx.MessageBox(last_column)
        #     return
        if controlled_train_flag == '1':
            wx.MessageBox(last_column)
            return

        if flag:
            if (station_train_code not in self.tick_win.trains):
                self.tick_win.trains.append(station_train_code)
        else:
            self.tick_win.trains.remove(station_train_code)

        self.tick_win.train_txt.SetValue(' '.join(obj for obj in self.tick_win.trains))

        # ----------------------------------------------------------------------------


# 订单验证码弹出窗口Frame
class PassCodeFrame(wx.MiniFrame):
    def __init__(self, parent, title, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.CAPTION | wx.CLOSE_BOX | wx.TAB_TRAVERSAL, **kwargs):
        wx.MiniFrame.__init__(self, parent, 99, title, pos, size, style)

        wx.LogMessage(u'开始获取订单验证码...')

        win = kwargs['win']
        auto_submit_params = kwargs['auto_submit_params']
        auto_submit_result_list = kwargs['auto_submit_result_list']
        queue_data = kwargs['queue_data']
        yp_info = kwargs['yp_info']

        panel = wx.Panel(self, -1)
        # 显示订单验证码图片
        scaledBmp = self.GetPassCodeImg()
        self.codeBitMap = wx.StaticBitmap(panel, wx.ID_ANY, scaledBmp)
        self.codeBitMap.SetPosition((15, 15))
        self.codeBitMap.Bind(wx.EVT_LEFT_DOWN, self.OnDrawImage)

        self.imageContainer = []
        self.pos = []

        # 刷新验证码图标
        refreshImg = Common.codeRefreshMark.GetBitmap()
        self.refreshImg = wx.StaticBitmap(self.codeBitMap, wx.ID_ANY, refreshImg)
        self.refreshImg.SetPosition((260, 4))
        self.refreshImg.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        self.refreshImg.Bind(wx.EVT_LEFT_DOWN, self.RefreshPassCode)

        self.goBtn = wx.Button(panel, wx.ID_ANY, u'提交验证码')
        self.goBtn.SetPosition((135, 218))
        self.goBtn.Bind(wx.EVT_BUTTON, lambda event, win_obj=win, submit_params=auto_submit_params,
                                              submit_result_list=auto_submit_result_list,: self.TicketGo4Code(event,
                                                                                                              win_obj,
                                                                                                              submit_params,
                                                                                                              submit_result_list
                                                                                                              ))

        self.Bind(wx.EVT_CLOSE, lambda evt, win_obj=win: self.OnCloseWindow(evt, win_obj))
        # 綁定鍵盤空格事件
        self.Bind(wx.EVT_KEY_DOWN, lambda event, win_obj=win, submit_params=auto_submit_params,
                                          submit_result_list=auto_submit_result_list: self.spaceClick(event,
                                                                                                      win_obj,
                                                                                                      submit_params,
                                                                                                      submit_result_list,
                                                                                                      ))
        # 绑定键盘右键事件
        # wx.EVT_COMMAND_RIGHT_CLICK
        panel.Bind(wx.EVT_RIGHT_DOWN, lambda event, win_obj=win, submit_params=auto_submit_params,
                                             submit_result_list=auto_submit_result_list: self.TicketGo4Code(event,
                                                                                                            win_obj,
                                                                                                            submit_params,
                                                                                                            submit_result_list,
                                                                                                            ))
        panel.Bind(wx.EVT_COMMAND_RIGHT_CLICK, lambda event, win_obj=win, submit_params=auto_submit_params,
                                                      submit_result_list=auto_submit_result_list: self.TicketGo4Code(
            event,
            win_obj,
            submit_params,
            submit_result_list,
        ))

        self.codeBitMap.Bind(wx.EVT_RIGHT_DOWN, lambda event, win_obj=win, submit_params=auto_submit_params,
                                                       submit_result_list=auto_submit_result_list: self.TicketGo4Code(
            event,
            win_obj,
            submit_params,
            submit_result_list,
        ))
        self.codeBitMap.Bind(wx.EVT_COMMAND_RIGHT_CLICK,
                             lambda event, win_obj=win, submit_params=auto_submit_params,
                                    submit_result_list=auto_submit_result_list: self.TicketGo4Code(
                                 event,
                                 win_obj,
                                 submit_params,
                                 submit_result_list,
                             ))

        try:
            sound = wx.Sound(Common.opj(u'../TrainTicketGo/media/message.wav'))
            sound.Play(wx.SOUND_ASYNC)
            self.sound = sound
            wx.YieldIfNeeded()
        except NotImplementedError, v:
            wx.LogMessage(v)

    # 空格键提交
    def spaceClick(self, event, win_obj, submit_params, submit_result_list):
        if event.GetKeyCode() == wx.WXK_SPACE:
            self.TicketGo4Code(event, win_obj, submit_params, submit_result_list)

    def OnCloseWindow(self, event, win_obj):
        global F
        F = 0
        win_obj.order_btn.SetLabel(u'开始订票')
        self.Destroy()

    # 刷新验证码
    def RefreshPassCode(self, event):
        scaledBmp = self.GetPassCodeImg()
        self.codeBitMap.SetBitmap(scaledBmp)
        self.goBtn.Enable()
        self.goBtn.SetLabel(u'提交验证码')
        # 清空已选值
        self.ClearCodeData()

    # 提交订单验证码
    def OnDrawImage(self, event):

        self.goBtn.SetFocus()

        pos = event.GetPosition()
        location = pos - (13, 13)
        pos = pos - (0, 30)

        if pos.x - 5 < 0:
            return None

        if pos.y < 0:
            return None

        imageBitmap = wx.StaticBitmap(self.codeBitMap, wx.ID_ANY, Common.codeMark.GetBitmap(), location)
        imageBitmap.Bind(wx.EVT_LEFT_DOWN, lambda evt, postion=pos: self.codeMapRemove(evt, postion))
        self.imageContainer.append(imageBitmap)

        # 验证码坐标添加至pos list中
        self.pos.append(str(pos.x))
        self.pos.append(str(pos.y))

    def codeMapRemove(self, event, pos):
        obj = event.GetEventObject()

        if str(pos.x) in self.pos or str(pos.y) in self.pos:
            self.imageContainer.remove(obj)
            try:
                self.pos.remove(str(pos.x))
            except:
                pass
            else:
                self.pos.remove(str(pos.y))

            obj.Destroy()

    # 提交订单验证码
    def TicketGo4Code(self, event, win_obj, submit_params, submit_result_list):
        global F
        if not self.pos:
            wx.MessageBox(u'请选择验证码')
            return

        self.goBtn.Disable()
        self.goBtn.SetLabel(u'正在疯狂提交...')

        wx.LogMessage(u'①校验订单验证码')
        randCode = ','.join(self.pos)
        passenger_code_params = {'rand': 'randp', 'randCode': randCode, '_json_att': ''}
        passcode_rs = Req.post(Common.passenger_code_check, passenger_code_params, Common.headers)
        passcode_unzipped = Req.zippedDecompress(passcode_rs)

        if passcode_unzipped:
            passcode_json = json.loads(passcode_unzipped)
            passcode_status = passcode_json.get('status')
            passcode_data = passcode_json.get('data')
            if passcode_status and passcode_data and passcode_data.get('result') == '0':
                self.RefreshPassCode(None)
                self.goBtn.Enable(True)
                self.goBtn.SetLabel(u'提交验证码')
                wx.MessageBox(u'验证码貌似不正确，请您重新选择提交')
                return
            # 订单验证码正确
            if passcode_data.get('result') == '1':
                wx.LogMessage(u'订单验证码校验成功')
                wx.LogMessage(u'②开始提交订单...')
                # 组装：提交订单确认队列参数
                confirm_single_params = {'passengerTicketStr': submit_params['passengerTicketStr'],
                                         'oldPassengerStr': submit_params['oldPassengerStr'], 'randCode': randCode,
                                         'purpose_codes': submit_params['purpose_codes'],
                                         'key_check_isChange': submit_result_list[1],
                                         'leftTicketStr': submit_result_list[2],
                                         'train_location': submit_result_list[0],
                                         }
                print('confirm_single_params:')
                print(confirm_single_params)
                # 提交是否可以排队请求
                confirm_single_rs = Req.post(Common.confirm_single_for_queue_url, confirm_single_params,
                                             Common.headers)
                confirm_single_unzipped = Req.zippedDecompress(confirm_single_rs)
                print('confirm_single_unzipped:')
                print(confirm_single_unzipped)
                if confirm_single_unzipped:

                    confirm_single_json = json.loads(confirm_single_unzipped)
                    confirm_single_status = confirm_single_json.get('status')
                    confirm_single_messages = confirm_single_json.get('messages')
                    confirm_single_data = confirm_single_json.get('data')
                    # 订单确认成功返回
                    if confirm_single_status and confirm_single_data.get('submitStatus'):
                        wx.LogMessage(u'订单提交成功')
                        wx.LogMessage(u'③开始查询订单...')
                        # 查询未完成订单（未付款的订单）
                        query_myorder_rs = Req.post(Common.query_myorder_nocomplete_url, {}, Common.headers)
                        query_myorder_unzipped = Req.zippedDecompress(query_myorder_rs)
                        print('query_myorder_unzipped:')
                        print(query_myorder_unzipped)
                        if query_myorder_unzipped:
                            query_myorder_json = json.loads(query_myorder_unzipped)
                            query_myorder_status = query_myorder_json.get('status')
                            query_myorder_data = query_myorder_json.get('data')
                            if query_myorder_status and query_myorder_data:
                                order_cache_dto = query_myorder_data.get('orderCacheDTO')
                                if order_cache_dto and order_cache_dto.get('message'):
                                    order_cache_dto_message = order_cache_dto.get('message').get('message')
                                    if order_cache_dto_message:
                                        wx.LogMessage(u'【%s】' % order_cache_dto_message)
                                        self.OnCloseWindow(None, win_obj)
                                        win_obj.StartBuyTicket(None)
                                        return

                        # 获取订单号
                        order_time_params = {'random': str(time.mktime(time.localtime())),
                                             'tourFlag': submit_params['tour_flag']}
                        order_time_rs = Req.post(Common.query_order_waittime_url, order_time_params, Common.headers)
                        order_time_unzipped = Req.zippedDecompress(order_time_rs)
                        print('order_time_unzipped:', order_time_unzipped)
                        if order_time_unzipped:
                            order_time_json = json.loads(order_time_unzipped)
                            order_time_status = order_time_json.get('status')
                            order_time_data = order_time_json.get('data')
                            # 判断是否成功响应
                            if order_time_status and order_time_data and order_time_data.get(
                                    'queryOrderWaitTimeStatus'):
                                wx.LogMessage(u'正在获取订单号...')
                                # order_time_status = order_time_data.get('queryOrderWaitTimeStatus')
                                request_id = order_time_data.get('requestId')
                                msg = order_time_data.get('msg')
                                # 获取订单号
                                order_id = order_time_data.get('orderId')
                                if msg:
                                    wx.LogMessage(u'获取订单号失败，原因：【%s】' % (msg))
                                    self.OnCloseWindow(None, win_obj)
                                    win_obj.StartBuyTicket(None)
                                    return

                                # 获取订单如果失败，继续获取
                                if not order_id:
                                    count = 0
                                    while count < 3:
                                        time.sleep(2)
                                        count += 1
                                        order_time_rs = Req.post(Common.query_order_waittime_url,
                                                                 order_time_params, Common.headers)
                                        order_time_unzipped = Req.zippedDecompress(order_time_rs)
                                        order_time_json = json.loads(order_time_unzipped)
                                        order_time_data = order_time_json.get('data')
                                        wx.LogMessage(u'正在获取订单号...')

                                        if order_time_data.get('orderId'):
                                            order_id = order_time_data.get('orderId')
                                            break

                                if order_id:
                                    wx.LogMessage(u'获取订单号成功，订单号为：%s' % (order_id))
                                    # 查询订单结果
                                    data = {'orderSequence_no': order_id, '_json_att': ''}
                                    order_for_dcqueue_rs = Req.post(Common.order_for_dcqueue_url, data,
                                                                    Common.headers)
                                    order_for_dcqueue_unzipped = Req.zippedDecompress(order_for_dcqueue_rs)
                                    print('order_for_dcqueue_unzipped:', order_for_dcqueue_unzipped)
                                    if order_for_dcqueue_unzipped:
                                        order_for_dcqueue_json = json.loads(order_for_dcqueue_unzipped)
                                        status = order_for_dcqueue_json.get('status')
                                        data = order_for_dcqueue_json.get('data')
                                        if status and data and data.get('submitStatus'):
                                            # f = 0
                                            wx.LogMessage(u'恭喜您，订票成功，赶紧去支付吧')
                                            try:
                                                sound = wx.Sound(Common.opj(u'../TrainTicketGo/media/TheSmurfs.wav'))
                                                sound.Play(wx.SOUND_ASYNC)
                                                self.sound = sound
                                                wx.YieldIfNeeded()
                                            except NotImplementedError, v:
                                                wx.LogMessage(v)

                                            dlg = GMD.GenericMessageDialog(win_obj, u'订票成功，订单号为：' + order_id,
                                                                           u"恭喜您啦~~",
                                                                           wx.OK | GMD.GMD_USE_GRADIENTBUTTONS | wx.ICON_INFORMATION)
                                            dlg.ShowModal()
                                            dlg.Destroy()
                                            self.OnCloseWindow(None, win_obj)
                                            win_obj.QueryTicket(None)
                                else:
                                    wx.LogMessage(u'获取订单号，原因【乘车人可能存在订单】，请前往12306处理')
                                    self.OnCloseWindow(None, win_obj)


                    else:
                        self.RefreshPassCode(None)
                        self.goBtn.Enable(True)
                        self.goBtn.SetLabel(u'提交验证码')
                        wx.MessageBox(confirm_single_data.get('errMsg'))

    # 设置图片拉伸大小
    def ScaleBitMap(self, bitmap, width, height):
        image = wx.ImageFromBitmap(bitmap)
        image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
        result = wx.BitmapFromImage(image)
        return result

    # 获取提交订单验证码
    def GetPassCodeImg(self):
        passenger_passCode_url = Common.passenger_code_url + str(time.mktime(time.localtime()))
        res = Req.get(passenger_passCode_url, Common.headers)
        stream = cStringIO.StringIO(res.read())
        bmp = wx.BitmapFromImage(wx.ImageFromStream(stream))
        # scaledBmp = self.ScaleBitMap(bmp, bmp.GetWidth() + 100, bmp.GetHeight()+100)
        stream.flush()
        stream.close()
        return bmp

    def ClearCodeData(self):
        # 销毁验证码Marker
        for obj in self.imageContainer:
            obj.Destroy()
        # 清空Marker容器
        self.imageContainer = []
        # 清空坐标list
        self.pos = []
