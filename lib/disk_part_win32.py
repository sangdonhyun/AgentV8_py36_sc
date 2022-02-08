#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2016.08.02
    @author: jhbae
'''

import os
import wmi
import win32api
import time
import sys
from lib.common import Common
from lib.log_control import LogControl

class DiskPartWin32():
    def __init__(self):
        self.o_common = Common()
        self.s_tmp_save_dir = os.path.join(self.o_common.s_agent_path,'logs')
        self.o_wmi = wmi.GetObject(r"winmgmts:\root\cimv2")
        self.log_control = LogControl()

    def check_file(self, s_file_path):
        time.sleep(2)
        if os.path.isfile(s_file_path):
            if os.path.getsize(s_file_path) > 0:
                try:
                    o_f = open(s_file_path, 'r')
                    s_contents = o_f.read()
                    o_f.close()
                    return s_contents
                except:
                    return False
            else:
                return False
        else :
            self.log_control.logdata('AGENT', 'ERROR', '30007')
        return False

    def diskpart_execute(self, s_file):
        s_file_path = self.s_tmp_save_dir + '/' + s_file

        if os.path.isfile(s_file_path):
            o_shell = os.environ['COMSPEC']  # cmd.exe

            # Diskpart 접속 지연으로 1회 호출후 진행
            ## CMD 창이 안꺼지는 버그로 인해 수정
            #win32api.ShellExecute(0, 'runas', o_shell, 'diskpart', '', 0)
            #time.sleep(0.5)

            s_command = r'/c diskpart /s %s > %s/%s.out' %(s_file_path, self.s_tmp_save_dir, s_file)
            try :
                win32api.ShellExecute(0, 'runas', o_shell, s_command, '', 0)
            except Exception as e:
                self.log_control.logdata('AGENT', 'ERROR', '30008', str(e))
                return e
        else :
            return False

        return self.check_file(s_file_path+'.out')

    def diskvol_check(self):
        s_disk_vol_query = "SELECT Caption FROM Win32_Volume where Capacity > 0 and DriveLetter is not null"

        with open(self.s_tmp_save_dir + '/disk_vol','w') as disk_drive:
            for a_drive_name in self.o_wmi.ExecQuery(s_disk_vol_query):
                s_drive_name = a_drive_name.Caption.replace(':\\','')
                disk_drive.write('SELECT VOL=%s\n' %(s_drive_name))
                disk_drive.write('DETAIL VOL\n')

        s_rtn = self.diskpart_execute('disk_vol')
        if isinstance(s_rtn , bool):
            s_rtn = 'ERROR'
        return s_rtn        

    def diskpart_check(self):
        a_disk_drive = self.o_wmi.ExecQuery("SELECT * FROM Win32_DiskDrive")
        i_disk_drive = len(a_disk_drive) 

        with open(self.s_tmp_save_dir + '/disk_num','w') as disk_num:
            for i_disk_cnt in range(0, i_disk_drive):
                disk_num.write('SELECT DISK=%s\n' %(i_disk_cnt))
                disk_num.write('DETAIL DISK\n')

        s_rtn = self.diskpart_execute('disk_num')
        if isinstance(s_rtn , bool):
            s_rtn = 'ERROR'
        return s_rtn

