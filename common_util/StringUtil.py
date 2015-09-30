# encoding: utf8

'''
Created on 2014年5月16日

@author: Administrator
'''


import StringIO
import random
import base64
import uuid
import urllib
import binascii


#-------------------------

def toHex(s):
    return binascii.b2a_hex(s)

def strToUnicode(s, encoding):
    if s==None:
        return None
    if encoding==None:
        return s.decode()
    return s.decode(encoding)

def unicodeToStr(u, encoding):
    if u==None:
        return None
    if encoding==None:
        return u.encode()
    return u.encode(encoding)

#-------------------------

def trim(string, default=""):
    if string==None:
        return default;
    else:
        return string.strip();

def splitTrim(s, sep=","):
    if s is None:
        return []
    _arr = s.split(sep)
    _result = [];
    for _s in _arr:
        if _s.strip()=="":
            continue
        _result.append(_s)
    return _result

def join(arr, seperator):
    return seperator.join([str(x) for x in arr])

#---------------------

def equalsIgnoreCase(s1, s2):
    if s1!=None:
        s1 = s1.lower()
    if s2!=None:
        s2 = s2.lower()
    return s1==s1

#----------------------

def isBlank(string):
    if trim(string)=="":
        return True
    else:
        return False

#-----------------------

def uuid4():
    return str(uuid.uuid4()).replace("-", "")

#------------------

def urlencode(str1):
    return urllib.quote_plus(str1)

def urldecode(str1):
    return urllib.unquote_plus(str1)

#-----------------

"""
将一个字典转化为：a=1&b=2&c=3
"""
def urlencodeDict(dictData):
    return urllib.urlencode(dictData)

"""
将'a=1&b=2&c=3'转化为字典
"""
def urldecodeToDict(dictStr):
    rt = {};
    arr = dictStr.split("&")
    for item in arr:
        arr2 = item.split("=")
        rt[arr2[0]] = urllib.unquote_plus(arr2[1])
    return rt;

#--------------------

"""
用于生成指定长度的随机字符串
"""
def randomString(length=32):
    arr = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", 
           "a", "b", "c", "d", "e", "f", "g", 
           "h", "i", "j", "k", "l", "m", "n", 
           "o", "p", "q", "r", "s", "t", 
           "u", "v", "w", "x", "y", "z", 
           "A", "B", "C", "D", "E", "F", "G", 
           "H", "I", "J", "K", "L", "M", "N", 
           "O", "P", "Q", "R", "S", "T", 
           "U", "V", "W", "X", "Y", "Z"];
    sio = StringIO.StringIO()
    for i in xrange(length):
        sio.write(arr[random.randint(0, len(arr)-1)])
    return sio.getvalue()
    
#-----------------


def bytesToBase64(b):
    return base64.encodestring(b)


def base64ToBytes(string):
    return base64.decodestring(string)


#------------------









