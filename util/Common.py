# -*- coding:utf-8 -*-

import datetime
import json
import os
import pickle
import re
import time
import zlib
import wx, wx.adv
import Req
import random
import thread, threading
from wx.lib.embeddedimage import PyEmbeddedImage
from wx.lib.delayedresult import startWorker

# 车票预订图标
TRAIN_BOOK = PyEmbeddedImage(
    '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')

# 我的订单icon
MY_ORDER = PyEmbeddedImage(
    'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAABhElEQVRYR9WXgTEEQRBF30WACMgAESADInAiQASIABEgAyLgIkAGRIAIqF/Vo9rYvdmeu62t7aqrutrtnX79p3u2d8LANhk4PrUAu8AlsGUJPAGnwEs0oVqAN2AdeAVW7f8DsN83wLcLoOBSQAAf7voMkEKdLKqAB5AK28AG8LxsgCvg0LLT2nuA9tkDtGWYFJAKj+YkWK15nT/UpIAcjzPHBCCIkqkQT2wbEkB65gI49wvkANpTL2fyTQCl4P6+V8BfXwM+04UcQHRnDVGUUbTFlIzUzO0AuI8CRDIv+f7Zhq4KlBaN3B8fgNqqS/U3qaCTcTO7EVagpgNSzKaiDgOoYqMdkADUivmxHAaIFFgX3/EB3AE6y2tM8u+MvghVgL9nd1AGvar18za+GggmXXQPK1A1bBrG1AabhbZg8JOwqGnQYe4WaPDQvN+nzR1I1DJqu5WeCL6sLVtHMsVV4dz0BHAE3Pq1274LNM/pVaqjdFE13k1VzYf/5oroh8nShRkc4Ae1Jl4hC0COAQAAAABJRU5ErkJggg==')

# 我的联系人
MY_CONCACTS = PyEmbeddedImage(
    'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAABtklEQVRYR+2V7TEEQRCG34sAGRABIuAiIANEgAgQASJABi4CZCADZEAE1LM1UzVme6dnP6r2z82frbrt637m7bd7F5r5LGaurzVAHwUOkna9TdW6GoATSdeStpOi35IuJD2NBfEATiU9FIpcSrobA1EC4MYfFcl3JH1WxJkhJQAkvq1IPEqFEsCzpKMKAAx5mMSdB89sht/IA6SpUgngVVLq/C6WFAC/4Jv8YNp9C2JKAM8z92Fy/sFN0YKVpOOQvOQZWoBhqwFqTXgTes6uuHI807rwlGM4OQCX8SYhyk+st7S+sm3aiOVtQkaJ3m0Y0v6EhDic45mQtd2aEA+gdLMzSY8ZWGl0l5J4X23CGMiSeTEUsBKiwruhmDmCtS2g+J4BQCEgYgtiCB8ntmF6toy4ogfoPWs4/wznHPiDGMyYgtBrQKJ32IIAt07qAaSmKE/rxs6INwXoMTA8ycETCOCA4p3pga4d7hXteo85MWnuH0CAYrwb1VDAm9+hEHFKUGbXSALMEoDar15fkPiVtEwZc60A+O2buUc8+UsrumnBnADuKu5x2WGhNat4WObKf60BZlfgD8hTWO+lfgpwAAAAAElFTkSuQmCC')

# 验证码Mask Icon
CODE_MARK = PyEmbeddedImage(
    'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAACUUlEQVRYR8WXT07bUBDGv+HZZgm9AZyg6aIKSESEHQsi0ROUG7Q3iHMDOAFwApCSRXc1IhKkm6YnaG5QskxsM+gZO7Kd53/PruKVJfvN/Gbe92bmETb80Ib9oxJA9/f5rr/wj5m4BUY3AU9wiGkqtsWD8+n+pWxgpQAOnk73TDL7IFyUMsy4cdkdPB/+mBX9nwsQROz6fTC+FxlSfidcClMM8jKSCSCde0vvJ4FaWs7DRQyeGpZxkgWhBAgiX/p/AezWcR5b+yIssa+CWANoKvI0eFYm1gCOns8uiehbQ5EnzDDz1fhglNBTAiBQ+5YpU1/rYfAfaYBAH9OG3Fd3P346EgCdSe8GwNc63qVzwzKCGuEtPUcBcfvYHq6O8wogFN6/JpxHYsvKqLDEh+ifFUDnV+8CjGtdgCjyyHCBmL88tof379sUPkeTM5tAfR2Ais7B4MG4PbJTAD2HgOOqAFWdS/sMPIzbw0AnsQzkAswZPEsLSse5DsDcJ79rmdYsrmpd55UBeItPxp9HjlwYCit4l0etpODWdjVjC9QiTJdQCSEt6jp/z4BChJ1J7xzAnUqEWXW8Rt9YP4ZFhUiVCd12rSxEMvKiUhxBhGVWd1ZQl2JptEwzkhBho9EaVHKbkTS80XYcP2qqVlq1Ssb/T9eN6FveSCYn2p06TmNr58ISe6VGsmhRVHTqZiIr8twMJCAWnq07oskRzNg2bK2xPJ768HTI9ll2Wrp1X1279sUkvf9hseoyuAVQ8moGluPXVFjCafxq1pAQlWZK3Q3/J8AbmJSDMKmhGdsAAAAASUVORK5CYII=')

