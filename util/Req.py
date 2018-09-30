# -*- coding:utf-8 -*-
import urllib
import urllib2
import cStringIO
import ssl
import time
import json
import gzip, zlib
import functools
import httplib

context = ssl._create_unverified_context()


# 设置
class BoundHTTPHandler(urllib2.HTTPHandler):
    def __init__(self, source_address=None, debuglevel=0):
        urllib2.HTTPHandler.__init__(self, debuglevel)
        self.http_class = functools.partial(httplib.HTTPConnection,
                                            source_address=source_address)

    def http_open(self, req):
        return self.do_open(self.http_class, req)

# get请求


def get(url, headers):
    req = urllib2.Request(url, headers=headers)
    res = urllib2.urlopen(req, timeout=10, context=context)
    return res


# post 请求
def post(url, data, headers):
    req = urllib2.Request(url, urllib.urlencode(data), headers)
    res = urllib2.urlopen(req, timeout=10, context=context)
    return res


def quote(data):
    return urllib.quote(data)


def unquote(data):
    return urllib.unquote(data)


# 服务器设置gzipped，需要解压
def zippedDecompress(res):
    res_str = res.read()
    gzipped = res.headers.get('Content-Encoding')
    if gzipped:
        data = zlib.decompress(res_str, 16 + zlib.MAX_WBITS)
    else:
        data = res_str

    return data
