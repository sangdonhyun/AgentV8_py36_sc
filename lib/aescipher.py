#!/usr/bin/env python
#-*- coding: utf-8 -*-

import base64
import pyDes

def iv():
    return chr(0) * 8

class AESCipher(object):
    def __init__(self, key):
        self.key = key
        self.iv = iv()

    def encrypt(self, message):
        k = pyDes.des(self.key, pyDes.ECB, self.iv, pad=None, padmode=pyDes.PAD_PKCS5)
        d = k.encrypt(message)
        return base64.b64encode(d)

    def decrypt(self, enc):
        k = pyDes.des(self.key, pyDes.ECB, self.iv, pad=None, padmode=pyDes.PAD_PKCS5)
        
        if not isinstance(enc,bytes):
            enc = enc.encode()
        # data = base64.b64decode(enc + b'=' * (-len(enc) % 4))
        data = base64.b64decode(enc)
        # data = base64.urlsafe_b64decode(enc)
        d = k.decrypt(data)
        return d