# 起始站切换图标
SWITCH_IMAGE = PyEmbeddedImage(
    'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAB6ElEQVRYR+2XzVHCUBSF73FAlwYaQGaErXQgdCAVKEth4dgBViAugKXpQDoQO8AtOCMV6HPJz3CcFwhDgISQBFho1sk73/05991ADvzgwPriC8B4/DQ0qLpPq6iBNwJocRyPXrUwh/FC1BCeALY4gBxFfkjmVSXbiTILrgD7ENeBuAIkG11TBNf6pQlZUpWsGWXk9llrARbFhTQnQDhx8setdCsAyfpHTcC7qKMlRVFYVZXs0+LZKwBGvZsD0IbIadQQ1nmUh69KpupZgkWIGXkhTPfrhj46GdXsnvoqZ+aBu7tAZ0LQAiRlQRxJUd1m2mGykmz0aDU1pGCf5QDQ9SeY4iBW0gPHsuLJqA3BRRRuSDR6urSX7gBrCFcgEEur23Q/SCYCAWihKcS4RdIMMw8CAwSJdt03fwdgamN5IaW4aN+9ZSBR7/Xn9hXOZ8jeANwGmVHv3kBwxWHsxt4rHHMg0eh2tOcngqIqn7fCNJ/faeocRLMrmMI+gVLYyecHwgEw83t/VxcRRd6+y5m8923Y/DwDx6YemWFKsPwthe8cxPPLO6X3TtjsOWi3AiIMkM+AGG7inivZVmJLL6/sk4PYmds2vXEtDwJiu8nPJr0TAMvvQM3PGr8TAPsG9fMTszMAv6X7B/gF5ydgMBmzonwAAAAASUVORK5CYII=')

# 获取验证码失败图片
CODE_FAIL = PyEmbeddedImage(
    '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')

