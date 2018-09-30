# -*- coding:utf-8 -*-
# author: BenLee

# wx lib
import cStringIO
import json
import re
import time
import wx
import wx.lib.agw.genericmessagedialog as GMD
import js2py

from util import User as u
from ui import TicketWin
from util import Req, Common


# ----------------------------------------------------------------------

# HEADERS = Common.headers


# 登录成功主窗体
class MainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        # user, headers, passenger_data, login_frame,two_isOpenClick=two_isOpenClick, other_isOpenClick=other_isOpenClick
        wx.Frame.__init__(self, parent=None, title=kwargs['user'].username, pos=(100, 100), size=(1080, 650),
                          style=wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.TAB_TRAVERSAL)

        TicketWin.Init(self, *args, **kwargs)
        self.Centre()
        self.Show(True)

        # 设置隐藏到托盘
        self.taskBarIcon = Common.TaskBarIcon(self)
        # 右上角关闭
        self.Bind(wx.EVT_CLOSE, lambda evt, fram_obj=kwargs['login_frame']: self.on_close_window(evt, fram_obj))
        self.Bind(wx.EVT_ICONIZE, self.on_icon_fiy)

    # 点击最小化时，隐藏界面，到托盘
    def on_icon_fiy(self, event):
        self.Hide()

    # 关闭窗体
    def on_close_window(self, event, fram_obj):
        dlg = GMD.GenericMessageDialog(self, u'您已登录，确定退出？', u'提示',
                                       wx.YES_NO | GMD.GMD_USE_GRADIENTBUTTONS | wx.ICON_QUESTION)
        # dlg = wx.MessageDialog(self, u'您已登录，确定退出？', u'提示', wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal() == wx.ID_YES
        if result:
            self.Destroy()
            # fram_obj.login_btn.Enable(True)
            # fram_obj.login_btn.SetLabel(u'登录')
            # fram_obj.refresh_btn.Enable(True)
            # fram_obj.refresh_click(None)
            # fram_obj.Show(True)
            fram_obj.Destroy()


