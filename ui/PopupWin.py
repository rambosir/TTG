# -*- coding:utf-8 -*-
import wx
import wx.dataview


class Popup(wx.PopupTransientWindow):
    def __init__(self, parent, style, price_data, train_detail_data):
        wx.PopupTransientWindow.__init__(self, parent, style)
        pnl = wx.Panel(self, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(700, 400),
                       style=wx.HSCROLL | wx.TAB_TRAVERSAL)
        self.SetSize((700, 350))
        pnl.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        # pnl.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        pnl.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        # pnl.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        #

        # ------------------------票价显示开始-------------------------------#
        # 商务座
        swz_price = price_data.get('A9') if price_data.get('A9') else '--'
        # 特等座
        tdz_price = price_data.get('P') if price_data.get('P') else '--'
        # 一等座
        ydz_price = price_data.get('M') if price_data.get('M') else '--'
        # 二等座
        edz_price = price_data.get('O') if price_data.get('O') else '--'
        # 高级软卧
        gjrw_price = price_data.get('A6') if price_data.get('A6') else '--'
        # 软卧
        rw_price = price_data.get('A4') if price_data.get('A4') else '--'
        # 硬卧
        yw_price = price_data.get('A3') if price_data.get('A3') else '--'
        # 软座
        rz_price = price_data.get('A2') if price_data.get('A2') else '--'
        # 硬座
        yz_price = price_data.get('A1') if price_data.get('A1') else '--'
        # 无座
        wz_price = price_data.get('WZ') if price_data.get('WZ') else '--'
        # 其他

        fgSizer = wx.FlexGridSizer(0, 2, 2, 2)
        fgSizer.AddGrowableCol(0)
        fgSizer.AddGrowableCol(1)
        fgSizer.SetFlexibleDirection(wx.BOTH)
        fgSizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        sbSizer = wx.StaticBoxSizer(wx.StaticBox(pnl, wx.ID_ANY, u"票价"), wx.VERTICAL)

        gSizer = wx.GridSizer(0, 2, 0, 0)

        self.swz_price_lbl = wx.StaticText(sbSizer.GetStaticBox(), wx.ID_ANY, u"商务座：", wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.swz_price_lbl.Wrap(-1)
        gSizer.Add(self.swz_price_lbl, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        self.swz_price = wx.StaticText(sbSizer.GetStaticBox(), wx.ID_ANY, swz_price, wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.swz_price.Wrap(-1)
        self.swz_price.SetForegroundColour('#fc8302')
        gSizer.Add(self.swz_price, 0, wx.ALL, 5)

        self.tdz_price_lbl = wx.StaticText(sbSizer.GetStaticBox(), wx.ID_ANY, u"特等座：", wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.tdz_price_lbl.Wrap(-1)
        gSizer.Add(self.tdz_price_lbl, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        self.tdz_price = wx.StaticText(sbSizer.GetStaticBox(), wx.ID_ANY, tdz_price, wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.tdz_price.SetForegroundColour('#fc8302')
        gSizer.Add(self.tdz_price, 0, wx.ALL, 5)

        self.ydz_price_lbl = wx.StaticText(sbSizer.GetStaticBox(), wx.ID_ANY, u"一等座：", wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.ydz_price_lbl.Wrap(-1)
        gSizer.Add(self.ydz_price_lbl, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        self.ydz_price = wx.StaticText(sbSizer.GetStaticBox(), wx.ID_ANY, ydz_price, wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.ydz_price.Wrap(-1)
        self.ydz_price.SetForegroundColour('#fc8302')
        gSizer.Add(self.ydz_price, 0, wx.ALL, 5)

        self.edz_price_lbl = wx.StaticText(sbSizer.GetStaticBox(), wx.ID_ANY, u"二等座：", wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.edz_price_lbl.Wrap(-1)
        gSizer.Add(self.edz_price_lbl, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        self.edz_price = wx.StaticText(sbSizer.GetStaticBox(), wx.ID_ANY, edz_price, wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.edz_price.Wrap(-1)
        self.edz_price.SetForegroundColour('#fc8302')
        gSizer.Add(self.edz_price, 0, wx.ALL, 5)

        self.gjrw_price_lbl = wx.StaticText(sbSizer.GetStaticBox(), wx.ID_ANY, u"高级软卧：", wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.gjrw_price_lbl.Wrap(-1)
        gSizer.Add(self.gjrw_price_lbl, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        self.gjrw_price = wx.StaticText(sbSizer.GetStaticBox(), wx.ID_ANY, gjrw_price, wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.gjrw_price.Wrap(-1)
        self.gjrw_price.SetForegroundColour('#fc8302')
        gSizer.Add(self.gjrw_price, 0, wx.ALL, 5)

        self.rw_price_lbl = wx.StaticText(sbSizer.GetStaticBox(), wx.ID_ANY, u"软卧：", wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.rw_price_lbl.Wrap(-1)
        gSizer.Add(self.rw_price_lbl, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        self.rw_price = wx.StaticText(sbSizer.GetStaticBox(), wx.ID_ANY, rw_price, wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.rw_price.Wrap(-1)
        self.rw_price.SetForegroundColour('#fc8302')
        gSizer.Add(self.rw_price, 0, wx.ALL, 5)

        self.yw_price_lbl = wx.StaticText(sbSizer.GetStaticBox(), wx.ID_ANY, u"硬卧：", wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.yw_price_lbl.Wrap(-1)
        gSizer.Add(self.yw_price_lbl, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        self.yw_price = wx.StaticText(sbSizer.GetStaticBox(), wx.ID_ANY, yw_price, wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.yw_price.Wrap(-1)
        self.yw_price.SetForegroundColour('#fc8302')
        gSizer.Add(self.yw_price, 0, wx.ALL, 5)

        self.rz_price_lbl = wx.StaticText(sbSizer.GetStaticBox(), wx.ID_ANY, u"软座：", wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.rz_price_lbl.Wrap(-1)
        gSizer.Add(self.rz_price_lbl, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        self.rz_price = wx.StaticText(sbSizer.GetStaticBox(), wx.ID_ANY, rz_price, wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.rz_price.Wrap(-1)
        self.rz_price.SetForegroundColour('#fc8302')
        gSizer.Add(self.rz_price, 0, wx.ALL, 5)

        self.yz_price_lbl = wx.StaticText(sbSizer.GetStaticBox(), wx.ID_ANY, u"硬座：", wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.yz_price_lbl.Wrap(-1)
        gSizer.Add(self.yz_price_lbl, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        self.yz_price = wx.StaticText(sbSizer.GetStaticBox(), wx.ID_ANY, yz_price, wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.yz_price.Wrap(-1)
        self.yz_price.SetForegroundColour('#fc8302')
        gSizer.Add(self.yz_price, 0, wx.ALL, 5)

        self.wz_price_lbl = wx.StaticText(sbSizer.GetStaticBox(), wx.ID_ANY, u"无座：", wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.wz_price_lbl.Wrap(-1)
        gSizer.Add(self.wz_price_lbl, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        self.wz_price = wx.StaticText(sbSizer.GetStaticBox(), wx.ID_ANY, wz_price, wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.wz_price.Wrap(-1)
        self.wz_price.SetForegroundColour('#fc8302')
        gSizer.Add(self.wz_price, 0, wx.ALL, 5)

        sbSizer.Add(gSizer, 1, wx.ALIGN_CENTER, 5)
        fgSizer.Add(sbSizer, 1, wx.ALL | wx.EXPAND, 5)

        # ------------------------票价显示结束-------------------------------#


        # ------------------------停靠站显示开始-------------------------------#
        sbSizerDetail = wx.StaticBoxSizer(wx.StaticBox(pnl, wx.ID_ANY, u"停靠站"), wx.VERTICAL)

        station_train_code = train_detail_data[0].get('station_train_code')
        start_station_name = train_detail_data[0].get('start_station_name')
        end_station_name = train_detail_data[0].get('end_station_name')
        train_class_name = train_detail_data[0].get('train_class_name')
        service_type = u'无空调' if train_detail_data[0].get('service_type') == '0' else u'有空调'

        # 显示车次起始站及服务类型
        self.train_station_lbl = wx.StaticText(sbSizerDetail.GetStaticBox(), wx.ID_ANY, '     '.join(
            (station_train_code, start_station_name, ' --> ', end_station_name, train_class_name, service_type)),
                                               wx.DefaultPosition,
                                               wx.DefaultSize, 0)
        sbSizerDetail.Add(self.train_station_lbl, 0, wx.ALL, 5)

        # 停靠站列表
        self.trainDetailDataView = wx.ListCtrl(sbSizerDetail.GetStaticBox(), -1, wx.DefaultPosition, (480, 280),
                                               style=wx.LC_REPORT
                                               )
        self.trainDetailDataView.Bind(wx.EVT_LIST_COL_BEGIN_DRAG, self.OnColumnDrag)
        self.trainDetailDataView.InsertColumn(0, u'站序', wx.LIST_FORMAT_CENTER, 80)
        self.trainDetailDataView.InsertColumn(1, u'站名', wx.LIST_FORMAT_CENTER, 80)
        self.trainDetailDataView.InsertColumn(2, u'到站时间', wx.LIST_FORMAT_CENTER, 100)
        self.trainDetailDataView.InsertColumn(3, u'出发时间', wx.LIST_FORMAT_CENTER, 100)
        self.trainDetailDataView.InsertColumn(4, u'停留时间', wx.LIST_FORMAT_CENTER, 100)

        for index, d in enumerate(train_detail_data):
            station_no = d.get('station_no')
            station_name = d.get('station_name')
            arrive_time = d.get('arrive_time')
            start_time = d.get('start_time')
            stopover_time = d.get('stopover_time')
            isEnabled = d.get('isEnabled')
            # 列表添加停靠站数据
            self.trainDetailDataView.Append((station_no, station_name, arrive_time, start_time, stopover_time))
            # 如果不是起始站的车次，则该车站以前的停靠站设置为灰色
            if not isEnabled:
                self.trainDetailDataView.SetItemTextColour(index, wx.Colour(153, 153, 153))
                pass

        sbSizerDetail.Add(self.trainDetailDataView, 0, wx.ALL | wx.EXPAND, 5)
        fgSizer.Add(sbSizerDetail, 1, wx.ALL | wx.EXPAND, 5)
        # ------------------------停靠站显示结束-------------------------------#

        self.SetSizer(fgSizer)
        self.Layout()

    # 列表标题禁用可拉伸
    def OnColumnDrag(self, evt):
        evt.Veto()
        return

    def OnMouseLeftDown(self, evt):
        self.Show(False)
        self.Destroy()
        # self.Refresh()
        # self.ldPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
        # self.wPos = self.ClientToScreen((0, 0))
        # self.pnl.CaptureMouse()

    def OnMouseMotion(self, evt):
        self.Show(False)
        self.Destroy()

        # if evt.Dragging() and evt.LeftIsDown():
        #     dPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
        #     nPos = (self.wPos.x + (dPos.x - self.ldPos.x),
        #             self.wPos.y + (dPos.y - self.ldPos.y))
        #     self.Move(nPos)

    def OnMouseLeftUp(self, evt):
        self.Show(False)
        self.Destroy()
        # if self.pnl.HasCapture():
        #     self.pnl.ReleaseMouse()

    def OnRightUp(self, evt):
        self.Show(False)
        self.Destroy()