# 验证码刷新图标
CODE_REFRESH_MARK = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABYAAAAWCAYAAADEtGw7AAAABHNCSVQICAgIfAhkiAAABG9J"
    "REFUOI2N03tM1XUYx/H373bO7xzgAAJGCOEN5CaCXEZpstlkZbY516i2bJUuHEvTudpaLWZt"
    "6VotyaVhzWbrolRbFy+ltnA6UQyVywTxriTXA5zOjfM7v0t/oISh4vPn9/s8r3337PMVuM+S"
    "ircfcwhCnm8ouJlE9zsc3qDfs/++1Kxamxqlb/xoU5nLriqPtv3lryDuCTfu/WfuNiLcXasS"
    "yUlOwNJsmKIqO6T6nd88ExeT5KL+SBe7vmrgQvO1FkSxkrOvHp0YLq2S6Ut4C8F60RGpxDlU"
    "WTJNC1WRHBVvLxPM6GgcdtBDBqeOXub4vkaz+2p3Haa4ko41l+8M526dTDh8OG32lIziRbNx"
    "PZCArChYgAiINic9AREskBVwOMHwh+hpaud0XUvoRo93u3Wmcs3tcGmVTN+klvR5uRnZi+fh"
    "CysMayCKN18gQBTgDoIogGWNnEt2iI+DYNs5/txVpw2fWGUHkEfh/rh3J01LzshevIBhXUSV"
    "YNgzgHfQCwJIokD89CRcThlMsKkg28DdOciRX0/T13ahG1lYf4v7DxbE50rKcslMFTFNqN/T"
    "RP1PxzRdN3sBUbbLiYVV5eL0xFjsCgz2B2g41EpTXbM/5PFto33d62O3OgpHudSkksIYZiTD"
    "pQsDnNzbYOq6sYTW1QfJqrUJkqczPVVJiI03+f3nNg78cEp3dw58j2pbS/u63v9nYBQOaqbx"
    "xQeHsNkky+fXhIBm9tK6+uBoo12Srp69zo597VZL/fUGnMpKOta2jkvVuFQU1pTi1SYT1g3s"
    "koLTfoXGihOj9wWfbRY1s9QM6ZvoWLP7buB4+F6VWZ0P0kZUuZ3Tq9aOnhdtTycYSiVs6gii"
    "jFMa4FRl48TwnI9j8LIlOT3+2UVPZcq1u1v8fr82lcaKfgDyt52LdqkzIyJslm5YwsBAIKCf"
    "fCUKxqZibKV+qaJ63rTbnetLl+ZELHs+H9OE775uNgmK5shqah5UQtpDK9Y/JuYVpXDj+hAf"
    "vvGLo/8mMR7OqX5ZFAPvzSrJSZr/5FxSpsXytw88Xf9ghLQI0I6TsyVMUEuZXTZHdSalcKkP"
    "Os4HGfQEPIyD82oeIWxscz2UlJu9sJCUzCkMmdDdPrIwp+Agb+lCUdetNMuycERHkjg9iaYr"
    "oDqhfm8rhqb/MQ62ycZv859+OCoiNw+PFzp7AGsENS2Y5FCISEvDGFkEpjnyvWMjLM7XnaGz"
    "paMf1fbaODgcFmsvHm9/Ya5TVtIyZmGpCgE/mAaYQKLTQlE0DNNCEMDULbx9blr2t9J87KIb"
    "m7KExoquW97tqciqzsKyPk+eOaWkZHGRmFOcgiiL+IfBHvTx4yd7CA5rmiiJ+IOG1d3r91lh"
    "/QA2VyVNLw2Npe4ct+zqMgxpa0bB1Bnly4vIL56Mt8fHiuXf+sMDwccxxH7sQJT9Go0VgTsa"
    "96xZ1auFnE/d5RuOWDsbuqzIBTt8FNTE38/oxD+voMaJP/R+TFzkKl/Y6NR90VmcLdcmGvsX"
    "ZajORhkOFtcAAAAASUVORK5CYII=")

# 删除图标
DEL_ICON = PyEmbeddedImage(
    'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABhUlEQVQ4T6WTTVLCQBCFXydOcCOytEqJuLHCSrgBNzA3EG+AJ0BPoJ5AbiDeAE8groJuiKBVLgNuhCloaxImf5QWVWY3M+9902+6Q/jnR3m/t4eKIUSbCS5ApeicA2J0l1JeVT/hpz0ZwMAWLYCu/yqKmc+rY9nRmhiwiVmb0pAQoMomyxrGNzMeQNwAaHcVYQKmHginOhLPZV3FiQBl0SGisyguPztjWXvdF7WliZ7aMhZoHH/I/qAs+iA6CXVLvnXeZSsC2JYiHeZLVBC1p8xeWTSJ6C6leayOZSMEDGyL8w+Xzpk3a60zmtMvAJ7ospU4iaPfJELEgGyExKxuVkLVtjyEmZMInm1dEtBeleYXpvP6945wdWYVZ/tLdmdF6wlAZdWJC2ckb8IIwxJKs6Lwk7aF07YSxq+T2uNJYSorRwGCeJBeyqbLZN7/NYX6zFhwXXVGrTOj7B1sNcigbqqSDI+BN3PBrjavAVJxmsxwQVQh5gAgH8Q9lTlf4drfuEmEtOYHERq/EZns+WYAAAAASUVORK5CYII=')

