#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2017.04.14
    @author: jhbae
'''

import re
import sys
import urllib.request, urllib.parse, urllib.error
from . import common
import os

class EmcClone():
    def __init__(self):
        self.o_common = common.Common()
        self.a_emc_cmd_list = self.get_emc_cmd()
        self.b_end_flag = False

        # sym cmd path add
        self.sym_cmd_path()

    def url_check(self):

        s_cfg_url = self.o_common.cfg_parse_read('emcClone.cfg', 'CHECKURL', 'url')
        s_srm_ip = self.o_common.cfg_parse_read('fleta.cfg', 'srm', 'srm_ip')
        s_srm_port = self.o_common.cfg_parse_read('fleta.cfg', 'srm', 'srm_port')
        s_ip = self.o_common.cfg_parse_read('fleta.cfg', 'COMMON', 'agent_ip')

        s_param = '?serverIp=%s&serverNm=%s' % (s_ip, self.o_common.s_host_name)

        if s_cfg_url == '':
            return False

        try :
            s_cfg_url = re.sub('^\/{1,2}', '', s_cfg_url)

            s_url = 'http://%s:%s/%s' % (s_srm_ip, s_srm_port, s_cfg_url) + s_param
            o_url_res = urllib.request.urlopen(s_url)
            if o_url_res.code == 200:
                s_read_val = o_url_res.read().strip().upper()
                if s_read_val == 'T':
                    return True
                else:
                    return False
            else:
                return False
        except:
            return False

    def sym_cmd_path(self):
        s_sym_cmd_dir = self.o_common.cfg_parse_read('emcClone.cfg', 'PATH', 'path')

        if sys.platform == "win32":
            os.environ['PATH'] = ';'.join([s_sym_cmd_dir, os.getenv('PATH')])
        else:
            os.environ['PATH'] = ':'.join([s_sym_cmd_dir, os.getenv('PATH')])

    def get_cmd_parse(self, s_cmd_tmp):
        s_title = ''
        s_cmd = ''

        if s_cmd_tmp != '':
            try:
                s_title, s_cmd = s_cmd_tmp.split('^')
            except:
                s_title = s_cmd_tmp
                s_cmd = s_cmd_tmp
        return s_title, s_cmd

    def get_emc_cmd(self):
        a_sym_cmd_list_cfg = self.o_common.cfg_parse_read('vendor/emcClone.cfg', 'cmd')
        a_sym_cmd = {}
        if isinstance(a_sym_cmd_list_cfg, (dict, tuple, list)):

            for a_sym_tmp in a_sym_cmd_list_cfg:
                try:
                    s_sym_cmd = self.o_common.s_aes_cipher.decrypt(a_sym_tmp[1])
                except:
                    s_sym_cmd = a_sym_tmp[1]
                a_sym_cmd[a_sym_tmp[0]] = s_sym_cmd
        return a_sym_cmd

    def get_sid(self):
        if sys.platform == "win32":
            s_cmd = 'symcfg list | grep Local | awk "{print $1}"'
        else:
            s_cmd = "symcfg list | grep Local | awk '{print $1}'"

        # LIST 받아오기
        s_sid_list = self.o_common.get_execute(s_cmd)

        if s_sid_list:
            if re.match(r'^[0-9]{3,}', s_sid_list):
                a_sid_list = s_sid_list.splitlines()
                return a_sid_list

        return False

    def emc_checker(self, s_sid):
        if s_sid:
            a_save_type = {
                            'file_name' : 'clone_' + s_sid + '.tmp'
                           , 'check_type' : 'EMC'
                           , 'execute_type' : 'CLONE'
                        }

            s_title = 'EMC CLONE(SERVER : %s , SID : %s)' % (self.o_common.s_host_name, s_sid)
            self.o_common.screenshot(self.o_common.get_agent_head_msg(s_title), a_save_type=a_save_type, b_start=True)

            for s_emc_cmd, s_emc_cmd_tmp in sorted(self.a_emc_cmd_list.items()):
                s_title, s_cmd = self.get_cmd_parse(s_emc_cmd_tmp)
                if '<SID>' in s_cmd:
                    s_emc_cmd = s_cmd.replace('<SID>', s_sid)

                    if sys.platform == "win32":
                        a_re_tmp = re.findall("(.+)(awk '{.+}')(.+)", s_emc_cmd)
                        if len(a_re_tmp) > 0:
                            s_emc_cmd_tmp_re = ''
                            for s_re_cmd in a_re_tmp[0]:
                                if s_re_cmd.startswith('awk'):
                                    s_re_cmd = s_re_cmd.replace("\"", '\\"')
                                    s_re_cmd = s_re_cmd.replace("'", '"')
                                s_emc_cmd_tmp_re += s_re_cmd
                            s_emc_cmd = s_emc_cmd_tmp_re

                    s_rtn = self.o_common.get_execute(s_emc_cmd)
                    self.o_common.screenshot(self.o_common.get_cmd_title_msg(s_title), a_save_type=a_save_type)
                    self.o_common.screenshot(s_rtn, a_save_type=a_save_type)

            self.o_common.screenshot(self.o_common.get_agent_tail_msg(False), a_save_type=a_save_type)
            self.b_end_flag = True

    def emc_clone(self):
        if self.url_check() is True:
            a_sid_list = self.get_sid()

            if isinstance(a_sid_list, list) and len(a_sid_list) > 0:
                for s_sid in a_sid_list:
                    if len(s_sid.strip()) > 0:
                        self.emc_checker(s_sid.strip())
        else:
            print('Not EMC Sym Module Check Target Server')
        return self.b_end_flag
