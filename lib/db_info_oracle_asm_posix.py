#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2016.08.22
    @author: jhbae
'''
import os
import sys
from . import common
from .db_info_oracle_getuser import DbInfoOracleExecute

from .oracle_auth import OracleAuth

class DbInfoOracleAsmPosix():
    def __init__(self, b_jdbc, o_jdbc):
        self.b_jdbc = b_jdbc
        self.o_jdbc = o_jdbc
        self.o_common = common.Common()
        self.s_aes_cipher = self.o_common.s_aes_cipher
        self.o_oracle_auth = OracleAuth()
        self.a_save_type = {}

    def get_instance_default(self):

        s_cmd = 'ps -ef |grep asmb |egrep -v "\+ASM|grep"'
        s_ret = self.o_common.get_execute(s_cmd)
        a_instance_list = {'SID':'', 'ORAUSER':''}
        a_ret_instance = s_ret.splitlines()
        if len(a_ret_instance) > 0:
            for line in a_ret_instance:
                a_tmp = line.split()
                a_instance_list['ORAUSER'] = a_tmp[0]
                if isinstance(a_tmp[-1],bytes):
                    s_sid = a_tmp[-1].encode('utf-8').split('_')[-1]
                else:
                    s_sid = a_tmp[-1].split('_')[-1]
                a_instance_list['SID'] = s_sid

        return a_instance_list

    def run(self, a_instance):
        s_ora_user = a_instance['ORAUSER']
        s_sid = a_instance['SID']

        if s_sid == '':
            return
        self.o_common.screenshot(self.o_common.get_db_head(s_db_type='ORACLE (ASM)', s_user=s_ora_user), a_save_type=self.a_save_type)

        s_cmd = "oracleasm listdisks"
        self.o_common.screenshot(self.o_common.get_cmd_title_msg(s_cmd), a_save_type=self.a_save_type)
        self.o_common.screenshot(self.o_common.get_execute(s_cmd), a_save_type=self.a_save_type)

        s_cmd = "oracleasm listdisks | awk '{print \"oracleasm querydisk -p \"$1}'|sh"
        self.o_common.screenshot(self.o_common.get_cmd_title_msg(s_cmd), a_save_type=self.a_save_type)
        self.o_common.screenshot(self.o_common.get_execute(s_cmd), a_save_type=self.a_save_type)

        s_title = "ASM Query"
        self.o_common.screenshot(self.o_common.get_cmd_title_msg(s_title), a_save_type=self.a_save_type)

        # JDBC
        if self.b_jdbc is True:
            s_asm_info = self.o_jdbc.get_query('./sql/asm.sql')

        # JDBC가 아닐때
        else:
            s_file = os.path.join('.','sql','asm.sql')
            o_asm_enc = self.o_common.file_read(s_file)
            print(o_asm_enc)
            print(self.s_aes_cipher.decrypt(o_asm_enc))
            self.o_common.file_write('/tmp/asm.sql', self.s_aes_cipher.decrypt(o_asm_enc), s_agent_path=False)
            s_file_name = os.path.join('/tmp', 'asm.sql')
            print(s_ora_user, s_sid, s_file_name)
            b_multi_check, s_cmd = self.o_oracle_auth.oracle_command(s_ora_user, s_sid, s_file_name)

            if b_multi_check is False :
                s_ora_user = None

            s_rtn = DbInfoOracleExecute().get_execute(s_cmd, s_ora_user)
            if os.path.isfile('/tmp/asm.tmp'):
                s_asm_info = self.o_common.file_read('/tmp/asm.tmp', False)
            else:
                s_asm_info = s_rtn
        self.o_common.screenshot(s_asm_info, a_save_type=self.a_save_type)

    def main(self, a_save_type):

        self.a_save_type = a_save_type

        a_instance = self.get_instance_default()
        s_sid = a_instance['SID']
        if self.b_jdbc is True:
            if self.o_jdbc.jdbc(s_sid) is False:
                print("[ERROR] Check Oracle Network Connection - Oracle Listener SID : %s" % (s_sid))
        self.run(a_instance)

        if os.path.isfile('/tmp/asm.tmp'):
            os.remove('/tmp/asm.tmp')

        if os.path.isfile('/tmp/asm.sql'):
            os.remove('/tmp/asm.sql')