WIN_ICON = PyEmbeddedImage(
    'iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAMAAAD04JH5AAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAJlQTFRFAAAAx1xcx1xcx1xcx1xcx1xcx1xcx1xcx1xcx1xcx1xcx1xcx1xcx1xcx1xcT11zWmd8kZqoplBQqlJSrWJgslVVtFVVvIaAvVhYv1lZv3hhw3ljw5iRxVtbx1xcyqqhznBw0ryx1YBp3JmZ3NfJ4Jle4J1l4LSJ4NfD4ODR466u6evu6sLC67+A78GC8dbW9c+H/PX1////6bcnUgAAAA90Uk5TABAgMEBQYHCAj6+/z9/vBV3gigAAA+BJREFUeNrtm9ta6jAQRqEUG2gbIOWoGClycIMC8v4PtwEtIl8yOTe98L8uncUkmSaTmVpNQ0GIWnGM6VU4jlsoDGplKES3ln8Lxyh0ajyIYipUHAWurCdUUokDhmabKqndtGm9HqVUWWlUt2UeYaoljOo+zVtCaKbUSKnZXAhiaqzYYEUgakVI9+8n1JISLSc8YGpN+EHdfotaVUt18SXUshKlBdlIqXWlDQX7mDoQbvi1L0/wQJ1JajE0qEM1/PlfdhTc2hcT1FPqWCkcDxLqXIl6/J1t9p9HZX3uNzPVqMxcgLP9UVv7mdJiDFgT8PVopFfWRAwUJsD70VDv8tMA2f//PB8w90gBa/yPFsSaB6xBYO0/9zYA9qydKmP/7coBbBc0pULgpnjFttdRVbe3LX69kQmIzB14MQLbbkdD3S0wBvfzsM78BhXxr9fRUq+IicyvUl3iCFL4sKsH0Cl+Lz6usB1wBei4APjlgoiWD0CjG4DUB0AKxwD3ADexoO0HoA19BcoAuH4RIl8AkWgj6BogEYyAc4DvMYj8AUTcjUBJAF/bAuoPgF7y7z4BQjgX5x4AgVOgBIDzJMA+ATAUBcoAOEWC0C9ACOaDSwBAYEa0BIAWtAjKAIj9A2C/ALhG/QJQlwBdawCGRzNzAMPDqTnA6XiujvBzPLcAYKg/gD8AEAD7BcBSHyOHALF/AGhD8s+SwA0J8guAwE1pCQAhuC0vASAADybuATB8NHMPEMOHU/cACD6euwcI4QTF9Q1v6+Vq/SZv8e55OEEBTILr+1bLk1bSBPfPC1I0kRBgvbxoLQtw/7wgSRUIAVZfL1zKAtw/L0jT8ROVxQu+37eSBbh/XnSPzR2DhZ0hWIhStdwxyO1MwlyUrOam66c/y2q1VFuGt89PRel67oVF304c6gsvLHhXNiS3YT8nwisb3jTMrLign4kvrTjXdgMyMrc/IgPxtR3nkzgm5MXU/gshY/HFJc8FGTH1wYiQTMIBPBdMCCF9g5mY908vmEg4gFvBNCRnhGm+UDe+yKdn82QoWc/EiQUDYqiBMAZAJRyFD/Q1hDYC4iKWyzzI9M1nE9FXQKqMeTzQYsgGY2gvqlzJNt8dpLWba9WzBVCuYH5QEkTALeUCq0l3agA7vcpS4Kx+UBR0ItcqaLQGkGiWdNoaAkFJJ7+o9UkN4Ml2We0zefyQN//xSHTt8wqbn1XDEBugoV/arRgMM9UFKByFsRrAWNP/EIGCDzIz+/4bHPy3ePhvcqlAm4//Rif/rV4VaHbz3+5XgYZH/y2fFWh6rUDbbxUanyvQ+l2F5ncX7f//AWSUP+1z7/rnAAAAAElFTkSuQmCC')

HEADERS = {
    'Host': 'kyfw.12306.cn',
    'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586',
    'Accept': '*/*',
    'Accept-Language': 'zh-CN',
    'Accept-Encoding': 'gzip, deflate',
    'Origin': 'https://kyfw.12306.cn',
    'Referer': 'https://kyfw.12306.cn/otn/login/init',
    'Connection': 'keep-live',
    'Cache-Control': 'no-cache',
    'Content-Type': 'application/x-www-form-urlencoded'
}

# 身份证号正则
ID_NO_REG = [
    '^[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}$',
    '^[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}$',
    '^[1-9][0-9]{5}19[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}[0-9Xx]$',
    '^[1-9][0-9]{5}19[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}[0-9Xx]$']

# 主窗体Tab
TAB_LIST = [u'车票预订', u'我的订单', u'我的联系人']

# 所有坐席
SEAT_TYPES = [{'9': u'商务座'}, {'P': u'特等座'}, {'M': u'一等座'}, {'O': u'二等座'}, {'6': u'高级软卧'}, {'4': u'软卧'},
              {'3': u'硬卧'}, {'2': u'软座'}, {'1': u'硬座'}, {'WZ': u'无座'}]

OTN_URL = 'https://kyfw.12306.cn/otn/'

