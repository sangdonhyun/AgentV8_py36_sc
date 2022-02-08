#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2016.08.16
    @author: jhbae
'''
import re
import sys
import os
from . import common

class DbInfoUdbPosix():

    def __init__(self):
        self.o_common = common.Common()
        self.shell_dir = os.path.join(self.o_common.s_agent_path, 'scripts')
        self.s_aes_cipher = self.o_common.s_aes_cipher

    def get_user_list(self):
        s_cmd = "ps -ef | grep db2sysc | grep -v grep | awk '{print $1}' | sort -u"
        s_tmp = self.o_common.get_execute(s_cmd)

        a_user_list = []
        for s_ps_value in s_tmp.splitlines():
            try:
                a_user_list.append(s_ps_value.split()[0])
            except:
                pass
        return a_user_list

    def make_init_sh(self, s_user):
        s_init_shell_name = 'db2_inst_%s.sh' % (s_user)

        s_init_shell = os.path.join(self.shell_dir, s_init_shell_name)
        s_sh = '\n'
        s_sh += 'su - %s << EOF\n' % (s_user)
        #s_sh += 'LANG=C\n'
        s_sh += 'db2 list db directory\n'
        s_sh += 'EOF'

        with(open(s_init_shell, 'w')) as o_inst:
            o_inst.write(s_sh)

        os.chmod(s_init_shell, 0o701)

        s_init_shell_execute = self.o_common.get_execute(s_init_shell)

        return self.get_instance(s_user, s_init_shell_execute)

    def get_instance(self, s_user, s_db_list):
        a_tmp = s_db_list.split('entry:')
        a_instance_liist = []

        for s_entry_tmp in a_tmp:
            for a_entry in s_entry_tmp.splitlines():
                if 'Database alias' in a_entry:
                    s_dbname = a_entry.split('=')[1].strip()
                if 'Directory entry type' in a_entry and s_dbname:
                    s_type = a_entry.split('=')[1].strip()
                    a_db_instance_dic = {}
                    a_db_instance_dic['instance'] = s_user
                    a_db_instance_dic['dbname'] = s_dbname
                    a_db_instance_dic['type'] = s_type
                    if s_type == 'Indirect':
                        a_instance_liist.append(a_db_instance_dic)
        return a_instance_liist

    def db2_level(self, s_user, s_instance):
        i_db2_level = 9

        s_level_check_file = self.o_common.s_tmp_path + 'level_check.sh'
        s_sh = ''
        s_sh += 'su - %s << EOF\n' % (s_user)
        #s_sh += 'LANG=C\n'
        s_sh += 'db2level\n'
        s_sh += 'EOF'

        with open(s_level_check_file, 'w') as o_f:
            o_f.write(s_sh)

        os.chmod(s_level_check_file, 0o701)
        s_ret = self.o_common.get_execute(s_level_check_file)

        a_ver_check = re.findall('.*DB2 v([0-9]{1,2}).*', s_ret)
        if len(a_ver_check) > 0:
            i_db2_level = int(a_ver_check[0])
            if int(i_db2_level) > 9:
                i_db2_level = 10
        return i_db2_level

    def make_DB2_sh(self, s_instance, s_db):
        s_query = ''
        s_ret = ''
        s_version = self.db2_level(s_instance, s_db)

        if os.path.isdir(self.o_common.s_tmp_path) == False:
            os.mkdir(self.o_common.s_tmp_path)
            os.chmod(self.o_common.s_tmp_path, 0o707)
        else:
            os.chmod(self.o_common.s_tmp_path, 0o707)

        o_query_contents_enc = self.o_common.file_read('/sql/udb_v%s.sql' % (s_version))

        self.o_common.file_write('/tmp/udb_v%s.sql' % (s_version), self.s_aes_cipher.decrypt(o_query_contents_enc))
        s_query_file = self.o_common.s_tmp_path + '/udb_v%s.sql' % (s_version)
        s_db2sh_file_name = 'db2_sh_%s_%s.sh' % (s_instance, s_db)

        s_db2sh_path = os.path.join(self.shell_dir, s_db2sh_file_name)

        #s_db_tmp_file = self.o_common.s_tmp_path + 'db2_%s.out' % (s_inst)
        s_db_tmp_file = '/tmp/db2_%s_%s.out' % (s_instance, s_db)

        if os.path.isfile(s_query_file):
            s_query = self.o_common.file_read('/tmp/udb_v%s.sql' % (s_version))
        else:
            s_ret = 'Not Supported This Version : %s' % (s_version)
            print(s_ret)
        if s_query:
            s_sh = ''
            s_sh += 'su - %s << EOF\n' % (s_instance)
            #s_sh += 'LANG=C\n'
            s_sh += 'db2 connect to %s\n' % (s_db)
            s_sh += 'db2 \"%s\" > %s\n' % (s_query, s_db_tmp_file)
            s_sh += 'EOF' + '\n'

            with open(s_db2sh_path, 'w') as f:
                f.write(s_sh)

            os.chmod(s_db2sh_path, 0o777)
            self.o_common.get_execute(s_db2sh_path)

            if os.path.isfile(s_db_tmp_file):
                with open(s_db_tmp_file) as o_f:
                    s_ret = o_f.read()
        return s_ret

    def get_msg(self, s_instance, s_database=''):
        import datetime
        s_msg = ''
        s_msg = s_msg + '#' * 50 + '\n'
        s_msg = s_msg + '#' + ('HOSTNAME : %s' % (self.o_common.s_host_name)).ljust(48) + '#\n'
        s_msg = s_msg + '#' + ('DATABASE : DB2').ljust(48) + '#\n'
        s_msg = s_msg + '#' + ('INSTANCE : %s' % (s_instance)).ljust(48) + '#\n'
        s_msg = s_msg + '#' + ('DATE     : %s' % datetime.datetime.now()).ljust(48) + '#\n'
        s_msg = s_msg + '#' * 50 + '\n'
        return s_msg

    def main(self, a_save_type):
        self.o_common.screenshot(self.o_common.get_cmd_title_msg('Tablespace info'), a_save_type=a_save_type)
        for s_user in self.get_user_list():
            a_instance_list = self.make_init_sh(s_user)
            for a_inst_dic in a_instance_list:
                s_instance = a_inst_dic['instance']
                s_db = a_inst_dic['dbname']
                self.o_common.screenshot(self.get_msg(s_instance, s_db), a_save_type=a_save_type)
                self.o_common.screenshot(self.make_DB2_sh(s_instance, s_db), a_save_type=a_save_type)
