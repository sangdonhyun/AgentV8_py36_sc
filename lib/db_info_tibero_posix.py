#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2017.10.10
    @author: jhbae
'''
import os
import sys
import re
import platform
from . import common

class DbInfoTiberoPosix():
    def __init__(self):
        self.o_common = common.Common()
        self.s_aes_cipher = self.o_common.s_aes_cipher
        b_ld = False

        if 'TB_HOME' in os.environ:
            s_tibero_cli = os.path.join(os.environ['TB_HOME'], 'client/bin')
            os.environ['PATH'] = ':'.join([s_tibero_cli, os.getenv('PATH')])

            if platform.uname()[0] == 'Linux':
                a_ld_path = os.environ['LD_LIBRARY_PATH'].split(':')

                for s_ld in a_ld_path:
                    if re.search(os.environ['TB_HOME'] + '/lib', s_ld):
                        b_ld = True
                        break
                if b_ld is False:
                    s_ld_path = os.environ['TB_HOME'] + '/lib' + ':' + os.environ['TB_HOME'] + '/client/lib'
                    os.environ['LD_LIBRARY_PATH'] = ':'.join([s_ld_path, os.getenv('LD_LIBRARY_PATH')])

    def get_instance_list(self):
        if platform.uname()[0] == 'SunOS':
            if os.path.isfile('/usr/ucb/ps'):
                s_instance_check = "/usr/ucb/ps -auxww | egrep 'tbsvr.*SVR_SID'|grep -v egrep |awk '{print $1, $NF}'|sort -u"
            else:
                s_instance_check = "ps -ef | egrep 'tbsvr.*SVR_SID'|grep -v egrep |awk '{print $1, $NF}'|sort -u"
        else:
            s_instance_check = "ps -ef | egrep 'tbsvr.*SVR_SID'|grep -v egrep |awk '{print $1, $NF}'|sort -u"

        s_proc_check_cmd = self.o_common.get_execute(s_instance_check)

        a_tibero_dic_list = []
        for s_ps_value in s_proc_check_cmd.split('\n'):
            a_tmp = s_ps_value.split()

            try:
                s_uname = a_tmp[0]
                s_instance = a_tmp[1]
                a_tibero_dic = {}
                a_tibero_dic['user'] = s_uname
                a_tibero_dic['sid'] = s_instance
                a_tibero_dic_list.append(a_tibero_dic)
            except :
                pass

        return a_tibero_dic_list



    def options(self, s_item, a_instance):
        a_options_dict = {
                           'version': self.tibero_version
                          , 'Tablespace info' : self.tablespace_info
                       }
        return a_options_dict[s_item](a_instance)


    def sqlcmd(self, s_file='' , s_sid='', s_switch_user='') :
        s_cmd = ''
        o_file_cont_enc = self.o_common.file_read(s_file)
        a_file_info = os.path.split(s_file)

        self.o_common.file_write(os.path.join('/tmp', a_file_info[1]), self.s_aes_cipher.decrypt(o_file_cont_enc), s_agent_path=False)
        s_file_name = os.path.join('/tmp', a_file_info[1])

        s_sysdba_check = self.o_common.cfg_parse_read('dbms.cfg', 'TIBERO_AUTH', 'sysdba')

        if s_sysdba_check.lower().strip() == 'y':
            s_sql_cmd = '< %s' % (s_file_name)
        else:
            try:
                # a_auth_info = self.o_common.tuple_to_dict(self.o_common.cfg_parse_read('tibero.cfg', s_sid))
                a_auth_info = self.o_common.cfg_parse_read('tibero.cfg', s_sid)
            except:
                a_auth_info = {}

            if len(a_auth_info) > 0:
                s_user = a_auth_info['user'].strip()
                try:
                    s_password = self.o_common.s_aes_cipher.decrypt(a_auth_info['passwd'].strip())
                except:
                    s_password = a_auth_info['passwd'].strip()

            else:
                s_user = 'sys'
                s_password = 'tibero'

            s_sql_cmd = '%s/%s < %s' % (s_user, s_password, s_file_name)



        if s_switch_user.lower() == 'root':
            s_cmd = 'export TB_SID=%s;tbsql %s' % (s_sid, s_sql_cmd)
        else:
            s_cmd = 'su - %s -c "export TB_SID=%s;tbsql -s %s"' % (s_switch_user, s_sid, s_sql_cmd)
        return self.o_common.get_execute(s_cmd).strip()

    def tibero_version(self, a_val):
        s_file = '/sql/tibero_version.sql'
        s_switch_user = a_val['user']
        s_sid = a_val['sid']

        if os.path.isfile('/tmp/tibero_version.sql'):
            os.remove('/tmp/tibero_version.sql')
        return self.sqlcmd(s_file, s_sid=s_sid, s_switch_user=s_switch_user)

    def tablespace_info(self, a_val):
        s_file = '/sql/tibero.sql'
        s_sid = a_val['sid']
        s_switch_user = a_val['user']

        self.sqlcmd(s_file=s_file, s_sid=s_sid, s_switch_user=s_switch_user)
        s_tablespace_info = self.o_common.file_read('/tmp/tibero.tmp', False)

        if os.path.isfile('/tmp/tibero.sql'):
            os.remove('/tmp/tibero.sql')
        return str(s_tablespace_info, 'cp949')

    def main(self, a_save_type):

        a_execute_items = self.o_common.cfg_parse_read('dbms.cfg', 'TIBERO')

        for a_instance_info in self.get_instance_list():
            b_version_check = False
            s_sid = a_instance_info['sid'].strip()

            self.o_common.screenshot(self.o_common.get_db_head('TIBERO', s_sid), a_save_type=a_save_type)

            for s_execute_cmd_name, s_flag in a_execute_items:
                if s_flag == 'T':
                    if b_version_check and s_execute_cmd_name == 'version':
                        return

                    if s_execute_cmd_name == 'version' and b_version_check == False:
                        b_version_check = True

                    self.o_common.screenshot(self.o_common.get_cmd_title_msg(s_execute_cmd_name), a_save_type=a_save_type)
                    self.o_common.screenshot(self.options(s_execute_cmd_name, a_instance_info), a_save_type=a_save_type)

            if os.path.isfile('/tmp/tibero.tmp'):
                os.remove('/tmp/tibero.tmp')


