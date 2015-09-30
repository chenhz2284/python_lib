# encoding: utf8

'''
Created on 2014年5月16日

@author: Administrator
'''
import hashlib
import base64

#-----------

def digest(string):
    md5 = hashlib.md5()
    md5.update(string)
    return md5.digest()
    
#-----------

def digestToHex(string):
    md5 = hashlib.md5()
    md5.update(string)
    return md5.hexdigest()

#-----------

def digestToBase64(string):
    m = hashlib.md5()
    m.update(string)
    return base64.b64encode(m.digest())

#-----------












