#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2017.09.14
    @author: jhbae
'''
import os
import sys
from . import common
import subprocess
import re

class DbInfoAltibasePosix():

    def __init__(self):
        self.o_common = common.Common()
        self.s_aes_cipher = self.o_common.s_aes_cipher
        self.s_alti_proc = self.o_common.cfg_parse_read('dbms.cfg', 'DBMS_POSIX_PROCESS', 'ALTIBASE')
        self.s_version = ''

    def options(self, s_item, s_version):
        a_options_dict = {
                           'version': self.altibase_version
                          , 'Disk Tablespace info' : self.disk_tablespace_info
                          , 'Memory Tablespace info' : self.memory_tablespace_info
                       }
        return a_options_dict[s_item](s_version)


    def altibase_version_check(self):
        s_user_name = self.o_common.get_user_pid_posix(self.s_alti_proc)
        s_cmd = 'su - %s -c "altibase -v  " | grep version | awk \'{print $2}\'' % (s_user_name)

        s_alti_version = self.o_common.get_execute(s_cmd).strip()
        return s_alti_version[0:5]


    def symbolic_pattern_replace(self, s_str):
        a_str = s_str.split('\n')

        for a in a_str:
            if re.search(r'^DTFP|MTFP', a):
                b = a.split(',')
                c = os.path.split(b[-1])
                d = subprocess.getoutput('cd %s;pwd -P' % (c[0]))
                e = os.path.join(d, c[1])
                if b[-1] != e :
                    s_str = s_str.replace(b[-1], e)
        return s_str

    def sqlcmd(self, s_file='') :
        s_cmd = ''
        o_file_cont_enc = self.o_common.file_read(s_file)
        a_file_info = os.path.split(s_file)

        s_file_name = os.path.join(self.o_common.s_tmp_path, a_file_info[1])

        self.o_common.file_write(s_file_name, self.s_aes_cipher.decrypt(o_file_cont_enc), s_agent_path=False)

        s_cmd = ' is -f %s' % s_file_name

        s_user_name = self.o_common.get_user_pid_posix(self.s_alti_proc)
        s_cmd = 'su - %s -c "%s"' % (s_user_name, s_cmd)

        if os.path.isfile(s_file_name):
            s_rtn = self.o_common.get_execute(s_cmd).strip()
            if s_rtn != '':
                s_rtn = self.symbolic_pattern_replace(s_rtn)
                os.remove(s_file_name)
        else:
            s_rtn = '[%s] File Not Found' % s_file_name

        return s_rtn

    def altibase_version(self, s_version=''):
        s_file = '/sql/altibase_version.sql'
        return self.sqlcmd(s_file)

    def disk_tablespace_info(self, s_version=''):
        s_file = '/sql/altibase_disk_tablespace_%s.sql' % (s_version)
        s_disk_tablespace_info = self.sqlcmd(s_file=s_file)
        return s_disk_tablespace_info

    def memory_tablespace_info(self, s_version=''):
        s_file = '/sql/altibase_memory_tablespace_%s.sql' % (s_version)

        s_memory_tablespace_info = self.sqlcmd(s_file=s_file)
        return s_memory_tablespace_info


    def main(self, a_save_type):
        if os.path.isfile(os.path.join(self.o_common.s_config_path, 'altibase.cfg')):
            s_alti_version_check = self.altibase_version_check()

            try:
                s_version = self.o_common.cfg_parse_read('altibase.cfg', 'VERSION', s_alti_version_check)
                if len(s_version) < 1:
                    print("CFG VERSION Unsupported version %s " % (s_alti_version_check))
                    raise NameError
                a_execute_items = self.o_common.cfg_parse_read('dbms.cfg', 'ALTIBASE')

                self.o_common.screenshot(self.o_common.get_db_head('ALTIBASE'), a_save_type=a_save_type)

                for s_execute_cmd_name, s_flag in a_execute_items:
                    if s_flag == 'T':
                        self.o_common.screenshot(self.o_common.get_cmd_title_msg(s_execute_cmd_name), a_save_type=a_save_type)
                        self.o_common.screenshot(self.options(s_execute_cmd_name, s_version), a_save_type=a_save_type)
            except Exception:
                print("Unsupported version %s " % (s_alti_version_check))
                self.o_common.screenshot("Unsupported version %s " % (s_alti_version_check), a_save_type=a_save_type)
        else:
            print("Altibase Config File Not found.")

