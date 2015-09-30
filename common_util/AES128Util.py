# encoding: utf8




import os
from Crypto.Cipher import AES


_bs = AES.block_size
_pad   = lambda s : s + (_bs - len(s) % _bs) * chr( _bs - len(s) % _bs )
_unpad = lambda s : s[0:-ord(s[-1])]


def generateKey():
    return os.urandom(16)
    
    
def encrypt(key, content):
    cipher = AES.new(key)
    return cipher.encrypt(_pad(content))
    
    
def decrypt(key, content):
    cipher = AES.new(key)
    return _unpad(cipher.decrypt(content));
    

    
    
    
    
    
    
    
    