# 起售时间url
QSS_URL = 'https://kyfw.12306.cn/otn/resources/js/query/qss.js'

# 全国站名url
STATION_NAMES_URL = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js'

# 乘客列表url
PASSENGER_URL = 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'

# 登录初始化
LOGIN_INIT_URL = 'https://kyfw.12306.cn/otn/login/init'

# 获取登录验证码url v 0.1
LOGIN_PASSCODE_URL = 'https://kyfw.12306.cn/otn/passcodeNew/getPassCodeNew?module=login&rand=sjrand&'

# 获取登录验证码url v 0.2
LOGIN_PASSCODE_URL_0 = 'https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&'

# 校验验证码url（登录验证码） v 0.1
CHECK_RANDCODE_URL = 'https://kyfw.12306.cn/otn/passcodeNew/checkRandCodeAnsyn'

# 校验验证码url（登录验证码） v 0.2
CHECK_RANDCODE_URL_0 = 'https://kyfw.12306.cn/passport/captcha/captcha-check'

# 异步login登录url
ASYN_LOGIN_URL = 'https://kyfw.12306.cn/otn/login/loginAysnSuggest'

# 用户登录
ULOGIN_URL = 'https://kyfw.12306.cn/otn/login/userLogin'

# 初始化12306
INIT_MY12306_URL = 'https://kyfw.12306.cn/otn/index/initMy12306'
LEFT_TICKET_URL = 'https://kyfw.12306.cn/otn/leftTicket/init'

INIT_NOCOMPLETE_URL = 'https://kyfw.12306.cn/otn/queryOrder/initNoComplete'

# 检查用户状态
CHECK_USER_URL = 'https://kyfw.12306.cn/otn/login/checkUser'

# 查询车票价格Url
TICKET_PRICE_FL_URL = 'https://kyfw.12306.cn/otn/leftTicket/queryTicketPriceFL?train_no='
TICKET_PRICE_URL = 'https://kyfw.12306.cn/otn/leftTicket/queryTicketPrice?train_no='

# 查询车次停靠站明细
TRAIN_DETAIL_URL = 'https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no='

# 查询车票信息
QUERY_TICKET_LOG_URL = 'https://kyfw.12306.cn/otn/leftTicket/log?'
QUERY_TICKET_URL = ['leftTicket/query?', 'leftTicket/queryX?', 'leftTicket/queryA?']
# query_ticket_X_url = 'https://kyfw.12306.cn/otn'
# query_ticket_A_url = 'https://kyfw.12306.cn/otn/'

# 提交订单url
AUTO_SUBMIT_URL = 'https://kyfw.12306.cn/otn/confirmPassenger/autoSubmitOrderRequest'

# 获取队列url
QUEUE_URL = 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCountAsync'

# 订单验证码url
PASSENGER_CODE_URL = 'https://kyfw.12306.cn/otn/passcodeNew/getPassCodeNew?module=passenger&rand=randp&'

# 校验提交订单验证码url
PASSENGER_CODE_CHECK = 'https://kyfw.12306.cn/otn/passcodeNew/checkRandCodeAnsyn'

# 确认订单排队
CONFIRM_SINGLE_FOR_QUEUE_URL = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueueAsys'

# 等待订单生成
QUERY_ORDER_WAITTIME_URL = 'https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime'

# 订票成功，确认结果
ORDER_FOR_DCQUEUE_URL = 'https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue'

# 查询未完成订单（未付款）
QUERY_MYORDER_NOCOMPLETE_URL = 'https://kyfw.12306.cn/otn/queryOrder/queryMyOrderNoComplete'

# 查询已完成订单（已付款）
QUERY_MYORDER_COMPLETE_URL = 'https://kyfw.12306.cn/otn/queryOrder/queryMyOrder'

# 继续支付
CONTINUE_PAY_NOCAMPLETE_URL = 'https://kyfw.12306.cn/otn/queryOrder/continuePayNoCompleteMyOrder'

# 添加联系人
ADD_PASSENGER_URL = 'https://kyfw.12306.cn/otn/passengers/add'

# 删除联系人
DELETE_PASSENGER_URL = 'https://kyfw.12306.cn/otn/passengers/delete'

CDN12306_IPLIST_URL = 'http://www.fishlee.net/apps/cn12306/ipservice/getlist'


# 判断是否存在12306 cdn


