#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2016.08.16
    @author: jhbae
'''
from . import common
import os
import sys
import glob
try:
    import pwd
except:
    pass

class DbInfoInformixPosix():

    def __init__(self):
        self.o_common = common.Common()
        self.a_save_type = {}

    def options(self, s_item):
        a_options_dict = {
                           'INFORMIX TABLE INFO': self.informix_table_info
                       }
        return a_options_dict[s_item]()

    def informix_instance_list(self):
        s_cmd = 'ps -ef | grep informix | grep oninit | grep -v grep'
        s_ret = self.o_common.get_execute(s_cmd)

        a_ps_list = []
        a_tmp_list = []

        for i in s_ret.splitlines():
            a_tmp = i.split()
            if len(a_tmp) > 1:
                s_uname = a_tmp[0]
                s_psname = a_tmp[-1]

                if 'oninit' in s_psname and s_psname not in a_tmp_list:
                    a_tmp_list.append(s_psname)
                    s_inst, s_home_dir = self.get_inst(s_psname)

                    a_informix_dic = {}
                    a_informix_dic['inst'] = s_inst
                    a_informix_dic['homeDir'] = s_home_dir
                    a_informix_dic['uname'] = s_uname
                    a_informix_dic['uid'] = self.get_uid(s_uname)
                    a_informix_dic['psname'] = s_psname
                    if os.path.isdir(os.path.join(s_home_dir, 'DBS')):
                        a_informix_dic['dbs'] = os.path.join(s_home_dir, 'DBS')
                    else:
                        a_informix_dic['dbs'] = os.path.join(s_home_dir, 'storage')

                    a_cfg_list = glob.glob(os.path.join(s_home_dir, '.online_*'))

                    s_tmp = ''

                    if len(a_cfg_list) > 0:
                        s_tmp = a_cfg_list[0]

                    a_informix_dic['cfgfile'] = s_tmp
                    a_ps_list.append(a_informix_dic)
        return a_ps_list

    def get_uid(self, s_uname):
        i_uid = 0
        try:
            i_uid = pwd.getpwnam(s_uname).pw_uid
        except:
            pass
        return i_uid

    def get_inst(self, s_proc_name):
        s_inst, s_info_dir = '', ''

        if '/bin/oninit' in s_proc_name:
            s_info_dir = s_proc_name.replace('/bin/oninit', '')
            s_inst = s_info_dir.split('/')[-1]
        return s_inst, s_info_dir

    def informix_table_info(self):

        a_instance_list = self.informix_instance_list()

        s_msg = ''
        for a_instance in a_instance_list:
            s_inst = a_instance['inst']
            s_cfg_file = a_instance['cfgfile']
            s_uname = a_instance['uname']
            s_cfg_file = a_instance['cfgfile']
            s_dbs = a_instance['dbs']
            if s_cfg_file:
                s_cmd = "su - %s -c '. %s; onstat -'" % (s_uname, s_cfg_file)
            else:
                s_cmd = "su - %s -c 'onstat -'" % (s_uname)

            if '-- On-Line --' in self.o_common.get_execute(s_cmd):
                self.o_common.screenshot(self.o_common.get_db_head('INFORMIX', s_inst), a_save_type=self.a_save_type)
                if s_cfg_file:
                    s_cmd = "su - %s -c '. %s;onstat -d update'" % (s_uname, s_cfg_file)
                else:
                    s_cmd = "su - %s -c 'onstat -d update'" % (s_uname)

                s_msg = 'DB INSTANCE A: %s\n' % (s_inst)
                s_msg += self.o_common.get_execute(s_cmd) + '\n'

                s_msg += '###***INFORMIX TABLESPACE INFO***###\n'
                s_msg += 'DB INSTANCE B: %s\n' % (s_inst)
                if s_cfg_file:
                    s_cmd = "su - %s -c '. %s;onstat -T'" % (s_uname, s_cfg_file)
                else:
                    s_cmd = "su - %s -c 'onstat -d update'" % (s_uname)
                s_msg += self.o_common.get_execute(s_cmd) + '\n'
                s_msg += '###***INFORMIX FILE INFO***###\n'
                s_msg += 'DB INSTANCE C: %s\n' % (s_inst)
                s_cmd_ls = 'ls -al %s\n' % (s_dbs)
                s_msg += self.o_common.get_execute(s_cmd_ls)
        return s_msg

    def main(self, a_save_type):
        self.a_save_type = a_save_type
        a_execute_items = self.o_common.cfg_parse_read('dbms.cfg', 'INFORMIX')
        for s_execute_cmd_name, s_flag in a_execute_items:
            if s_flag == 'T':
                self.o_common.screenshot(self.o_common.get_cmd_title_msg(s_execute_cmd_name), a_save_type=self.a_save_type)
                self.o_common.screenshot(self.options(s_execute_cmd_name), a_save_type=self.a_save_type)