# 登录窗体
class LoginFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, id=-1, title=u"登   录", size=(500, 400),
                          style=wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.TAB_TRAVERSAL)

        # self.SetBackgroundColour(wx.Colour(246, 246, 246))
        self.loginPanel = wx.Panel(self, id=wx.ID_ANY, size=(500, 400))

        fgSizer = wx.FlexGridSizer(4, 2, 2, 2)
        fgSizer.AddGrowableCol(0)
        fgSizer.AddGrowableCol(1)
        fgSizer.AddGrowableRow(0)
        fgSizer.AddGrowableRow(1)
        fgSizer.AddGrowableRow(2)
        fgSizer.AddGrowableRow(3)
        fgSizer.SetFlexibleDirection(wx.BOTH)

        self.pos = []

        # 获取ck、动态js url

        zf_url = 'https://kyfw.12306.cn/otn/HttpZF/GetJS'
        zf_result = Req.get(zf_url, Common.headers)
        cvt_zf_result = Req.zippedDecompress(zf_result)
        # print(cvt_zf_result)
        # data = js2py.EvalJs(cvt_zf_result)

        cookies, dynamic_url = self.login_init()
        print(cookies)
        Common.headers['Cookie'] = cookies

        # 加载12306动态js
        self.dynamic_js_init(dynamic_url)
        # 获取12306验证码
        code_bmp = self.get_new_code_img()

        self.username_label = wx.StaticText(self.loginPanel, wx.ID_ANY, u"用户名", wx.DefaultPosition, wx.DefaultSize, 0)
        fgSizer.Add(self.username_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5)

        self.username = wx.TextCtrl(self.loginPanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                    (290, -1), wx.TE_RICH)
        fgSizer.Add(self.username, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.password_label = wx.StaticText(self.loginPanel, wx.ID_ANY, u"密码", wx.DefaultPosition, wx.DefaultSize, 0)
        fgSizer.Add(self.password_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5)

        self.password = wx.TextCtrl(self.loginPanel, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
                                    (290, -1),
                                    wx.TE_PASSWORD | wx.TE_RICH)
        fgSizer.Add(self.password, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        # 验证码
        self.randCode_label = wx.StaticText(self.loginPanel, wx.ID_ANY, u"验证码", wx.DefaultPosition, wx.DefaultSize, 0)
        fgSizer.Add(self.randCode_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5)

        self.codeBitMap = wx.StaticBitmap(self.loginPanel, -1, code_bmp, wx.DefaultPosition, wx.DefaultSize)
        fgSizer.Add(self.codeBitMap, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        # 刷新验证码图标
        refreshImg = Common.codeRefreshMark.GetBitmap()
        self.refreshImg = wx.StaticBitmap(self.codeBitMap, wx.ID_ANY, refreshImg)
        self.refreshImg.SetPosition((260, 4))
        self.refreshImg.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.refreshImg.Bind(wx.EVT_LEFT_DOWN, self.refresh_click)

        # fgSizer.AddSpacer((0, 0), 1, 0, 5)
        fgSizer.AddSpacer(1)

        # #验证码图片Maker list
        self.imageContainer = []
        self.codeBitMap.Bind(wx.EVT_LEFT_DOWN, self.on_draw_image)

        bSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.login_btn = wx.Button(self.loginPanel, 1, u"登录", size=(190, -1))
        self.Bind(wx.EVT_BUTTON, self.login_click, self.login_btn)
        bSizer.Add(self.login_btn, 0, wx.ALL, 5)

        self.refresh_btn = wx.Button(self.loginPanel, 2, u"刷新验证码")
        self.Bind(wx.EVT_BUTTON, self.refresh_click, self.refresh_btn)
        bSizer.Add(self.refresh_btn, 0, wx.ALL, 5)

        # 綁定鍵盤空格事件
        self.loginPanel.Bind(wx.EVT_KEY_DOWN, self.space_click)

        fgSizer.Add(bSizer, 1, wx.ALL, 5)
        self.SetSizer(fgSizer)
        self.Layout()

        # 居中显示
        self.Centre()
        # 创建就显示Frame框架
        self.Show(True)

        # 右上角关闭
        self.Bind(wx.EVT_CLOSE, self.on_close_window)

    # 登录初始化
    def login_init(self):

        if Common.headers.get('Cookie'): del Common.headers['Cookie']
        init_res = Req.get(Common.login_init_url, Common.headers)

        html = Req.zippedDecompress(init_res)
        dynamic_url_str = self.get_dynamic_js_url(html)

        set_cookies = init_res.info().getheader('Set-Cookie')
        set_cookies = self.cookie_str = set_cookies.replace('Path=/otn,', '').replace('path=/', '').replace(' ', '')
        return (set_cookies, dynamic_url_str)

    # 获取页面动态js
    @staticmethod
    def get_dynamic_js_url(self, html_str):
        # 查找到动态js <script>
        html_reg = r'</title>(.*?)</head>'
        script_list = re.findall(html_reg, html_str, re.S | re.M)
        script_reg = r'src="(.*?)"'
        dy_url = re.findall(script_reg, script_list[0], re.S | re.M)
        return Common.headers['Origin'] + dy_url[0]

    # 请求动态js
    @staticmethod
    def dynamic_js_init(self, dynamic_url):
        try:
            dynamic_res = Req.get(str(dynamic_url), Common.headers)
            return dynamic_res.info()
        except:
            wx.MessageBox(u'网络异常，请重试')

    # 获取新验证码
    @staticmethod
    def get_new_code_img(self):

        t = time.mktime(time.localtime())
        new_url = Common.LOGIN_PASSCODE_URL_0 + str(t)
        bmp = Common.codeFail.GetBitmap()

        try:
            res = Req.get(new_url, Common.headers)
            res_data = Req.zippedDecompress(res)

            if res_data:
                setCookie = res.info().getheader('Set-Cookie')
                Common.headers['Cookie'] = Common.headers['Cookie'] + setCookie[:setCookie.find(';')]

                stream = cStringIO.StringIO(res_data)
                bmp = wx.Bitmap(wx.Image(stream, wx.BITMAP_TYPE_JPEG))
                stream.flush()
                stream.close()
        except:
            print(u'获取验证码失败')

        return bmp

    # 空格键
    def space_click(self, event):
        if event.GetKeyCode() == wx.WXK_SPACE:
            self.login_click(None)

    # 登录
    def login_click(self, event):

        # 判断是否输入用户名和密码
        username_val = self.username.GetValue()
        password_val = self.password.GetValue()
        if not username_val:
            wx.MessageBox(u"请输入用户名")
            self.username.SetFocus()
            return
        if not password_val:
            wx.MessageBox(u"请输入密码")
            self.password.SetFocus()
            return

        if not self.pos:
            wx.MessageBox(u"请选择验证码")
            return

        # 让当前窗口焦点聚焦在验证码上
        self.codeBitMap.SetFocus()
        self.refresh_btn.Disable()
        self.login_btn.Disable()
        self.login_btn.SetLabel(u'准备校验验证码...')

        # 调用12306登录
        Common.startWorkFunc(self.to_12306_login, self.login_success, wargs=(username_val, password_val))

    def login_success(self, delayedResult, *args, **kwargs):
        try:
            rs = delayedResult.get()
        except Exception as e:
            print(u'登录 %s 异常:%s' % (delayedResult.getJobID, e))

        if rs and isinstance(rs, dict):
            # 隱藏当前登录窗口
            rs['login_frame'].Show(False)

            MainFrame(user=rs['user'], passenger_data=rs['passenger_data'],
                      login_frame=rs['login_frame'],
                      two_isOpenClick=rs['two_isOpenClick'], other_isOpenClick=rs['other_isOpenClick'])

    # 校验验证码
    def check_rand_code(self):
        randCode = ','.join(self.pos)
        # version 0.1
        # data = {'randCode': randCode, 'rand': 'sjrand'}
        data = {'answer': randCode, 'rand': 'sjrand', 'login_site': 'E'}
        rand_res = Req.post(Common.CHECK_RANDCODE_URL_0, data, Common.headers)
        rand_msg = Req.zippedDecompress(rand_res)
        print('校验返回：' + rand_msg)
        return rand_msg

    def to_12306_login(self, *args, **kwargs):

        # print(HEADERS)
        # 读取校验验证码返回内容
        try:
            self.login_btn.SetLabel(u'开始校验验证码...')
            time.sleep(1)
            randMsg = self.check_rand_code()
            print(randMsg)
            # 判断验证码是否通过
            if randMsg:
                json_randMsg = json.loads(randMsg)
                # 验证码通过
                if json_randMsg['data']['result'] == '1' and json_randMsg['data']['msg'] == 'TRUE':
                    self.login_btn.SetLabel(u'验证码通过...')
                    return self.login_12306(Common.asyn_login_url, args[0], args[1])
                else:
                    return self.validate_code_fail()
                    # wx.CallAfter(self.validate_code_fail)
        except Exception as e:
            wx.MessageBox(u'网络异常，请重试')
            self.refresh_btn.Enable()
            self.login_btn.Enable()
            self.login_btn.SetLabel(u'登录')
            self.login_btn.SetFocus()

    # 验证码验证不正确
    def validate_code_fail(self):

        self.refresh_click(None)
        # self.login_btn.SetLabel(u'登录')
        # self.login_btn.Enable()
        # self.refresh_btn.Enable()
        wx.MessageBox(u"验证码错误，请重新选择")
        return False

    def login_12306(self, url, username, password):
        # 开始登录
        self.login_btn.SetLabel(u'开始登录...')
        randCode = ','.join(self.pos)
        data = {'randCode': randCode, 'loginUserDTO.user_name': username, 'userDTO.password': password}

        login_res = Req.post(url, data, Common.headers)
        res_data_obj = Req.zippedDecompress(login_res)
        print(res_data_obj)

        if res_data_obj:
            res_rs = json.loads(res_data_obj)
            data, msg = res_rs.get('data'), res_rs.get('messages')
            #
            if data and data.get('loginCheck') == 'Y':
                self.login_btn.SetLabel(u'登录成功...')
                # 登录
                self.login_btn.SetLabel(u'正在初始化...')
                Req.post(Common.ulogin_url, {}, Common.headers)
                # 初始化my12306
                Req.get(Common.init_my12306_url, Common.headers)
                print(Common.headers)

                # 初始化leftTicket init
                Common.headers['Referer'] = Common.init_my12306_url
                print(Common.headers)
                left_res = Req.get(Common.left_ticket_url, Common.headers)
                if left_res:
                    left_res_html = Req.zippedDecompress(left_res)
                    html_reg = r'</title>(.*?)</head>'
                    all_list = re.findall(html_reg, left_res_html, re.S | re.M)

                    # 查找到动态js，找到，执行
                    if all_list:
                        script_reg = r'(?<=src=\").+?(?=\")|(?<=src=\').+?(?=\')'
                        script_list = re.findall(script_reg, all_list[0], re.S | re.M)
                        if script_list:
                            self.dynamic_js_init(Common.headers['Origin'] + script_list[-1])
                            # Req.get(HEADERS['Origin'] + script_list[-1], HEADERS)

                # self.Close(True)
                self.login_btn.SetLabel(u'正在获取联系人...')
                user = u.User(username, password)

                # 获取当前登录帐号的联系人
                passenger_data, two_isOpenClick, other_isOpenClick = Common.GetPassenger(Common.headers)
                self.login_btn.SetLabel(u'获取联系人成功...')

                return dict(user=user, passenger_data=passenger_data,
                            login_frame=self,
                            two_isOpenClick=two_isOpenClick, other_isOpenClick=other_isOpenClick)

                # 显示登录后主窗体
                # wx.CallAfter(MainFrame, user=user, headers=Common.headers, passenger_data=passenger_data,
                #              login_frame=self,
                #              two_isOpenClick=two_isOpenClick, other_isOpenClick=other_isOpenClick)
                # MainFrame(user, HEADERS, passenger_data, self)

            else:
                # wx.CallAfter(self.maintenance_time, msg[0])
                return self.maintenance_time(msg[0])

    # 非法购票时间（12306例行维护时间23:00~06:00）
    def maintenance_time(self, msg):
        self.refresh_click(None)
        self.login_btn.SetLabel(u'登录')
        self.login_btn.Enable()
        self.refresh_btn.Enable()
        wx.MessageBox(msg)
        return False

    # 验证码刷新事件
    def refresh_click(self, event):
        self.refresh_btn.Disable()
        self.refresh_btn.SetLabel(u'正在获取...')
        self.refreshImg.Hide()
        Common.startWorkFunc(self.refresh_click_req, self.refresh_click_res)

    def refresh_click_res(self, delayedResult, *args, **kwargs):
        try:
            rs = delayedResult.get()
        except Exception as e:
            print
            'Result for job %s raised exception:%s' % (delayedResult.getJobID, e)
            self.refreshImg.Show()
            self.refresh_btn.Enable()
            self.refresh_btn.SetLabel(u'刷新验证码')

        self.codeBitMap.SetBitmap(rs)
        # 清空
        self.clear_code_data()
        self.login_btn.SetLabel(u'登录')
        self.login_btn.Enable()
        self.refreshImg.Show()
        self.refresh_btn.Enable()
        self.refresh_btn.SetLabel(u'刷新验证码')

    def refresh_click_req(self, *args, **kwargs):
        cookie, dy_url = self.login_init()
        Common.headers['Cookie'] = cookie
        # 加载12306动态js
        self.dynamic_js_init(dy_url)

        # 获取验证码
        newCodeImg = self.get_new_code_img()
        return newCodeImg

    def on_close_window(self, event):
        # dlg = GMD.GenericMessageDialog(self, u'确定关闭？',
        #                          u"提示：",
        #                          wx.YES_NO | GMD.GMD_USE_GRADIENTBUTTONS | wx.ICON_QUESTION)
        # dlg = wx.MessageDialog(self, u'确定关闭？', u'提示', wx.YES_NO | wx.ICON_QUESTION)
        # result = dlg.ShowModal() == wx.ID_YES
        # if result:
        self.Destroy()

    @staticmethod
    def on_launch(self):
        wx.Locale(wx.LANGUAGE_CHINESE_SIMPLIFIED)
        Common.IsLocalSaleTimeExists()
        Common.IsLocalStationExists()

    # 移除验证码Mask
    def code_map_remove(self, event, pos):
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

    # 添加验证码Mask
    def on_draw_image(self, evt):

        self.login_btn.SetFocus()

        pos = evt.GetPosition()
        location = pos - (13, 13)
        pos = (pos - (0, 30))

        if pos.x - 5 < 0:
            return None

        if pos.y < 0:
            return None

        imageBitmap = wx.StaticBitmap(self.codeBitMap, wx.ID_ANY, Common.codeMark.GetBitmap(), location)
        imageBitmap.Bind(wx.EVT_LEFT_DOWN, lambda event, position=pos: self.code_map_remove(event, position))
        self.imageContainer.append(imageBitmap)

        # dc = wx.ClientDC(self.codeBitMap)
        #  # dc.SetPen(wx.Pen("RED"))
        #  # dc.SetBrush(wx.Brush("RED"))
        #  pos = evt.GetPosition()
        #  location = pos - (13,13)
        #
        #  pos = pos - (0,30)
        #
        #
        #  # dc.DrawCircle(pos.x, pos.y, 8)
        #
        #
        #  print(pos)
        #  codeMap = wx.Bitmap("code.png")
        #  #
        #  '''
        #  图1：5,73-41,109 图2：左上：41,78 左下：78,108 右上：145,41 右下：145,109
        #  '''
        #  #w = (68 - 28) / 4
        # # h = (68 - 28) / 4
        #
        #  #print(w, h)
        #  dc.BeginDrawing()
        #  dc.DrawBitmap(codeMap, location.x, location.y, True)
        #  # dc.DrawText(u"",pos.x, pos.y)
        #  dc.EndDrawing()
        #
        #  x1, y1, x2, y2 = dc.GetBoundingBox()
        #
        #  print(x1, y1, x2, y2)
        #
        #
        #
        #
        #
        #
        #
        # 验证码坐标添加至pos list中
        self.pos.append(str(pos.x))
        self.pos.append(str(pos.y))

    def clear_code_data(self):
        # 销毁验证码Marker
        for obj in self.imageContainer:
            obj.Destroy()
        # 清空Marker容器
        self.imageContainer = []
        # 清空坐标list
        self.pos = []


if __name__ == '__main__':
    app = wx.App()

    frame = LoginFrame()
    frame.on_launch()

    app.MainLoop()