def is_exist_cdn_ip():
    cdn_exists = os.path.exists('./cdn.data')
    if not cdn_exists:
        get_cdn_ip()
    else:
        # 获取cdn数据最后修改时间
        m_time = os.path.getmtime('./cdn.data')
        m_time5 = datetime.datetime.fromtimestamp(m_time) + datetime.timedelta(days=5)
        # 当前时间
        n_time = datetime.datetime.now()
        # 如果cdn数据修改超过5天（包括5天），远程更新
        if n_time >= m_time5:
            get_cdn_ip()


# 获取12306CDN ip

def get_cdn_ip():
    f = open('cdn.data', 'rb')
    cdns = pickle.load(f)
    print(cdns)
    f.close()

    # default_header = {}
    # rs_data = Req.get(CDN12306_IPLIST_URL,default_header)
    # rs_zipped = Req.zippedDecompress(rs_data)
    # if rs_zipped:
    #     iplist = json.loads(rs_zipped)
    #     sf = open('cdn.data', 'wb')
    #     pickle.dump(iplist, sf)
    #     sf.close()


# 获取登录账户下的联系人
def get_passenger(p_headers):
    passenger_rs = Req.get(PASSENGER_URL, p_headers)
    rs_data = Req.zippedDecompress(passenger_rs)

    if rs_data:

        # 响应内容
        rs_json = json.loads(rs_data)
        status = rs_json.get('status')
        data = rs_json.get('data')
        isExist = data.get('isExist')
        exMsg = data.get('exMsg')
        other_isOpenClick = data.get('other_isOpenClick')
        two_isOpenClick = data.get('two_isOpenClick')
        passenger_data = data.get('normal_passengers')

        if status and isExist and passenger_data:
            return passenger_data, two_isOpenClick, other_isOpenClick
        else:
            return exMsg, [], []


def is_local_station_exists():
    station_exists = os.path.exists('./station.data')
    if not station_exists:
        get_station_from12306()
    else:
        # 获取车站数据最后修改时间
        m_time = os.path.getmtime('./station.data')
        m_time5 = datetime.datetime.fromtimestamp(m_time) + datetime.timedelta(days=5)
        # 当前时间
        n_time = datetime.datetime.now()
        # 如果车站数据修改超过5天（包括5天），从12306更新
        if n_time >= m_time5:
            get_station_from12306()


def get_station_from12306():
    print('----初始化站名数据开始----')
    station_res = Req.get(STATION_NAMES_URL, HEADERS)
    # station_req = urllib2.Request(url=_station_names)
    # station_res = urllib2.urlopen(station_req, context=context)
    # station_raw = station_res.read()
    # gzipped = station_res.headers.get('Content-Encoding')
    # if gzipped:
    #     station_data = zlib.decompress(station_raw, 16 + zlib.MAX_WBITS)
    # else:
    #     station_data = station_raw

    station_data = Req.zippedDecompress(station_res)
    if station_data:
        reg = r'=(.*?);'
        # station_data_format = station_data.replace('\n', '').replace('\t', '').replace('\r', '').replace(' ',
        #                                                                                                  '').replace(
        #     'var', '').replace('station_names=', '').replace(';', '')
        station_data_format = re.findall(reg, station_data)
        print(station_data_format[0])
        sf = open('station.data', 'wb')
        pickle.dump(station_data_format[0], sf)
        sf.close()
    print('----初始化站名数据结束----')


def get_station_from_local():
    f = open('./station.data', 'rb')
    stations = pickle.load(f)
    p = re.compile(r'@[a-z]+\|([^\|]+)\|([A-Z]+)\|([a-z]+)\|([a-z]+)\|(\d+)')
    list_stations = eval(stations)
    rs = p.findall(list_stations)
    sort_stations = sorted(rs, key=lambda index: int(index[4]))
    f.close()
    return sort_stations


def is_local_sale_time_exists():
    qss_exists = os.path.exists('./qss.data')
    if not qss_exists:
        get_city_sale_time_from12306()
        pass
    else:
        # 获取车站起售时间最后修改时间
        m_time = os.path.getmtime('./qss.data')
        m_time5 = datetime.datetime.fromtimestamp(m_time) + datetime.timedelta(days=5)
        # 当前时间
        n_time = datetime.datetime.now()
        # 如果车站起售时间修改超过5天（包括5天），从12306更新
        if n_time >= m_time5:
            get_city_sale_time_from12306()


