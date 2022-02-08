#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2016.08.09
    @author: jhbae
'''
from . import common
import os
import sys
import wmi

class DbInfoWin32():
    def __init__(self, s_arg):
        self.o_common = common.Common()
        self.s_arg = s_arg
        self.b_end_flag = False
        
    def get_proc_check(self, s_proc_name):
        o_wmi = wmi.GetObject(r"winmgmts:\root\cimv2")
        s_proc_check_query = "SELECT Name FROM Win32_Process where Name ='%s'" %(s_proc_name)

        return len(o_wmi.ExecQuery(s_proc_check_query))

    def db_cnt(self):
        a_proc_name = self.o_common.cfg_parse_read('dbms.cfg', 'DBMS_WIN32_PROCESS')
        a_cnt = {}

        if len(a_proc_name) > 0: 
            for s_proc_key, s_process_name in a_proc_name:
                a_cnt[s_proc_key.upper()] = self.get_proc_check(s_process_name)
        return a_cnt

    def check_query(self, a_db_cnt):
        s_dbms_info = ''
        s_dr_type_check = ''
        s_dr_type = self.o_common.cfg_parse_read('fleta.cfg', 'systeminfo', 'set_device').lower().strip()

        if s_dr_type.lower() in ('fs','vt'):
            s_dr_type_check = 'db'
        else:
            s_dr_type_check = s_dr_type

        for s_db_name, i_cnt in a_db_cnt.items():
            s_dbms_info += "%s : %s\n" %(s_db_name, i_cnt)

        a_save_type = { 
            'file_name' : s_dr_type_check + '_' + self.o_common.s_host_name + '.tmp' 
           ,'check_type' : 'dbinfo'
           ,'execute_type' : self.s_arg
        }

        self.o_common.screenshot(self.o_common.get_agent_head_msg(), a_save_type = a_save_type, b_start = True)
        self.o_common.screenshot(self.o_common.get_cmd_title_msg('DBMS'), a_save_type = a_save_type)
        self.o_common.screenshot(s_dbms_info, a_save_type = a_save_type)

        for s_dbms in a_db_cnt :
            if (s_dbms == 'MSSQL') and int(a_db_cnt['MSSQL']) > 0 :
                from . import db_info_mssql_win32
                o_main = db_info_mssql_win32.DbinfoMssqlWin32()
                o_main.main(a_save_type)

            elif (s_dbms == 'ORACLE') and int(a_db_cnt['ORACLE']) > 0:
                from . import db_info_oracle_win32
                o_main = db_info_oracle_win32.DbinfoOracleWin32()
                o_main.main(a_save_type)
        self.o_common.screenshot(self.o_common.get_agent_tail_msg(), a_save_type = a_save_type)
        
    def main(self):
        a_db_cnt = self.db_cnt()
        for i_cnt in list(a_db_cnt.values()):
            if int(i_cnt) > 0:
                self.check_query(a_db_cnt)
                self.b_end_flag = True
                break
        return self.b_end_flag
