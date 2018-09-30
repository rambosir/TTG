# -*- coding:utf-8 -*-
import wx
import wx.aui
import wx.dataview as dv
import wx.lib.agw.ultimatelistctrl as ULC
import wx.lib.agw.gradientbutton as GB
import wx.lib.agw.genericmessagedialog as GMD
import wx.html2
import wx.lib.sized_controls as sc
from TrainTicketGo.util import Req, Common
import json
import random
import os
import thread
import time
import sys
import re


class Init(dv.PyDataViewModel):
    def __init__(self, *args, **kwargs):
        parent = args[0]
        self.passenger_data = kwargs['passenger_data']
        self.two_isOpenClick = kwargs['two_isOpenClick']
        self.other_isOpenClick = kwargs['other_isOpenClick']

        self.passengers_panel = wx.Panel(parent)
        passengers_sizer = wx.BoxSizer(wx.VERTICAL)

        self.btn = GB.GradientButton(self.passengers_panel, -1, None, u"增加")
        self.payBtn = GB.GradientButton(self.passengers_panel, -1, None, u"删除", (60, 5))
        self.reloadBtn = GB.GradientButton(self.passengers_panel, -1, None, u"加载联系人", (120, 5))
        self.btn.Bind(wx.EVT_BUTTON, self.addContact)
        self.payBtn.Bind(wx.EVT_BUTTON, lambda evt, p_panel=self.passengers_panel: self.delContact(evt, p_panel))
        self.reloadBtn.Bind(wx.EVT_BUTTON, self.operatedAfterInit)

        passengers_sizer.Add(self.btn, 0, wx.ALL, 5)
        # passengers_sizer.Add(self.payBtn, 0, wx.ALL, 5)

        agwStyle = (ULC.ULC_HAS_VARIABLE_ROW_HEIGHT | wx.LC_REPORT |
                    wx.LC_VRULES | wx.LC_HRULES | ULC.ULC_SINGLE_SEL | ULC.ULC_AUTO_CHECK_CHILD)
        self.contactlist = contactlist = ULC.UltimateListCtrl(self.passengers_panel, wx.ID_ANY,
                                                              size=(400, 300),
                                                              agwStyle=agwStyle)
        self.contactlist.Bind(wx.EVT_LIST_COL_BEGIN_DRAG, self.OnColumnDrag)

        # orderlist.InsertColumn(0, u'序号', format=ULC.ULC_FORMAT_CENTER, width=50)
        info = ULC.UltimateListItem()
        info._mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_FORMAT | ULC.ULC_MASK_CHECK
        info._format = 0
        info._kind = 1
        info._text = u"序号"
        contactlist.InsertColumnInfo(0, info)
        contactlist.SetColumnWidth(0, 80)

        contactlist.InsertColumn(1, u'姓名', format=ULC.ULC_FORMAT_CENTER, width=80)
        contactlist.InsertColumn(2, u'证件类型', format=ULC.ULC_FORMAT_CENTER, width=150)
        contactlist.InsertColumn(3, u'证件号码', format=ULC.ULC_FORMAT_CENTER, width=150)
        contactlist.InsertColumn(4, u'手机/电话', format=ULC.ULC_FORMAT_CENTER, width=150)
        contactlist.InsertColumn(5, u'旅客类型', format=ULC.ULC_FORMAT_CENTER, width=150)
        contactlist.InsertColumn(6, u'核验状态', format=ULC.ULC_FORMAT_CENTER, width=100)
        contactlist.InsertColumn(7, u'操作', format=ULC.ULC_FORMAT_CENTER, width=50)
        # contactlist.InsertColumn(8, u'', format=ULC.ULC_FORMAT_CENTER, width=0)
        # contactlist.SetColumnWidth(8, 0)

        # 初始化联系人
        self.initPassengerData(self.passenger_data)
        passengers_sizer.Add(self.contactlist, 0, wx.ALL | wx.EXPAND, 5)

        self.passengers_panel.SetSizer(passengers_sizer)
        self.passengers_panel.Layout()

        sizer = wx.BoxSizer()
        sizer.Add(self.passengers_panel, 1, wx.EXPAND)
        parent.SetSizer(sizer)
        # wx.CallAfter(self.nb.SendSizeEvent)

    def initPassengerData(self, passenger_data):
        self.imgs = {}
        total_times_str = None
        self.passenger_id_type_codes = []
        if isinstance(passenger_data, (str, unicode)):
            return

        for d in passenger_data:

            passenger_name = d.get('passenger_name')
            passenger_id_type_code = d.get('passenger_id_type_code')
            passenger_id_type_name = d.get('passenger_id_type_name')
            passenger_id_no = d.get('passenger_id_no')
            mobile_no = d.get('mobile_no')
            passenger_type_name = d.get('passenger_type_name')
            passenger_flag = d.get('passenger_flag')
            index_id = d.get('index_id')
            total_times = d.get('total_times')

            index = self.contactlist.InsertStringItem(sys.maxint, wx.EmptyString)

            s = str(index + 1)

            self.contactlist.SetStringItem(index, 0, label=(s if index_id != '0' else '    ' + s),
                                           it_kind=(1 if index_id != '0' else 0))

            if passenger_id_type_code == '1':
                total_times_str = u'已通过' if total_times in self.two_isOpenClick else u'待核验'
            else:
                total_times_str = u'已通过' if total_times in self.other_isOpenClick else u'待核验'

            self.passenger_id_type_codes.append(passenger_id_type_code)

            self.contactlist.SetStringItem(index, 1, passenger_name)
            self.contactlist.SetStringItem(index, 2, passenger_id_type_name)
            self.contactlist.SetStringItem(index, 3, passenger_id_no)
            self.contactlist.SetStringItem(index, 4, mobile_no)
            self.contactlist.SetStringItem(index, 5, unicode(passenger_type_name))
            self.contactlist.SetStringItem(index, 6, total_times_str)

            if index_id != '0':
                bitmap = wx.StaticBitmap(self.contactlist, wx.ID_ANY, Common.del_icon.Bitmap, wx.DefaultPosition,
                                         wx.DefaultSize, 0)

                self.imgs[bitmap.GetId()] = index
                self.contactlist.SetItemWindow(index, 7, bitmap, expand=True)
                bitmap.Bind(wx.EVT_LEFT_DOWN, lambda evt, p_panel=self.passengers_panel: self.delContact(evt, p_panel))

                # self.contactlist.SetStringItem(index, 8, passenger_id_type_code)

    def OnColumnDrag(self, evt):
        evt.Veto()
        return

    # 新增
    def addContact(self, event):

        # 判断是否可预定
        if self.passenger_data and isinstance(self.passenger_data, (str, unicode)):
            wx.MessageBox(u'暂不能添加联系人，原因【%s' % self.passenger_data + u'】，如需添加请前往12306操作')
            return

        dlg = FormDialog(self, -1)
        dlg.CenterOnScreen()

        # this does not return until the dialog is closed.
        val = dlg.ShowModal()

        if val == wx.ID_OK:
            passenger_name = self.name.GetValue()
            passenger_sex_code = self.sex[self.sexChoice.GetCurrentSelection()]
            passenger_sex_name = self.sexChoice.GetStringSelection()
            passenger_country_code = self.country[self.countryChoice.GetCurrentSelection()]
            passenger_id_type_code = self.idtype[self.idtypeChoice.GetCurrentSelection()]
            passenger_id_type_name = self.idtypeChoice.GetStringSelection()
            passenger_id_no = self.id_no.GetValue()
            passenger_mobile_no = self.mobile_no.GetValue()

            add_params = {
                'passenger_name': passenger_name.encode('utf-8'),
                'sex_code': passenger_sex_code,
                'country_code': passenger_country_code,
                'passenger_id_type_code': passenger_id_type_code,
                'passenger_id_no': passenger_id_no,
                'mobile_no': passenger_mobile_no,
                'passenger_type': '1'
            }
            res = Req.post(Common.add_passenger_url, add_params, Common.headers)
            rs_zipped = Req.zippedDecompress(res)
            if rs_zipped:

                rs_json = json.loads(rs_zipped)
                rs_data = rs_json.get('data')
                data_message = rs_data.get('message')

                if rs_data and rs_data.get('flag'):
                    wx.MessageBox(u'添加成功')
                    self.operatedAfterInit(None)

                else:
                    wx.MessageBox(u'添加失败，原因【%s' % data_message + u'】')

        dlg.Destroy()

    # 删除
    def delContact(self, event, parent):
        obj = event.GetEventObject()
        # 如果是点击列表中图标删除
        if isinstance(obj, wx.StaticBitmap):
            # dlg = wx.MessageDialog(parent, u'确定删除？', u'提示', wx.YES_NO | wx.ICON_WARNING)
            dlg = GMD.GenericMessageDialog(parent, u'确定删除当前联系人吗？', u'提示',
                                           wx.YES_NO | GMD.GMD_USE_GRADIENTBUTTONS | wx.ICON_QUESTION)
            result = dlg.ShowModal() == wx.ID_YES
            if result:
                idx = self.imgs[obj.GetId()]
                passenger_id_type_code = self.passenger_id_type_codes[idx]  # self.contactlist.GetItem(idx, 8).GetText()
                passenger_name = self.contactlist.GetItem(idx, 1).GetText()
                passenger_id_no = self.contactlist.GetItem(idx, 3).GetText()

                req_data = {'passenger_name': passenger_name.encode('utf-8') + '#',
                            'passenger_id_type_code': passenger_id_type_code + '#',
                            'passenger_id_no': passenger_id_no + '#', 'isUserSelf': 'N'}

                res = Req.post(Common.delete_passenger_url, req_data, Common.headers)
                rs_zipped = Req.zippedDecompress(res)
                if rs_zipped:

                    rs_json = json.loads(rs_zipped)
                    status = rs_json.get('status')
                    json_data = rs_json.get('data')
                    message = json_data.get('message')

                    if status and json_data and json_data.get('flag'):

                        wx.MessageBox(u'删除成功')
                        self.operatedAfterInit(None)

                    else:
                        wx.MessageBox(u'删除失败，原因【%s' % message + u'】')

        # 按钮点击删除
        if isinstance(obj, GB.GradientButton):

            itemCount = self.contactlist.GetItemCount()
            temp_name_list = []
            temp_id_type_code_list = []
            temp_id_no = []
            i = 0

            for ic in range(itemCount):

                isChecked = self.contactlist.GetItem(ic).IsChecked()

                if isChecked:
                    passenger_id_type_code = self.passenger_id_type_codes[
                        ic]  # self.contactlist.GetItem(ic, 8).GetText()
                    passenger_name = self.contactlist.GetItem(ic, 1).GetText()
                    passenger_id_no = self.contactlist.GetItem(ic, 3).GetText()

                    temp_id_type_code_list.append(passenger_id_type_code)
                    temp_id_no.append(passenger_id_no)
                    temp_name_list.append(passenger_name)
                    i += 1

            if i == 0:
                msg = GMD.GenericMessageDialog(parent, u'请选择联系人', u'提示',
                                               wx.OK | GMD.GMD_USE_GRADIENTBUTTONS | wx.ICON_INFORMATION)
                msg.ShowModal()
                msg.Destroy()
                return

            prompt_dlg = GMD.GenericMessageDialog(parent, u'确定删除选中的联系人吗？', u'提示',
                                                  wx.YES_NO | GMD.GMD_USE_GRADIENTBUTTONS | wx.ICON_WARNING)

            r = prompt_dlg.ShowModal() == wx.ID_YES
            if r:
                id_type_codes = '#'.join(p for p in temp_id_type_code_list) + '#'
                id_nos = '#'.join(p for p in temp_id_no) + '#'
                names = '#'.join(p for p in temp_name_list) + '#'
                print(id_type_codes, id_nos, names)
                req_data = {'passenger_name': names.encode('utf-8') + '#',
                            'passenger_id_type_code': id_type_codes + '#',
                            'passenger_id_no': id_nos + '#', 'isUserSelf': 'N'}

                res = Req.post(Common.delete_passenger_url, req_data, Common.headers)
                rs_zipped = Req.zippedDecompress(res)
                if rs_zipped:
                    rs_json = json.loads(rs_zipped)
                    status = rs_json.get('status')
                    json_data = rs_json.get('data')
                    message = json_data.get('message')
                    if status and json_data and json_data.get('flag'):

                        wx.MessageBox(u'删除成功')
                        self.operatedAfterInit(None)

                    else:
                        wx.MessageBox(u'删除失败，原因【%s' % message + u'】')

    # 操作之后，重新初始化联系人
    def operatedAfterInit(self, event):
        time.sleep(2)

        passenger_data, two_isOpenClick, other_isOpenClick = Common.GetPassenger(Common.headers)
        # 初始化联系人
        del self.passenger_data[:]
        for d in passenger_data:
            self.passenger_data.append(d)

        self.contactlist.DeleteAllItems()
        self.initPassengerData(self.passenger_data)

    def reloadContact(self):
        pass