def get_city_sale_time_from12306():
    print('----初始化起售时间数据开始----')
    qss_res = Req.get(QSS_URL, HEADERS)
    # qss_req = urllib2.Request(url=_qss)
    # qss_res = urllib2.urlopen(qss_req, context=context)
    qss_data = Req.zippedDecompress(qss_res)

    # qss_raw = qss_res.read()
    # gzipped = qss_res.headers.get('Content-Encoding')
    # if gzipped:
    #     qss_data = zlib.decompress(qss_raw, 16 + zlib.MAX_WBITS)
    # else:
    #     qss_data = qss_raw

    if qss_data:
        reg = r'({)(.*?)(})'
        qss_data_format = re.findall(reg, qss_data, re.S | re.M)
        # qss_data_format = str(qss_data).replace('\n', '').replace('\t', '').replace('\r', '').replace(' ', '').replace(
        #     'var', '').replace('citys=', '')
        print(qss_data_format[0])
        if qss_data_format:
            qss_data_str = ''.join(tmp_data for tmp_data in qss_data_format[0])
            f = open('qss.data', 'wb')
            pickle.dump(eval(qss_data_str), f)
            f.close()
    print('----初始化起售时间数据结束----')


def get_city_sale_time():
    f = open('./qss.data', 'rb')
    cities = pickle.load(f)
    saleTimes = {}
    for k, v in cities.items():
        saleTimes[k.decode('utf-8')] = v
    # choices = list()
    # for q in cities:
    #     print(cities[q])
    #     choices.append(q.decode('utf-8'))
    f.close()
    return saleTimes


# 所有坐席
def get_seat_type():
    seatTypes = []
    for st in SEAT_TYPES:
        for k, v in st.items():
            seatTypes.append(v)
    return seatTypes


# 设置字典值字符集
def encoded_dict(in_dict):
    out_dict = {}
    for k, v in in_dict.iteritems():
        if isinstance(v, unicode):
            v = v.encode('utf8')
        elif isinstance(v, str):
            # Must be encoded in UTF-8
            v.decode('utf8')
        out_dict[k] = v
    return out_dict


# 类似ajax异步执行操作
def start_work_func(req, res, cargs=(), ckwargs={},
                    wargs=(), wkwargs={},
                    jobID=None, group=None, daemon=False,
                    sendReturn=True, senderArg=None):
    startWorker(res, req,
                cargs, ckwargs,
                wargs, wkwargs,
                jobID, group, daemon,
                sendReturn, senderArg)


# 日期验证
class DateValidator(wx.PyValidator):
    def __init__(self):
        wx.PyValidator.__init__(self)
        self.Bind(wx.EVT_DATE_CHANGED, self.OnDateChanged)

    def Clone(self):
        return DateValidator()

    def Validate(self, win):
        return True

    def TransferToWindow(self):
        return True  # Prevent wxDialog from complaining.

    def TransferFromWindow(self):
        return True  # Prevent wxDialog from complaining.

    def OnDateChanged(self, event):
        datePicker = self.GetWindow()
        textVal = datePicker.GetValue()
        now = wx.DateTime().Now()
        now_format = now.Format('%Y-%m-%d')
        txt_format = textVal.Format('%Y-%m-%d')
        if txt_format < now_format:
            # wx.MessageBox(u'行程日期不能小于今天')
            datePicker.SetValue(now)
            return
        event.Skip()


# 查票綫程
class TicketThread:
    def __init__(self, __do):
        self.__do = __do

    def Start(self):
        self.keepGoing = self.running = True
        thread.start_new_thread(self.Run, ())

    def Stop(self):
        self.keepGoing = False

    def IsRunning(self):
        return self.running

    def Run(self):
        while True:
            if not self.keepGoing:
                break
            self.__do()
            time.sleep(random.randint(1, 2))

        self.running = False


def opj(path):
    """Convert paths to the platform-specific separator"""
    st = apply(os.path.join, tuple(path.split('/')))
    # HACK: on Linux, a leading / gets lost...
    if path.startswith('/'):
        st = '/' + st
    return st


