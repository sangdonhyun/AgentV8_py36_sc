#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2016.07.29
    @author: jhbae
'''
import sys
import os
import time
import socket
import re
from subprocess import Popen, PIPE
from cgi import log

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0]))))
from lib.common import Common
from lib.file_transfer import FileTransfer
from lib.log_control import LogControl
from version_check import VersionCheck
from lib.decode import Decode

# EMC Clone All Platform
from lib.emc_clone import EmcClone

if sys.platform == 'win32':
    from lib.disk_info_win32 import DiskInfoWin32
    from lib.db_info_win32 import DbInfoWin32
else:
    from lib.disk_info_posix import DiskInfoPosix
    from lib.db_info_posix import DbInfoPosix


class Fleta():
    def __init__(self):
        self.o_common = Common()
        self.log_control = LogControl()
        self.exec_path()
        self.s_execute_file = os.path.basename(os.path.abspath(sys.argv[0]))
        self.o_file_transfer = FileTransfer()

    def proc_check(self):
        if sys.platform == 'win32':  # Windows
            process = Popen(
                            'tasklist.exe /FO CSV /FI "IMAGENAME eq %s" /NH' % self.s_execute_file,
                            stdout=PIPE, stderr=PIPE,
                            universal_newlines=True)
            out, err = process.communicate()
        try :
            a_cnt = out.strip().split("\n")
            if len(a_cnt) > 1 :
                return True
            else :
                return False
        except :
            return False

    def exec_path(self):
        if sys.platform == "win32":
            s_custom_path = 'windows_custom_path'
        else:
            s_custom_path = 'posix_custom_path'

        # a_path = self.o_common.tuple_to_dict(self.o_common.cfg_parse_read('custom_path.cfg', s_custom_path))
        #py36 add
        a_path = self.o_common.cfg_parse_read('custom_path.cfg', s_custom_path)
        print(a_path,type(a_path))
        print(len(a_path))
        s_custom_exec_dir = ''
        s_path = ''
        if sys.platform == "win32":

            import ntpath
            s_custom_exec_dir = ntpath.abspath(self.o_common.s_agent_path) + '\scripts'
            if len(a_path) > 0:
                s_path = ';'.join(list(a_path.values())) + ';'
                s_custom_exec_dir = s_path + s_custom_exec_dir
        else:
            import platform
            s_custom_exec_dir = os.path.abspath(self.o_common.s_agent_path) + '/scripts/' + platform.system()
            print('s_custom_exec_dir :',s_custom_exec_dir)
            print(a_path)
            if os.path.isdir(s_custom_exec_dir) > 0:
                s_path = s_custom_exec_dir+':'+os.environ['PATH']
                os.environ['PATH'] = s_path
                # s_path = ':'.join(list(a_path.values())) + ':'
                # s_custom_exec_dir = s_path + s_custom_exec_dir
        try:
            if sys.platform == "win32":
                os.environ['PATH'] = ';'.join([s_custom_exec_dir, os.getenv('PATH')])
            else:
                os.environ['PATH'] = ':'.join([s_custom_exec_dir, os.getenv('PATH')])

        except Exception as e:
            self.log_control.logdata('AGENT', 'ERROR', '30010', str(e))

    def __win32__(self, s_execute_type):
        self.log_control.logdata('AGENT', 'ERROR', '30010', str('diskinfo excuting'))
        b_proc_check = self.proc_check()
        if b_proc_check:
            print("Already Process - %s" % self.s_execute_file)
            sys.exit(1)

        a_res = {
                  'diskinfo.' + s_execute_type : False
                 , 'dbinfo.' + s_execute_type : False
                 , 'EMC.CLONE' : False
              }
        #a_cfg_parse = self.o_common.tuple_to_dict(self.o_common.cfg_parse_read('disk_info_win32.cfg', 'check'))
        a_cfg_parse = self.o_common.cfg_parse_read('disk_info_win32.cfg', 'check')

        if a_cfg_parse['diskinfo'] == 'T':
            print('#' * 40)
            print('DISK INFO CHECK')
            print('#' * 40)
            self.log_control.logdata('AGENT', 'ACCESS', '30001')
            o_disk_info = DiskInfoWin32(s_execute_type)
            a_res['diskinfo.' + s_execute_type] = o_disk_info.main()
            self.log_control.logdata('AGENT', 'ACCESS', '30002')

        if a_cfg_parse['dbinfo'] == 'T':
            print('#' * 40)
            print('DB INFO CHECK')
            print('#' * 40)
            self.log_control.logdata('AGENT', 'ACCESS', '30003')
            o_db_info = DbInfoWin32(s_execute_type)
            a_res['dbinfo.' + s_execute_type] = o_db_info.main()
            self.log_control.logdata('AGENT', 'ACCESS', '30004')

        if a_cfg_parse['EMC.CLONE'] == 'T':
            print('#' * 40)
            print('EMC SYM MODULE CHECK')
            print('#' * 40)
            self.log_control.logdata('AGENT', 'ACCESS', '30005')
            o_emc_clone = EmcClone()
            a_res['EMC.CLONE'] = o_emc_clone.emc_clone()
            self.log_control.logdata('AGENT', 'ACCESS', '30006')

        return a_res

    def __posix__(self, s_execute_type):

        a_res = {
                  'diskinfo.' + s_execute_type : False
                 , 'dbinfo.' + s_execute_type : False
                 , 'EMC.CLONE' : False
              }

        # a_cfg_parse = self.o_common.tuple_to_dict(self.o_common.cfg_parse_read('disk_info_posix.cfg', 'check'))
        a_cfg_parse = self.o_common.cfg_parse_read('disk_info_posix.cfg', 'check')
        print('a_cfg_parse :',a_cfg_parse)
        if a_cfg_parse['diskinfo'] == 'T':
            print('#' * 40)
            print('DISK INFO CHECK')
            print('#' * 40)
            self.log_control.logdata('AGENT', 'ACCESS', '30001')
            o_disk_info = DiskInfoPosix(s_execute_type)
            a_res['diskinfo.' + s_execute_type] = o_disk_info.main()
            self.log_control.logdata('AGENT', 'ACCESS', '30002')

        if a_cfg_parse['dbinfo'] == 'T':
            print('#' * 40)
            print('DB INFO CHECK')
            print('#' * 40)
            self.log_control.logdata('AGENT', 'ACCESS', '30003')
            o_db_info = DbInfoPosix(s_execute_type)
            print('!' * 50)
            print('Check point : 1')
            a_res['dbinfo.' + s_execute_type] = o_db_info.main()

            # sybase file check
            s_sybase_check = os.path.join(self.o_common.s_data_path, 'dbms_spool')
            s_extension = '*.log'
            print('!'*50)
            print('Check point : 2')
            import fnmatch
            for s_root, s_dirs, s_filenames in os.walk(s_sybase_check):
                if len(fnmatch.filter(s_filenames, s_extension)) > 0:
                    a_res['dbinfo.' + s_execute_type] = True
                    break

            self.log_control.logdata('AGENT', 'ACCESS', '30004')

        if a_cfg_parse['EMC.CLONE'] == 'T':
            print('#' * 40)
            print('EMC SYM MODULE CHECK')
            print('#' * 40)
            self.log_control.logdata('AGENT', 'ACCESS', '30005')
            o_emc_clone = EmcClone()
            a_res['EMC.CLONE'] = o_emc_clone.emc_clone()
            self.log_control.logdata('AGENT', 'ACCESS', '30006')

        return a_res

    def end_msg(self, b_status):
        if b_status:
            print('#' * 40)
            print('Diskinfo Check Success')
            print('#' * 40)
        else:
            print('#' * 40)
            print('Diskinfo Check FAIL Transfer Error')
            print('#' * 40)

    def main(self, s_execute_type):

        s_diskcheck = self.o_common.cfg_parse_read('fleta_config.cfg', 'diskinfo', 'diskcheck')
        print('s_diskcheck :', s_diskcheck)
        s_diskcheck = self.o_common.cfg_parse_read('fleta_config.cfg', 'diskinfo', 'diskcheck')
        print('s_diskcheck :',s_diskcheck)
        a_res = {}
        try:
            if s_diskcheck.upper().strip() == 'F' :
                print('Disk Info Check Stop!!')
                sys.exit(1)
        except Exception as e:
            print(str(e))

        if os.path.isdir(self.o_common.s_data_path):
            for dirname, dirnames, filenames in os.walk(self.o_common.s_data_path):
                for filename in filenames:
                    if filename.endswith('.tmp'):
                        os.remove(os.path.join(dirname, filename))

        i_execute_cnt = self.o_common.cfg_parse_read('fleta.cfg', 'COMMON', 'agent_execute')
        print('i_execute_cnt:',i_execute_cnt)
        if int(i_execute_cnt) > 0:
            s_now_date = time.strftime("%Y%m%d", time.localtime(time.time()))

            if os.path.isfile(os.path.join(self.o_common.s_agent_path ,'tmp','agent_check')) == False:
                self.o_common.file_write(os.path.join('tmp','agent_check') , '%s@2@0' % (s_now_date))

            s_cnt = self.o_common.file_read(os.path.join('tmp','agent_check'))

            if s_cnt != '':
                a_cnt_split = s_cnt.split('@2@')

            if s_now_date > a_cnt_split[0]:
                self.o_common.file_write('/tmp/agent_check' , '%s@2@0' % (s_now_date))
                a_cnt_split[1] = 0

            i_replace_cnt = int(a_cnt_split[1]) + 1

            if i_replace_cnt > int(i_execute_cnt):
                self.log_control.logdata('AGENT', 'ERROR', '30009', "COUNT " + str(i_execute_cnt))
                print("#"*40)
                print("[ERROR] SCRIPT EXECUTE COUNT LIMIT %s" % (str(i_execute_cnt)))
                print("#"*40)
                sys.exit(1)

            self.o_common.file_write('/tmp/agent_check', '%s@2@%s' % (s_now_date, str(i_replace_cnt)))

        if sys.platform == 'win32':
            a_res = self.__win32__(s_execute_type)
        else:
            a_res = self.__posix__(s_execute_type)

        if len(a_res) > 0:
            print('#' * 40)
            print('DATA TRANSFER START')
            print('#' * 40)
            b_rtn = self.o_file_transfer.main(a_res)
            self.end_msg(b_rtn)
        else:
            print('#' * 40)
            print('Agent Check Not Execute Module List')
            print('#' * 40)
        """
        if os.path.isdir(self.o_common.s_tmp_path):
            ##원본 파일 삭제
            for dirname, dirnames, filenames in os.walk(self.o_common.s_tmp_path):
                for filename in filenames:
                    if filename.endswith('.sql') or filename.endswith('.tmp'):
                        os.remove(os.path.join(dirname, filename))
        """
if __name__ == '__main__':
    # default argument : MAN
    try:
        args = sys.argv[:]
        dir = args[1]
    except:
        dir = 'SCH'

    VersionCheck().main()
    o_fleta = Fleta()
    o_fleta.main(dir)

