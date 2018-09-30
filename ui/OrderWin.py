# -*- coding:utf-8 -*-
import wx
import wx.aui
import wx.dataview as dv
import wx.lib.agw.ultimatelistctrl as ULC
import wx.lib.agw.gradientbutton as GB
import wx.html2
from TrainTicketGo.util import Req, Common
import json
import random
import os
import thread
import time
from selenium import webdriver
from ghost import Ghost, Session


class Init(dv.PyDataViewModel):
    def __init__(self, **kwargs):
        parent = kwargs['parent']

        self.sequence_no = None
        self.nb = wx.aui.AuiNotebook(parent, style=wx.aui.AUI_NB_SCROLL_BUTTONS)

        # 未完成订单
        self.InCompleteOrder(parent)
        # 已完成订单
        self.CompleteOrder(parent)

        sizer = wx.BoxSizer()
        sizer.Add(self.nb, 1, wx.EXPAND)
        parent.SetSizer(sizer)
        wx.CallAfter(self.nb.SendSizeEvent)

    def InCompleteOrder(self, parent):
        ##########################未完成订单开始###############################
        incomplete_order_panel = wx.Panel(parent)
        incomplete_order_sizer = wx.BoxSizer(wx.VERTICAL)

        self.btn = GB.GradientButton(incomplete_order_panel, -1, None, u"查询订单")
        # self.payBtn = GB.GradientButton(incomplete_order_panel, -1, None, u"去12306支付", (80, 5))
        self.btn.Bind(wx.EVT_BUTTON, self.toQueryInCompleteOrder)
        # self.payBtn.Bind(wx.EVT_BUTTON, self.toGo12306Pay)

        incomplete_order_sizer.Add(self.btn, 0, wx.ALL, 5)
        # incomplete_order_sizer.Add(self.payBtn, 0, wx.ALL, 5)

        agwStyle = (ULC.ULC_HAS_VARIABLE_ROW_HEIGHT | wx.LC_REPORT |
                    wx.LC_VRULES | wx.LC_HRULES | wx.LC_SINGLE_SEL)
        self.orderlist = orderlist = ULC.UltimateListCtrl(incomplete_order_panel, wx.ID_ANY,
                                                          size=(400, 300),
                                                          agwStyle=agwStyle)
        self.orderlist.Bind(wx.EVT_LIST_COL_BEGIN_DRAG, self.OnColumnDrag)

        orderlist.InsertColumn(0, u'序号', format=ULC.ULC_FORMAT_CENTER, width=50)
        orderlist.InsertColumn(1, u'车次信息', format=ULC.ULC_FORMAT_CENTER, width=300)
        orderlist.InsertColumn(2, u'席位信息', format=ULC.ULC_FORMAT_CENTER, width=150)
        orderlist.InsertColumn(3, u'旅客信息', format=ULC.ULC_FORMAT_CENTER, width=150)
        orderlist.InsertColumn(4, u'票款金额', format=ULC.ULC_FORMAT_CENTER, width=100)
        orderlist.InsertColumn(5, u'车票状态', format=ULC.ULC_FORMAT_CENTER, width=180)

        incomplete_order_sizer.Add(self.orderlist, 0, wx.ALL | wx.EXPAND, 5)

        incomplete_order_panel.SetSizer(incomplete_order_sizer)
        incomplete_order_panel.Layout()

        self.nb.AddPage(incomplete_order_panel, u"未完成订单")
        ##########################未完成订单结束###############################

    # 已完成订单
    def CompleteOrder(self, parent):

        complete_order_panel = wx.Panel(parent)
        complete_order_sizer = wx.BoxSizer(wx.VERTICAL)

        self.complete_order_btn = GB.GradientButton(complete_order_panel, -1, None, u"查询订单")
        self.complete_order_btn.Bind(wx.EVT_BUTTON, self.toQueryCompleteOrder)
        complete_order_sizer.Add(self.complete_order_btn, 0, wx.ALL, 5)

        self.ch = wx.Choice(complete_order_panel, -1, (80, 5), choices=[u'按订票日期查询', u'按乘车日期查询'])
        self.queryType = [1, 2]
        self.ch.SetSelection(0)
        # self.ch.Bind(wx.EVT_CHOICE, self.EvtChoice)

        self.startDate = wx.DatePickerCtrl(complete_order_panel, pos=(210, 5), size=(120, -1), style=wx.DP_DROPDOWN)
        # dpc.Bind(wx.EVT_DATE_CHANGED, self.OnDateChanged)

        wx.StaticText(complete_order_panel, -1, u'－', (335, 5))
        self.endDate = wx.DatePickerCtrl(complete_order_panel, pos=(350, 5), size=(120, -1), style=wx.DP_DROPDOWN)

        agwStyle = (ULC.ULC_HAS_VARIABLE_ROW_HEIGHT | wx.LC_REPORT |
                    wx.LC_VRULES | wx.LC_HRULES | wx.LC_SINGLE_SEL)
        self.complete_orderlist = complete_orderlist = ULC.UltimateListCtrl(complete_order_panel, wx.ID_ANY,
                                                                            size=(400, 300),
                                                                            agwStyle=agwStyle)
        self.complete_orderlist.Bind(wx.EVT_LIST_COL_BEGIN_DRAG, self.OnColumnDrag)

        complete_orderlist.InsertColumn(0, u'序号', format=ULC.ULC_FORMAT_CENTER, width=50)
        complete_orderlist.InsertColumn(1, u'车次信息', format=ULC.ULC_FORMAT_CENTER, width=300)
        complete_orderlist.InsertColumn(2, u'席位信息', format=ULC.ULC_FORMAT_CENTER, width=150)
        complete_orderlist.InsertColumn(3, u'旅客信息', format=ULC.ULC_FORMAT_CENTER, width=150)
        complete_orderlist.InsertColumn(4, u'票款金额', format=ULC.ULC_FORMAT_CENTER, width=100)
        complete_orderlist.InsertColumn(5, u'车票状态', format=ULC.ULC_FORMAT_CENTER, width=180)

        complete_order_sizer.Add(self.complete_orderlist, 0, wx.ALL | wx.EXPAND, 5)

        complete_order_panel.SetSizer(complete_order_sizer)
        complete_order_panel.Layout()
        self.nb.AddPage(complete_order_panel, u"已完成订单")

    def EvtChoice(self, event):
        self.ch.Append("A new item")
        print(event.GetString())

    def OnDateChanged(self):
        pass

    def OnColumnDrag(self, evt):
        evt.Veto()
        return

    # 查询未完成订单
    def toQueryInCompleteOrder(self, event):
        Common.startWorkFunc(self.queryInCompleteOrder, self.queryInCompleteOrderSuccess)

    # 开始查询未完成订单
    def queryInCompleteOrder(self, *args, **kwargs):
        self.orderlist.DeleteAllItems()
        # 查詢未完成訂單
        data = {'_json_att': ''}
        order_nocomplete = Req.post(Common.query_myorder_nocomplete_url, data, Common.headers)
        order_nocomplete_unzipped = Req.zippedDecompress(order_nocomplete)
        if order_nocomplete_unzipped:
            order_nocomplete_json = json.loads(order_nocomplete_unzipped)
            return order_nocomplete_json
        else:
            return {}

    # 查询未完成订单成功success
    def queryInCompleteOrderSuccess(self, delayedResult, *args, **kwargs):
        try:
            order_nocomplete_json = delayedResult.get()
        except Exception, e:
            print(u'查询未完成订单 %s 异常:%s' % (delayedResult.getJobID, e))

        order_nocomplete_status = order_nocomplete_json.get('status')
        order_nocomplete_data = order_nocomplete_json.get('data')

        # 查询订单数据成功返回
        if order_nocomplete_status and order_nocomplete_data:
            orders = order_nocomplete_data.get('orderDBList')

            for index, o in enumerate(orders):
                # 车次号
                train_code_page = o.get('train_code_page')
                # 订单号
                sequence_no = o.get('sequence_no')
                self.sequence_no = sequence_no
                # 订单日期
                order_date = o.get('order_date')
                # 乘车时间：
                start_train_date_page = o.get('start_train_date_page')
                # 总票数
                ticket_totalnm = o.get('ticket_totalnm')
                # 订单总额
                ticket_total_price_page = o.get('ticket_total_price_page')
                #
                tickets = o.get('tickets')
                # 始发站
                from_station_name_page = o.get('from_station_name_page')
                # 到站
                to_station_name_page = o.get('to_station_name_page')
                # 支付状态
                pay_resign_flag = o.get('pay_resign_flag')
                for i, t in enumerate(tickets):
                    # 车厢号
                    coach_name = t.get('coach_name')
                    # 座位号
                    seat_name = t.get('seat_name')
                    # 座位类型名称
                    seat_type_name = t.get('seat_type_name')

                    # 乘客信息
                    passenger_id_type_name = t.get('passengerDTO').get('passenger_id_type_name')
                    passenger_name = t.get('passengerDTO').get('passenger_name')

                    # 车次信息
                    from_station_name = t.get('stationTrainDTO').get('from_station_name')
                    to_station_name = t.get('stationTrainDTO').get('to_station_name')

                    # 票价
                    str_ticket_price_page = t.get('str_ticket_price_page')
                    ticket_status_name = t.get('ticket_status_name')

                    self.orderlist.Append((i + 1, (
                        start_train_date_page + ' ' + train_code_page + ' ' + from_station_name + u'-' + to_station_name),
                                           coach_name + u'车厢' + ' ' + seat_name + ' ' + seat_type_name,
                                           passenger_name + '(' + passenger_id_type_name + ')',
                                           str_ticket_price_page, ticket_status_name))

    # 查询已完成订单
    def toQueryCompleteOrder(self, event):
        # thread.start_new_thread(self.queryCompleteOrder, ())
        Common.startWorkFunc(self.queryCompleteOrder, self.queryCompleteOrderSuccess)

    def queryCompleteOrder(self, *args, **kwargs):

        self.complete_orderlist.DeleteAllItems()

        startDate = self.startDate.GetValue()
        endDate = self.endDate.GetValue()

        # 查詢已完成訂單
        data = {'queryType': self.queryType[self.ch.GetCurrentSelection()], 'come_from_flag': 'my_order',
                'query_where': 'G', 'sequeue_train_name': '',
                'queryStartDate': startDate.Format('%Y-%m-%d'), 'queryEndDate': endDate.Format('%Y-%m-%d')}

        order_complete = Req.post(Common.query_myorder_complete_url, data, Common.headers)
        order_complete_unzipped = Req.zippedDecompress(order_complete)

        if order_complete_unzipped:
            order_complete_json = json.loads(order_complete_unzipped)
            return order_complete_json
        else:
            return {}

    def queryCompleteOrderSuccess(self, delayedResult, *args, **kwargs):
        try:
            order_complete_json = delayedResult.get()
        except Exception, e:
            print(u'查询已完成订单 %s 异常:%s' % (delayedResult.getJobID, e))

        order_complete_status = order_complete_json.get('status')
        order_complete_data = order_complete_json.get('data')

        if order_complete_status and order_complete_data:

            orderDTODataList = order_complete_data.get('OrderDTODataList')
            for o in orderDTODataList:

                # 车次号
                train_code_page = o.get('train_code_page')
                # 订单号
                sequence_no = o.get('sequence_no')
                self.sequence_no = sequence_no
                # 订单日期
                order_date = o.get('order_date')
                # 乘车时间：
                start_train_date_page = o.get('start_train_date_page')
                # 总票数
                ticket_totalnm = o.get('ticket_totalnm')
                # 订单总额
                ticket_total_price_page = o.get('ticket_total_price_page')
                # 始发站
                from_station_name_page = o.get('from_station_name_page')
                # 到站
                to_station_name_page = o.get('to_station_name_page')
                # 支付状态
                pay_resign_flag = o.get('pay_resign_flag')

                tickets = o.get('tickets')

                for i, t in enumerate(tickets):
                    # 车厢号
                    coach_name = t.get('coach_name')
                    # 座位号
                    seat_name = t.get('seat_name')
                    # 座位类型名称
                    seat_type_name = t.get('seat_type_name')

                    # 乘客信息
                    passenger_id_type_name = t.get('passengerDTO').get('passenger_id_type_name')
                    passenger_name = t.get('passengerDTO').get('passenger_name')

                    # 车次信息
                    from_station_name = t.get('stationTrainDTO').get('from_station_name')
                    to_station_name = t.get('stationTrainDTO').get('to_station_name')

                    # 票价
                    str_ticket_price_page = t.get('str_ticket_price_page')
                    ticket_status_name = t.get('ticket_status_name')

                    self.complete_orderlist.Append((i + 1, (
                        start_train_date_page + ' ' + train_code_page + ' ' + from_station_name + u'-' + to_station_name),
                                                    coach_name + u'车厢' + ' ' + seat_name + ' ' + seat_type_name,
                                                    passenger_name + '(' + passenger_id_type_name + ')',
                                                    str_ticket_price_page, ticket_status_name))

    # 跳转至12306支付
    def toGo12306Pay(self, event):
        # chromedriver = 'C:/Users/libin/Desktop/12306/TrainTicketGo/ui/chromedriver.exe'
        # os.environ["webdriver.chrome.driver"] = chromedriver
        # dr = webdriver.Chrome(chromedriver)
        # dr.get('https://kyfw.12306.cn/otn/queryOrder/initNoComplete')
        # dr.maximize_window()
        # dr.delete_all_cookies()
        # ss = Common.headers['Cookie'].split(';')
        # for s in ss:
        #     sk = {}
        #     list2 = s.split("=")
        #     sk[list2[0].lstrip()] = list2[1]
        #     dr.add_cookie({'name': list2[0].lstrip(), 'value': list2[1]})
        # dr.get('https://kyfw.12306.cn/otn/queryOrder/initNoComplete')
        # time.sleep(3)
        # dr.quit()

        # if self.orderlist.GetItemCount() > 0:
        queryInCompleteOrder_thread = thread.start_new_thread(self.go12306Pay, ())

    def go12306Pay(self):
        # data = {'sequence_no': self.sequence_no, 'pay_flag': 'pay', '_json_att': ''}
        # continue_pay_rs = Req.post(Common.continue_pay_nocamplete_url, data, Common.headers)
        # continue_pay_unzipped = Req.zippedDecompress(continue_pay_rs)
        # print(continue_pay_unzipped)
        # if continue_pay_unzipped:
        #     continue_pay_json = json.loads(continue_pay_unzipped)
        #     status = continue_pay_json.get('status')
        #     data = continue_pay_json.get('data')
        #     if data and data.get('existError') == 'Y':
        #         wx.MessageBox(data.get('errorMsg'))
        #         return


        wx.CallAfter(self.openBrowser)
        # 校验是否登录状态已失效
        # Req.get(Common.init_my12306_url, Common.headers)
        # check_user_rs = Req.post(Common.check_user_url, {}, Common.headers)
        # check_user_unzipped = Req.zippedDecompress(check_user_rs)
        # if check_user_unzipped:
        #     check_user_json = json.loads(check_user_unzipped)
        #     status = check_user_json.get('status')
        #     check_user_data = check_user_json.get('data')
        #     # 登录状态未失效
        #     if status and check_user_data and check_user_data.get('flag'):
        #         pass

    def openBrowser(self):
        chromedriver = 'C:/Users/Ben/Desktop/12306/TrainTicketGo/ui/chromedriver.exe'
        os.environ["webdriver.chrome.driver"] = chromedriver
        # DesiredCapabilities.CHROME['ignoreProtectedModeSettings'] = True

        dr = webdriver.Chrome(chromedriver)
        dr.get(Common.otn_url)
        dr.maximize_window()
        dr.delete_all_cookies()

        cookies = Common.headers['Cookie'].split(';')
        for c in cookies:
            sk = {}
            tmp_list = c.split("=")
            sk[tmp_list[0].lstrip()] = tmp_list[1]
            dr.add_cookie({'name': tmp_list[0].lstrip(), 'value': tmp_list[1]})

        dr.get(Common.init_nocomplete_url)

        # dialog = MyBrowser(None, -1)
        # dialog.browser.LoadURL('https://kyfw.12306.cn/otn/queryOrder/initNoComplete')
        # dialog.Show()


class MyBrowser(wx.Dialog):
    def __init__(self, *args, **kwds):
        wx.Dialog.__init__(self, *args, **kwds)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.browser = wx.html2.WebView.New(self)
        self.browser.Bind(wx.html2.EVT_WEBVIEW_LOADED, self.loaded)
        self.browser.LoadURL(Common.otn_url)

        sizer.Add(self.browser, 1, wx.EXPAND, 10)
        self.SetSizer(sizer)
        self.SetSize((1024, 700))

    def loaded(self, e):
        if e.GetURL() == 'about:blank':  # Skip if it's a blank page.
            return
        self.browser.RunScript('document.cookie=' + Common.headers['Cookie'])