def test():
    url = 'http://q.10jqka.com.cn/index/index/board/all/field/zdf/order/desc/page/1/ajax/1/'
    rs_data = Req.get(url, HEADERS)
    gzipped = rs_data.headers.get('Content-Encoding')

    rs_info = rs_data.read()
    if gzipped:
        res_data_obj = zlib.decompress(rs_info, 16 + zlib.MAX_WBITS)
    else:
        res_data_obj = rs_info

    res_data_obj = ''.join(res_data_obj.split())
    data = unicode(res_data_obj, 'GBK').encode('UTF-8')
    # res_data_obj = res_data_obj.replace('\n','').replace('\t','').replace('\r','').replace(' ','')
    # htmlTr = '<tbody><tr><td></td><td></td><td></td><td class="c-rise"></td><td class="c-rise"></td><td class="c-rise"></td><td class=""></td><td></td><td class=""></td><td class="c-rise"></td><td></td><td></td><td></td><td></td></tr></tbody>'

    ss = re.compile(r'<tbody>(.*?)</tbody>')
    rs = ss.findall(data)
    for s in rs:
        print(s)


# 定时器
mutex = threading.Lock()


class Timer(threading.Thread):
    def __init__(self, fn, args=(), sleep=0, lastDo=True):
        threading.Thread.__init__(self)
        self.fn = fn
        self.args = args
        self.sleep = sleep
        self.lastDo = lastDo
        self.setDaemon(True)

        self.isPlay = True
        self.fnPlay = False

    def __do(self):
        self.fnPlay = True
        apply(self.fn, self.args)
        self.fnPlay = False

    def run(self):
        while self.isPlay:
            if mutex.acquire(1):
                self.__do()
                mutex.release()
                time.sleep(self.sleep)

    def stop(self):
        # stop the loop
        self.isPlay = False
        while True:
            if not self.fnPlay: break
            time.sleep(0.01)
            # if lastDo,do it again
        if self.lastDo: self.__do()


# 最小化系统到托盘部分
class TaskBarIcon(wx.adv.TaskBarIcon):

    def __init__(self, frame):

        wx.adv.TaskBarIcon.__init__(self)

        self.ID_Abuout = wx.NewId()
        self.ID_MainFrame = wx.NewId()
        self.ID_Exit = wx.NewId()

        self.SetMainFrame(frame)
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarLeftDClick)
        self.Bind(wx.EVT_MENU, self.OnMainFrame, id=self.ID_MainFrame)
        self.Bind(wx.EVT_MENU, self.OnShowAbout, id=self.ID_Abuout)
        self.Bind(wx.EVT_MENU, self.OnExit, id=self.ID_Exit)

    def SetMainFrame(self, frame):

        self.frame = frame
        self.SetIcon(WIN_ICON.Icon, u"TT Go")

    def OnClose(self, event):

        self.taskBarIcon.Destroy()
        self.Destroy()

    def OnTaskBarLeftDClick(self, event):

        if self.frame.IsIconized():
            self.frame.Iconize(False)
        if not self.frame.IsShown():
            self.frame.Show(True)

        self.frame.Raise()

    def OnShowAbout(self, event):

        info = wx.AboutDialogInfo()
        info.Name = "TT Go"
        info.Version = "0.0.1"
        info.Copyright = "(C) 2016 Programmers and Coders Everywhere"
        info.Description = u'基于python2.7+wxpython3.0.2开发的订票程序，向开源致敬，拥抱开源'
        info.Developers = ["BenLee"]
        info.License = 'GPL'

        # Then we call wx.AboutBox giving it that info object
        wx.AboutBox(info)

    def OnMainFrame(self, event):

        # 显示主面板
        if not self.frame.IsShown():
            self.frame.Show(True)
        self.frame.Raise()

    # -------------------------------------
    def OnExit(self, event):

        # 关闭程序
        wx.Exit()

    def CreatePopupMenu(self):

        # 添加最小化菜单
        self.menu = wx.Menu()
        self.menu.Append(self.ID_MainFrame, u"主界面")
        self.menu.Append(self.ID_Abuout, u"关于")
        self.menu.AppendSeparator()
        self.menu.Append(self.ID_Exit, u"退出")

        return self.menu


if __name__ == '__main__':

    print(time.gmtime())
    print(time.tzname)
    stra = 'H1#21141337CD9C1DE1050F0864DF024BB103FA063A3E9D03159727A099#O055300444M0933000929174800016#1'
    print(stra.split('#'))
    for s in time.tzname:
        print(s.decode('gbk'))
    q = None
    r = '5'
    if q or r:
        print(q)
    print(random.randint(2, 5))
    print(time.asctime(time.localtime()))
    print(HEADERS)

    s = {}

    f = open('../cdn.data', 'rb')
    cdns = pickle.load(f)
    # print(cdns)
    print(len(cdns))
    i = 0
    for item in cdns:
        if item['host'] == 'kyfw.12306.cn':
            i += 1
            print(item['ip'])
    print(i)
    # test()
