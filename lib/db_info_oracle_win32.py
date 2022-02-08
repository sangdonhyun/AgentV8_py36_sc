#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2016.08.09
    @author: jhbae
'''
import re
import os
from . import common
import sys
import wmi

class DbinfoOracleWin32():
    def __init__(self):
        self.o_common = common.Common()
        self.s_host_name = self.o_common.s_host_name
        self.a_get_instance_list = self.get_instance_list()
        self.s_aes_cipher = self.o_common.s_aes_cipher
        self.s_sid = ''

        # JDBC
        self.b_jdbc = False
        self.get_jdbc()

    def get_jdbc(self):
        s_usage = self.o_common.cfg_parse_read('jdbc.cfg', 'jdbc', 'jdbc_usage')
        if s_usage.upper() == 'Y':
            try:
                from .db_info_oracle_jdbc import DbInfoOracleJdbc
                self.o_jdbc = DbInfoOracleJdbc()
                self.b_jdbc = True
            except:
                print('Exception JDBC')
                self.b_jdbc = False

    def options(self, s_item):
        a_options_dict = {
                           'version': self.oracle_version
                          , 'Tablespace info' : self.tablespace_info
                          , 'ocrcheck' : self.ocrcheck
                          , 'crsctl query css votedisk' : self.csrctl_votedisk
                       }
        return a_options_dict[s_item]()

    def sqlcmd(self, s_file='' , s_sid=''):
        s_cmd = ''

        o_file_cont_enc = self.o_common.file_read(s_file)
        a_file_info = os.path.split(s_file)
        s_dec_query = self.s_aes_cipher.decrypt(o_file_cont_enc)
        o_p = re.compile(r"^set[^\n]+|select[^;]+;", re.IGNORECASE | re.MULTILINE | re.DOTALL)

        a_regex = o_p.findall(s_dec_query)

        # self.o_common.file_write('/tmp/' + a_file_info[1], '\n'.join(a_regex))
        # s_file_name = self.o_common.s_tmp_path + a_file_info[1]

        s_file_name = os.path.join(self.o_common.s_tmp_path, a_file_info[1])
        self.o_common.file_write(s_file_name, '\n'.join(a_regex), s_agent_path=False)

        s_sqlcmd = 'sqlplus.exe -s '
        s_sysdba_check = self.o_common.cfg_parse_read('dbms.cfg', 'ORACLE_AUTH', 'sysdba')

        if s_sysdba_check.strip() == 'y':
            s_cmd = '%s /@%s as sysdba < %s' % (s_sqlcmd, s_sid, s_file_name)
        else:
            # a_auth_info = self.o_common.tuple_to_dict(self.o_common.cfg_parse_read('oracle.cfg', s_sid))
            a_auth_info = self.o_common.cfg_parse_read('oracle.cfg', s_sid)

            if len(a_auth_info) > 0:
                s_user = a_auth_info['user'].strip()
                try:
                    s_password = self.o_common.s_aes_cipher.decrypt(a_auth_info['passwd'].strip())
                except:
                    s_password = a_auth_info['passwd'].strip()

                s_hostname = a_auth_info['hostname'].strip()
                s_port = a_auth_info['port'].strip()

                if s_port.strip() == '':
                    s_port = '1521'
                if s_hostname != '':
                    s_network = "%s:%s/%s" % (s_hostname, s_port, s_sid)
                else:
                    s_network = s_sid

                s_cmd = '%s %s/%s@%s < %s' % (s_sqlcmd, s_user, s_password, s_network, s_file_name)

        return self.o_common.get_execute(s_cmd).strip()

    def get_instance_list(self):
        a_instance = []
        try:
            o_wmi = wmi.GetObject(r"winmgmts:\root\cimv2")
            s_wmi_service = "SELECT Caption FROM Win32_Service WHERE Caption LIKE 'OracleService%' AND Started=True"

            for o_item in o_wmi.ExecQuery(s_wmi_service):
                s_tmp = o_item.Name.replace('OracleService', '')
                a_instance.append(str(s_tmp.strip()))
        except :
            pass

        if len(a_instance) < 1:
            a_instance = self.o_common.cfg_section_read('oracle.cfg')
        return a_instance

    def oracle_version(self):
        s_file = '/sql/oracle_version.sql'
        if self.b_jdbc is True:
            return self.o_jdbc.get_version(s_file)
        else:
            return self.sqlcmd(s_file, s_sid=self.s_sid)

    def tablespace_info(self):
        s_file = '/sql/ora.sql'
        s_tablespace_info = ''

        if self.b_jdbc is True:
            return self.o_jdbc.get_query(s_file)
        else:
            s_tablespace_info += self.sqlcmd(s_file, s_sid=self.s_sid)
            return s_tablespace_info

    def ocrcheck(self):
        s_cmd_name = 'ocrcheck'
        return self.o_common.get_execute(s_cmd_name).strip()

    def csrctl_votedisk(self):
        s_cmd_name = 'crsctl query css votedisk'
        return self.o_common.get_execute(s_cmd_name).strip()

    def main(self, a_save_type):
        a_execute_items = self.o_common.cfg_parse_read('dbms.cfg', 'ORACLE')

        for s_sid in self.a_get_instance_list:
            b_version_check = False
            s_sid = s_sid.strip()

            self.o_common.screenshot(self.o_common.get_db_head('ORACLE', s_sid), a_save_type=a_save_type)
            self.s_sid = s_sid

            # # JDBC 일경우
            if self.b_jdbc is True:
                self.o_jdbc.jdbc(self.s_sid)

            for s_execute_cmd_name, s_flag in a_execute_items:
                if s_flag == 'T':
                    if b_version_check and s_execute_cmd_name == 'version':
                        return
                    if s_execute_cmd_name == 'version' and b_version_check is False:
                        b_version_check = True
                    self.o_common.screenshot(self.o_common.get_cmd_title_msg(s_execute_cmd_name), a_save_type=a_save_type)
                    self.o_common.screenshot(self.options(s_execute_cmd_name), a_save_type=a_save_type)
