#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2016.08.03
    @author: jhbae
'''
import os
import re
import base64
import hashlib

class Decode():
    def _en(self, _in):
        if not isinstance(_in,bytes):
            _in =  bytes(_in, 'utf-8')
        return base64.b64encode(_in) 

    def _de(self, _in):
        return base64.b64decode(_in)

    def fenc(self, s_str):
        s_encode_tmp = self._en(s_str)
        s_encode = self._en(s_encode_tmp)

        s_encode_hash = hashlib.md5(s_encode_tmp).hexdigest()
        if isinstance(s_encode,bytes):
            s_encode = s_encode.decode('utf-8')
        s_encode = s_encode.replace('=', '@')
        s_encode_val = s_encode + '@' + s_encode_hash
        s_encode_val = bytes(s_encode_val,'utf-8')
        return s_encode_val

    def fdec(self, s_str):
        i_split_check = s_str.rfind('@')

        if i_split_check == -1:
            pass
        s_decode_tmp = s_str[:i_split_check]
        s_decode_tmp = s_decode_tmp.replace('@','=')
        s_decode_str = self._de(s_decode_tmp)
        s_decode_value = self._de(s_decode_str)
        return s_decode_value

    def dec_bit(self, s_file_name):
        with open(s_file_name) as o_f:
            s_contents = o_f.read()

        if re.search('###\*\*\*', s_contents):
            return True
        else:
            return False

    def file_dec(self, s_file_name):
        if self.dec_bit(s_file_name):
            return None
        with open(s_file_name) as o_f:
            s_str = o_f.read()

        with open(s_file_name,'w') as o_f:
            o_f.write(self.fdec(s_str))

        return self.dec_bit(s_file_name)

    def file_Dec_re_text(self, s_file_name):
        if self.dec_bit(s_file_name):
            with open(s_file_name) as o_f:
                s_re_txt = o_f.read()
        else:
            with open(s_file_name) as o_f:
                s_str = o_f.read()
            s_re_txt = self.fdec(s_str)

        return s_re_txt

    def fileEncDec(self, s_file_name):
        if self.dec_bit(s_file_name) == False:
            return None

        with open(s_file_name) as o_f:
            s_str = o_f.read()

        with open(s_file_name,'w') as o_f:
            o_f.write(self.fenc(s_str))

        return self.dec_bit(s_file_name)

    """
    def secCfg(self):
        secFile = os.path.join('config','sec.cfg')
        if os.path.isfile(secFile) == False:
            with open(secFile ,'w') as o_f:
                o_f.write(self.fenc('kes2719!'))

        with open(secFile) as o_f:
            tmp=o_f.read()
        return self.fdec(tmp)
    """