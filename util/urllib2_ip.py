# coding:utf-8
import Req,Common
import functools
import httplib
import urllib2


class BoundHTTPHandler(urllib2.HTTPHandler):
    def __init__(self, source_address=None, debuglevel=0):
        urllib2.HTTPHandler.__init__(self, debuglevel)
        self.http_class = functools.partial(httplib.HTTPConnection,
                                            source_address=source_address)

    def http_open(self, req):
        return self.do_open(self.http_class, req)


handler = BoundHTTPHandler(source_address=("115.156.188.182", 0))
opener = urllib2.build_opener(handler)
urllib2.install_opener(opener)

req = urllib2.Request('https://kyfw.12306.cn/otn/')
res = urllib2.urlopen(req,context = Req.context)
print(res.read())


# 获取12306CDN ip
def GetCdnIp():
    '''
    Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Encoding:gzip, deflate, sdch
Accept-Language:zh-CN,zh;q=0.8
Cache-Control:no-cache
Connection:keep-alive

    :return:
    '''
    default_header = {
        # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        # 'Accept-Encoding': 'gzip, deflate, sdch',
        # 'Accept-Language': 'zh-CN,zh;q=0.8',
        # 'Cache-Control': 'no-cache',
        # 'Connection': 'keep-alive',
        # 'Host': 'www.fishlee.net',
        # 'Cookie': '__jsluid=347bbac0d95c079e6c0716b5a9ad429d; __utma=199150904.97040191.1482552540.1482552540.1482552540.1; __utmb=199150904.1.10.1482552540; __utmc=199150904; __utmz=199150904.1482552540.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); Hm_lvt_d7809eb4e8f2d1969bc286ea54c0de4e=1482552541; Hm_lpvt_d7809eb4e8f2d1969bc286ea54c0de4e=1482552541; pgv_pvi=4315102208; pgv_si=s8356115456',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2900.1 Iron Safari/537.36'}

    print(default_header)
    # try:
    #     req = urllib2.Request('http://www.fishlee.net/apps/cn12306/ipservice/getlist')
    #     res = urllib2.urlopen(req)
    #     rs_zipped = Req.zippedDecompress(res)
    #     iplist = json.loads(rs_zipped)
    #     for ip in iplist:
    #         if ip.get('host') == 'kyfw.12306.cn':
    #             print(ip.get('host'))
    # except urllib2.URLError, e:
    #     print "Oops, timed out?"
    # except socket.timeout:
    #     print "Timed out!"




    # rs_data = Req.get('http://www.fishlee.net/apps/cn12306/ipservice/getlist', default_header)
    # print(rs_data)
    # rs_zipped = Req.zippedDecompress(rs_data)
    # print(rs_zipped)
    # if rs_zipped:
    #     json.loads(rs_zipped)