# 联系人dialog窗体
class FormDialog(sc.SizedDialog):
    def __init__(self, parent, id):
        sc.SizedDialog.__init__(self, None, -1, u'添加联系人',
                                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BOX)

        pane = self.GetContentsPane()
        pane.SetSizerType("form")

        # row 1
        wx.StaticText(pane, -1, u"姓名")
        parent.name = wx.TextCtrl(pane, -1, "", size=(180, -1), validator=TextObjectValidator(), name='pname')
        parent.name.SetSizerProps(expand=True)

        # row 2
        wx.StaticText(pane, -1, u"性别")
        parent.sexChoice = wx.Choice(pane, -1, choices=[u"男", u"女"])
        parent.sexChoice.SetSelection(0)
        parent.sex = [u'M', u'F']

        # row 3
        wx.StaticText(pane, -1, u"国家/地区")  # CN
        parent.countryChoice = wx.Choice(pane, -1, choices=[u"中国CHINA"])
        parent.countryChoice.SetSelection(0)
        parent.country = [u'CN']

        # row 4
        wx.StaticText(pane, -1, u"证件类型")  # 1,C,G,B
        pane.idtypeChoice = parent.idtypeChoice = wx.Choice(pane, -1, choices=[u"二代身份证", u'港澳通行证', u'台湾通行证',
                                                                               u'护照'])

        parent.idtypeChoice.SetSelection(0)
        parent.idtype = [u'1', u'C', u'G', u'B']

        # row 5
        wx.StaticText(pane, -1, u"证件号码")
        parent.id_no = wx.TextCtrl(pane, -1, validator=TextObjectValidator(), name='id_no')
        parent.id_no.SetSizerProps(expand=True)

        wx.StaticText(pane, -1, u"手机号码")
        parent.mobile_no = wx.TextCtrl(pane, -1, size=(60, -1))
        parent.mobile_no.SetSizerProps(expand=True)

        # add dialog buttons
        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))

        self.Fit()
        self.SetMinSize(self.GetSize())


