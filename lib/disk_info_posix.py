#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2016.08.08
    @author: jhbae
'''

import os
import sys
import platform
from . import common
import base64
import subprocess
import configparser

env = os.environ
if platform.uname()[0] == 'AIX':
    env['LANG'] = 'en_US'
else:
    env['LANG'] = 'C'

class DiskInfoPosix():
    def __init__(self, s_arg):
        if os.name != 'posix':
            print('Posix Platform Only.')
            sys.exit(1)

        self.a_bad_cmd = ['shutdown', 'halt', 'reboot', 'chmod' , 'chown', 'rm -', 'rmdir' , 'finger', 'snoop', 'ping']
        self.o_common = common.Common()
        self.s_arg = s_arg
        self.a_save_type = {}
        self.s_aescipher = self.o_common.s_aes_cipher
        self.s_dr_type_check = ''

        if os.name == 'posix':
            self.s_conf_file = "vendor/%s_v8.cfg" % (platform.system())
        else:
            self.s_conf_file = "vendor/%s_v8.cfg" % ('Linux')

        self.a_cnt_dict = self.get_count_list()

    def vaild_check_char(self, s_file_name):

        with open(s_file_name) as o_f:
            s_str = o_f.read()
        if s_str.find('###***') > -1:
            return True
        else:
            return False

    def get_cfg(self, s_cfg_key):
        return self.o_common.cfg_parse_read(self.s_conf_file, s_cfg_key)

    def get_count_list(self):
        a_vendor_list = {}
        i_value = 0

        a_disk_cfg_list = self.get_cfg('Disk Flag')
        #print('a_disk_cfg_list :',a_disk_cfg_list)
        for s_ven_key in a_disk_cfg_list:
            s_ven_val = a_disk_cfg_list[s_ven_key]
            s_disk_cmd = self.o_common.s_aes_cipher.decrypt(s_ven_val)

            #print('s_disk_cmd :',s_disk_cmd)
            try:
                i_value = int(subprocess.getoutput(s_disk_cmd.strip()))
                #print('i_value :',i_value)
            except:
                i_value = 0
            a_vendor_list[s_ven_key] = i_value




        # for s_ven_key, s_disk_cmd_enc in a_disk_cfg_list:
        #     s_disk_cmd = self.o_common.s_aes_cipher.decrypt(s_disk_cmd_enc)
        #     try:
        #         i_value = int(subprocess.getoutput(s_disk_cmd.strip()))
        #     except:
        #         i_value = 0
        #     a_vendor_list[s_ven_key] = i_value
        return a_vendor_list

    def disk_flag(self):
        s_msg = ''
        for s_vendor in list(self.a_cnt_dict.keys()):
            s_msg += '%s : %s\n' % (s_vendor, self.a_cnt_dict[s_vendor])
        print('s_msg :',s_msg)
        self.o_common.screenshot(self.o_common.get_cmd_title_msg('Disk Flag'), a_save_type=self.a_save_type)
        self.o_common.screenshot(s_msg, a_save_type=self.a_save_type)

    def tot_except_emc_value(self):
        a_tmp_dict = self.a_cnt_dict
        if 'EMC' in a_tmp_dict:
            del a_tmp_dict['EMC']

        return sum(a_tmp_dict.values())

    def check_cmd(self, s_cmd):
        b_bit = True
        for s_bad_cmd in self.a_bad_cmd:
            if s_bad_cmd in s_cmd:
                b_bit = False
                break
        return b_bit

    def get_common(self, s_cmd_title):
        #print('s_cmd_title :',s_cmd_title)
        a_get_common = self.get_cfg(s_cmd_title)
        #print('a_get_common :',a_get_common)
        #print('a_get_common :', type(a_get_common))
        #print(isinstance(dict(a_get_common), (dict, tuple, list)))
        #print(dict(a_get_common))
        if not isinstance(a_get_common,dict):
            a_get_common = dict(a_get_common)

        if isinstance(a_get_common, (dict, tuple, list)):
            ##print('-' * 40)
            for sec in sorted(set(a_get_common.keys())):
                a_common_tmp = a_get_common[sec]

                ##print('a_common_tmp[1] :', type(a_common_tmp))
                s_common_dec = self.o_common.s_aes_cipher.decrypt(a_common_tmp)
                # s_common_dec = self.s_aescipher.decrypt(a_common_tmp[1])
                if isinstance( s_common_dec,bytes):
                    s_common_dec = s_common_dec.decode('utf-8')
                s_title, s_cmd = s_common_dec.split('^')
                if self.check_cmd(s_cmd):
                    self.o_common.screenshot(self.o_common.get_cmd_title_msg(s_title), a_save_type=self.a_save_type)
                    s_cmd_return = self.o_common.get_execute(s_cmd).strip()
                    self.o_common.screenshot(s_cmd_return, a_save_type=self.a_save_type)
            del a_get_common

    def vendor_cmd(self):
        if self.s_dr_type_check.lower() in ('vt', 'vd'):
            self.a_cnt_dict['VT'] = 1

        for s_vendor in self.a_cnt_dict:
            if self.a_cnt_dict[s_vendor] > 0:
                a_vendor_cmd = self.o_common.cfg_parse_read(self.s_conf_file, s_vendor)


                # if isinstance(a_vendor_cmd, (dict, tuple, list)):
                for a_vendor_tmp in a_vendor_cmd:
                    #print('a_vendor_tmp :',a_vendor_tmp)
                    #print('ven :',a_vendor_cmd[a_vendor_tmp])
                    v_cmd = a_vendor_cmd[a_vendor_tmp]
                    #print('v_cmd :',v_cmd)
                    s_vendor_dec = self.s_aescipher.decrypt(v_cmd)
                    if isinstance(s_vendor_dec,bytes):
                        st=s_vendor_dec.decode('utf-8')
                        if '^' in st:
                            s_title, s_cmd = st.split('^')
                    #print('s_title',s_title)
                    #print('s_cmd',s_cmd)
                    #print(self.check_cmd(s_cmd))
                    if self.check_cmd(s_cmd):
                        s_title = s_title
                        self.o_common.screenshot(self.o_common.get_cmd_title_msg(s_title), a_save_type=self.a_save_type)
                        #print('title :',self.o_common.get_cmd_title_msg(s_title))
                        s_cmd_return = self.o_common.get_execute(s_cmd).strip()
                        #print('s_cmd_return :',s_cmd_return)

                        self.o_common.screenshot(s_cmd_return, a_save_type=self.a_save_type)

    def dev_type(self):
        s_dev_type = self.o_common.cfg_parse_read('fleta.cfg', 'systeminfo', 'set_device')

        if s_dev_type:
            return s_dev_type.lower()
        else :
            return 'fs'

    def main(self):
        s_dev_type = self.dev_type()
        self.s_dr_type_check = s_dev_type

        self.a_save_type = {
                       'file_name' : s_dev_type + '_' + self.o_common.s_host_name + '.tmp'
                      , 'check_type' : 'diskinfo'
                      , 'execute_type' : self.s_arg
                   }
        print(self.o_common.get_agent_head_msg())
        self.o_common.screenshot(self.o_common.get_agent_head_msg(), a_save_type=self.a_save_type, b_start=True)
        self.o_common.screenshot(self.o_common.get_agent_default_msg(), a_save_type=self.a_save_type)

        self.disk_flag()
        print('COMMON1 START ..')
        self.get_common('COMMON1')
        self.vendor_cmd()

        # if only SunOS and not EMC disk
        s_os_type = platform.uname()[0]
        if s_os_type == 'SunOS':
            if self.tot_except_emc_value() > 0:
                self.get_common('COMMONS')

        self.get_common('COMMON2')
        self.get_common('COMMON3')
        self.o_common.screenshot(self.o_common.get_agent_tail_msg(), a_save_type=self.a_save_type)

        return True
