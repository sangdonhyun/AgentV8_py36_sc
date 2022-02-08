#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2016.08.16
    @author: jhbae
'''
import os
import sys
import pwd
from . import common
from .db_info_oracle_getuser import DbInfoOracleExecute

from .oracle_auth import OracleAuth

class DbInfoOraclePosix():

    def __init__(self):
        self.o_common = common.Common()
        self.s_aes_cipher = self.o_common.s_aes_cipher
        self.o_oracle_auth = OracleAuth()
        # JDBC
        self.b_jdbc = False
        self.o_jdbc = ''
        self.get_jdbc()

    def get_jdbc(self):
        s_usage = self.o_common.cfg_parse_read('jdbc.cfg', 'jdbc', 'jdbc_usage')
        if s_usage.upper() == 'Y':
            try:
                from .db_info_oracle_jdbc import DbInfoOracleJdbc
                self.o_jdbc = DbInfoOracleJdbc()
                self.b_jdbc = True
            except:
                self.b_jdbc = False

    def get_instance_list(self):
        proc_check_cmd = self.o_common.get_execute('ps -ef | grep ora_pmon | grep -v grep')
        a_ora_dic_list = []
        for s_ps_value in proc_check_cmd.splitlines():
            a_tmp = s_ps_value.split()
            try:
                s_uname = a_tmp[0]
                ora_pmon = a_tmp[-1]
                if isinstance(ora_pmon,bytes):
                    ora_pmon = ora_pmon.decode('utf-8')
                s_instance = ora_pmon.split('ora_pmon_')[1]
                a_ora_dic = {}
                a_ora_dic['user'] = s_uname
                a_ora_dic['sid'] = s_instance
                a_ora_dic_list.append(a_ora_dic)
            except Exception as e:
                print(str(e))

        return a_ora_dic_list

    def get_msg(self, s_instance):
        import datetime
        s_msg = ''
        s_msg = s_msg + '#' * 50 + '\n'
        s_msg = s_msg + '#' + ('HOSTNAME : %s' % (self.o_common.s_host_name)).ljust(48) + '#\n'
        s_msg = s_msg + '#' + ('DATABASE : ORACLE').ljust(48) + '#\n'
        s_msg = s_msg + '#' + ('INSTANCE : %s' % (s_instance)).ljust(48) + '#\n'
        s_msg = s_msg + '#' + ('DATE     : %s' % datetime.datetime.now()).ljust(48) + '#\n'
        s_msg = s_msg + '#' * 50 + '\n'
        return s_msg

    def options(self, s_item, a_instance):
        a_options_dict = {
                           'version': self.oracle_version
                          , 'Tablespace info' : self.tablespace_info
                          , 'ocrcheck' : self.ocrcheck
                          , 'crsctl query css votedisk' : self.csrctl_votedisk
                       }
        return a_options_dict[s_item](a_instance)


    def sqlcmd(self, s_file='' , s_sid='', s_switch_user='') :
        s_cmd = ''
        o_file_cont_enc = self.o_common.file_read(s_file)
        a_file_info = os.path.split(s_file)

        self.o_common.file_write(os.path.join('/tmp', a_file_info[1]), self.s_aes_cipher.decrypt(o_file_cont_enc), s_agent_path=False)
        s_file_name = os.path.join('/tmp', a_file_info[1])

        #### EDITING ####

        b_multi_check, s_cmd, b_unable_root = self.o_oracle_auth.oracle_command(s_switch_user, s_sid, s_file_name)

        #### EDITING ####
        if b_multi_check is False or b_unable_root is True:
            s_switch_user = None


        return DbInfoOracleExecute().get_execute(s_cmd, s_switch_user)

    def oracle_version(self, a_val):
        s_file = '/sql/oracle_version.sql'
        s_switch_user = a_val['user']
        s_sid = a_val['sid']

        if self.b_jdbc is True:
            return self.o_jdbc.get_version(s_file)
        else:
            return self.sqlcmd(s_file, s_sid=s_sid, s_switch_user=s_switch_user)

    def tablespace_info(self, a_val):

        s_file = './sql/ora.sql'
        s_sid = a_val['sid']
        s_switch_user = a_val['user']
        if self.b_jdbc is True:
            return self.o_jdbc.get_query(s_file)
        else:
            s_rtn = self.sqlcmd(s_file=s_file, s_sid=s_sid, s_switch_user=s_switch_user)

            if os.path.isfile('/tmp/ora.tmp'):
                s_tablespace_info = self.o_common.file_read('/tmp/ora.tmp', False)
            else:
                # try:
                s_tablespace_info = s_rtn
                # except Exception as e:
                #     print(str(e))
                #     s_tablespace_info =''
                #     pass

            return s_tablespace_info

    def ocrcheck(self, a_val):
        s_cmd = 'ocrcheck'
        DbInfoOracleExecute().get_oracle_grid_path(a_val['user'])
        return self.o_common.get_execute(s_cmd)

    def csrctl_votedisk(self, a_val):
        s_cmd = 'crsctl query css votedisk'
        DbInfoOracleExecute().get_oracle_grid_path(a_val['user'])
        return self.o_common.get_execute(s_cmd)

    def main(self, a_save_type):
        oldmode=os.stat('/tmp').st_mode&0o777
        os.chmod('/tmp',0o777);

        a_get_instance_list = self.get_instance_list()

        a_execute_items = self.o_common.cfg_parse_read('dbms.cfg', 'ORACLE')
        # ASM Check
        if not isinstance(a_execute_items,dict):
            a_execute_items = dict(a_execute_items)
        i_asm_cnt = int(self.o_common.get_execute('ps -ef | grep asm_pmon | grep -v grep | wc -l'))

        if i_asm_cnt > 0:
            from . import db_info_oracle_asm_posix
            o_asm_posix = db_info_oracle_asm_posix.DbInfoOracleAsmPosix(self.b_jdbc, self.o_jdbc)
            o_asm_posix.main(a_save_type)

        for a_instance_info in a_get_instance_list:
            b_version_check = False
            s_sid = a_instance_info['sid'].strip()
            print(self.get_msg(s_sid))
            self.o_common.screenshot(self.get_msg(s_sid), a_save_type=a_save_type)

            # # JDBC 일경우
            if self.b_jdbc is True:
                self.o_jdbc.jdbc(s_sid)

            # for s_execute_cmd_name, s_flag in a_execute_items:
            # {'version': 'F', 'Tablespace info': 'T', 'ocrcheck': 'T', 'crsctl query css votedisk': 'T'}
            s_flag = ''
            s_execute_cmd_name = ''
            for s_execute_cmd_name in a_execute_items.keys():
                s_flag = a_execute_items[s_execute_cmd_name]
                if s_flag == 'T':
                    if b_version_check and s_execute_cmd_name == 'version':
                        return

                    if s_execute_cmd_name == 'version' and b_version_check == False:
                        b_version_check = True

                    #20220203 sdhyun
                    if os.path.isfile('/tmp/ora.tmp'):
                        os.remove('/tmp/ora.tmp')
                    self.o_common.screenshot(self.o_common.get_cmd_title_msg(s_execute_cmd_name), a_save_type=a_save_type)
                    self.o_common.screenshot(self.options(s_execute_cmd_name, a_instance_info), a_save_type=a_save_type)

        # Need to checking Multi-instance

        if os.path.isfile('/tmp/ora.tmp'):
            os.remove('/tmp/ora.tmp')


        if os.path.isfile('/tmp/ora.sql'):
            os.remove('/tmp/ora.sql')
        os.chmod('/tmp',oldmode)