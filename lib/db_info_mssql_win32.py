#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2016.08.09
    @author: jhbae
'''
from . import common
import re
import os
class DbinfoMssqlWin32():
    def __init__(self):

        self.o_common = common.Common()
        self.s_aes_cipher = self.o_common.s_aes_cipher
        self.s_host_name = self.o_common.s_host_name
        self.mssql_auth = self.mssql_conn_info()
        self.a_get_db_list = self.get_db_list()

    def options(self, s_item):
        a_options_dict = {
                           'version': self.mssql_version
                          , 'Database info' : self.database_info
                          , 'Tablespace info' : self.tablespace_info
                          , 'param' : self.param_info
                       }

        return a_options_dict[s_item]()

    def mssql_conn_info(self):
        a_mssql_option = {
                          'windows_auth': ''
                          , 'user' : ''
                          , 'passwd' : ''
                          , 'server_name' : ''
                        }

        a_auth_config = self.o_common.cfg_parse_read('dbms.cfg', 'MSSQL_AUTH')

        if len(a_auth_config) > 0:
            for s_auth, s_value in a_auth_config:
                a_mssql_option[s_auth] = s_value
        return a_mssql_option

    def sqlcmd(self, s_query, b_custom=False):

        if s_query:
            s_query = s_query.replace("\r\n", " ")
            s_query = re.sub('\s+', ' ', s_query)

        if self.mssql_auth['server_name'] != '':
            s_sqlcmd = 'sqlcmd -S %s' % (self.mssql_auth['server_name'])
        else:
            s_sqlcmd = 'sqlcmd '


        if self.mssql_auth['windows_auth'].lower() == 'y' or b_custom == True:
            s_cmd = '%s -Q \"SET NOCOUNT ON; %s\" -h-1 -s, -W' % (s_sqlcmd , s_query)
        else:
            s_user = self.mssql_auth['user']
            s_passwd = self.mssql_auth['passwd']
            s_password = self.s_aes_cipher.decrypt(s_passwd)
            s_cmd = '%s -U %s -P %s -Q \"SET NOCOUNT ON; %s\" -h-1  -s, -W' % (s_sqlcmd, s_user, s_password, s_query)

        s_return_msg = self.o_common.get_execute(s_cmd)
        return str(s_return_msg, 'cp949')

    def get_db_list(self):
        s_cmd = "SELECT name FROM master.dbo.sysdatabases"
        a_db_list = self.sqlcmd(s_cmd).split("\n")

        return a_db_list

    def mssql_version(self):
        return self.sqlcmd("SELECT @@VERSION", True)

    def replace_query(self , s_db_name , s_tmp_query):
        if re.search('<HOSTNAME>', s_tmp_query):
            s_tmp_query = s_tmp_query.replace('<HOSTNAME>', self.o_common.s_host_name)

        if re.search('<DATABASENAME>', s_tmp_query):
            s_tmp_query = s_tmp_query.replace('<DATABASENAME>', s_db_name)
        return s_tmp_query

    def database_info(self):
        o_dbsize_enc = self.o_common.file_read(os.path.join('sql','dsize.sql'))
        print(o_dbsize_enc)
        o_dbsize_contents = self.s_aes_cipher.decrypt(o_dbsize_enc)

        if len(self.a_get_db_list) > 0:
            s_db_info = ''
            for s_db_name in self.a_get_db_list:
                s_replace_query = self.replace_query(s_db_name.strip(), o_dbsize_contents)
                s_db_info += '\n' + self.sqlcmd(s_replace_query)
        return s_db_info

    def tablespace_info(self):
        o_tablespace_enc = self.o_common.file_read(os.path.join('sql','tsize.sql'))
        o_tablespace_contents = self.s_aes_cipher.decrypt(o_tablespace_enc)

        if len(self.a_get_db_list) > 0:
            s_tablespace_info = ''
            for s_db_name in self.a_get_db_list:
                s_replace_query = self.replace_query(s_db_name.strip(), o_tablespace_contents)
                s_tablespace_info += '\n' + self.sqlcmd(s_replace_query)
        return s_tablespace_info

    def param_info(self):
        o_param_enc = self.o_common.file_read(os.path.join('sql','param.sql'))
        o_param_contents = self.s_aes_cipher.decrypt(o_param_enc)
        a_query_dict = {}

        s_split_version = "SELECT SERVERPROPERTY('productversion')"
        s_version_tmp = self.sqlcmd(s_split_version, True)
        if re.match("^[0-9]+\.[0-9]+", s_version_tmp):
            a_version_tmp = s_version_tmp.split('.')
            if int(a_version_tmp[0]) > 10:
                o_param_contents = o_param_contents.replace('bpool_committed', 'committed_kb')
                o_param_contents = o_param_contents.replace('bpool_commit_target', 'committed_target_kb')

        i_cnt = 0
        s_tmp = ""
        s_param_info = ""
        for s_query_split in o_param_contents.split("\n"):
            if re.search("^go", s_query_split.strip().lower()):
                i_cnt = i_cnt + 1
                s_tmp = ""
            s_query_split = re.sub("^go", "", s_query_split)
            s_tmp = s_tmp + " " + s_query_split.strip()
            a_query_dict[i_cnt] = s_tmp

        for s_query in list(a_query_dict.values()):
            if len(s_query.strip()) > 0:
                s_param_info += '\n' + self.sqlcmd(s_query.strip(), True) + "\n"

        return s_param_info

    def main(self, a_save_type):

        a_execute_items = self.o_common.cfg_parse_read('dbms.cfg', 'MSSQL')
        self.o_common.screenshot(self.o_common.get_db_head('MSSQL'), a_save_type=a_save_type)

        for s_execute_cmd_name, s_flag in a_execute_items:
            if s_flag == 'T':
                self.o_common.screenshot(self.o_common.get_cmd_title_msg(s_execute_cmd_name), a_save_type=a_save_type)
                self.o_common.screenshot(self.options(s_execute_cmd_name), a_save_type=a_save_type)
