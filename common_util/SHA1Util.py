# encoding: utf8

'''
Created on 2014年5月16日

@author: Administrator
'''
import hashlib
import base64

#-----------

def digest(string):
    m = hashlib.sha1()
    m.update(string)
    return m.digest()
    
#-----------

def digestToHex(string):
    m = hashlib.sha1()
    m.update(string)
    return m.hexdigest()

#-----------

def digestToBase64(string):
    m = hashlib.sha1()
    m.update(string)
    return base64.b64encode(m.digest())

#-----------


#--------------








