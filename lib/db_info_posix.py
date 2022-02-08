#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2016.08.19
    @author: jhbae
'''
from . import common
import os
import stat
import subprocess


class DbInfoPosix():
    def __init__(self, s_arg):
        self.o_common = common.Common()
        self.s_arg = s_arg
        self.b_end_flag = False

    def informix_cnt(self):
        s_ret = subprocess.getoutput('ps -ef | grep informix | grep -v grep | grep oninit')
        a_tmp_list = []
        for i in s_ret.splitlines():
            tmp = i.split()
            if len(tmp) > 1:
                s_uname = tmp[0]
                s_psname = tmp[-1]
                if s_psname not in a_tmp_list:
                    a_tmp_list.append(s_psname)

        return len(a_tmp_list)

    def get_proc_check(self, s_process_name):
        if s_process_name.lower() == 'informix':
            return self.informix_cnt()
        elif s_process_name.lower() == 'db2sysc':
            # return self.o_common.get_execute("ps -ef | grep %s | grep -v grep | awk '{print $1}' | sort -u | wc -l" % (s_process_name))
            return subprocess.getoutput("ps -ef | grep %s | grep -v grep | awk '{print $1}' | sort -u | wc -l" % (s_process_name))
        elif s_process_name.lower() == 'tbsvr':
            return subprocess.getoutput("ps -ef | grep %s | grep -v grep | awk '{print $NF}' | sort -u | wc -l" % (s_process_name))
        elif s_process_name:
            return subprocess.getoutput('ps -ef | grep %s | grep -v grep | wc -l' % (s_process_name))

    def db_cnt(self):
        a_proc_name = self.o_common.cfg_parse_read('dbms.cfg', 'DBMS_POSIX_PROCESS')
        a_cnt = {}
        if len(a_proc_name) > 0:
            for s_proc_key in a_proc_name:
                s_process_name = self.o_common.cfg_parse_read('dbms.cfg', 'DBMS_POSIX_PROCESS',s_proc_key)
                a_cnt[s_proc_key.upper()] = self.get_proc_check(s_process_name.strip())
            # for s_proc_key, s_process_name in a_proc_name:
            #     a_cnt[s_proc_key.upper()] = self.get_proc_check(s_process_name.strip())
        return a_cnt

    def check_query(self, a_db_cnt):
        s_dbms_info = ''
        s_dr_type_check = ''
        s_dr_type = self.o_common.cfg_parse_read('fleta.cfg', 'systeminfo', 'set_device').lower().strip()

        if s_dr_type.lower() in ('fs', 'vt'):
            s_dr_type_check = 'db'
        else:
            s_dr_type_check = s_dr_type

        for s_db_name, i_cnt in a_db_cnt.items():
            s_dbms_info += "%s : %s\n" % (s_db_name, i_cnt)

        a_save_type = {
            'file_name' : s_dr_type_check + '_' + self.o_common.s_host_name + '.tmp'
           , 'check_type' : 'dbinfo'
           , 'execute_type' : self.s_arg
        }

        self.o_common.screenshot(self.o_common.get_agent_head_msg(), a_save_type=a_save_type, b_start=True)
        self.o_common.screenshot(self.o_common.get_cmd_title_msg('DBMS'), a_save_type=a_save_type)
        self.o_common.screenshot(s_dbms_info, a_save_type=a_save_type)

        for s_dbms in a_db_cnt :

            if (s_dbms == 'ORACLE') and int(a_db_cnt['ORACLE']) > 0:
                print('ORACLE START :::::::')
                from . import db_info_oracle_posix
                o_main = db_info_oracle_posix.DbInfoOraclePosix()
                o_main.main(a_save_type)


            elif (s_dbms == 'DB2') and int(a_db_cnt['DB2']) > 0:

                from . import db_info_udb_posix
                o_main = db_info_udb_posix.DbInfoUdbPosix()
                o_main.main(a_save_type)

            elif (s_dbms == 'INFORMIX') and int(a_db_cnt['INFORMIX']) > 0:
                from . import db_info_informix_posix
                o_main = db_info_informix_posix.DbInfoInformixPosix()
                o_main.main(a_save_type)

            elif (s_dbms == 'ALTIBASE') and int(a_db_cnt['ALTIBASE']) > 0:
                from . import db_info_altibase_posix
                o_main = db_info_altibase_posix.DbInfoAltibasePosix()
                o_main.main(a_save_type)

            elif (s_dbms == 'TIBERO') and int(a_db_cnt['TIBERO']) > 0:
                from . import db_info_tibero_posix
                o_main = db_info_tibero_posix.DbInfoTiberoPosix()
                o_main.main(a_save_type)

            """
            elif s_dbms == 'SYBASE' and int(a_db_cnt['SYBASE']) > 0:
                import db_info_sybase_posix
                o_main = db_info_sybase_posix.DbInfoSybasePosix()
                o_main.main(a_save_type)
            """
        self.o_common.screenshot(self.o_common.get_agent_tail_msg(), a_save_type=a_save_type)

    def main(self):
        a_db_cnt = self.db_cnt()
        b_check_flag = False
        s_oct_perm = ''

        for i_cnt in list(a_db_cnt.values()):

            if int(i_cnt) > 0:
                s_file_check = os.path.join(self.o_common.s_tmp_path, 'dbcheck')

                # try:
                if os.path.isfile(s_file_check) == False:
                    open(s_file_check, 'w').close()

                o_st = os.stat(s_file_check)

                s_oct_perm = oct(o_st.st_mode)
                if int(s_oct_perm[-1]) > 3:  # read permission check
                    b_check_flag = True
                # except:
                #     pass
                # finally:
                #     if os.path.isfile(s_file_check):
                #         os.remove(s_file_check)

                if b_check_flag is True:
                    self.check_query(a_db_cnt)
                    self.b_end_flag = True
                else:
                    print("#"*100)
                    print("  * ERROR : Check the file permissions.")
                    if s_oct_perm != '':
                        print("Check the file create permissions : %s" % s_oct_perm[-3])
                    print("#"*100)
                break
        return self.b_end_flag