# 验证姓名和文本框
class TextObjectValidator(wx.PyValidator):
    def __init__(self):
        wx.PyValidator.__init__(self)

    def Clone(self):
        return TextObjectValidator()

    def Validate(self, win):

        textCtrl = self.GetWindow()
        text = textCtrl.GetValue()
        textCtrlName = textCtrl.GetName()

        if len(text) == 0:
            wx.MessageBox(u"联系人信息填写不完成，请检查", "Error")
            textCtrl.SetBackgroundColour("pink")
            textCtrl.SetFocus()
            textCtrl.Refresh()
            return False

        # 如果选择的是证件类型是身份证类型，验证身份证号是否正确
        if win.idtypeChoice.GetCurrentSelection() == 0:
            if textCtrlName == 'id_no':
                flag = False
                for r in Common.id_no_reg:
                    print(re.match(r, text))
                    if re.match(r, text):
                        flag = True
                        break

                if not flag:
                    wx.MessageBox(u"证件号不正确请检查", "Error")
                    textCtrl.SetBackgroundColour("pink")
                    textCtrl.SetFocus()
                    textCtrl.Refresh()
                    return False

        textCtrl.SetBackgroundColour(
            wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
        textCtrl.Refresh()
        return True

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True  # Prevent wxDialog from complaining.
