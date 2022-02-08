#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2016.08.01
    @author: jhbae
'''

import os
import re
import wmi
import time
import platform
import sys
import win32api

from .common import Common
# from drive_info_win32 import DriveInfoWin32
from .disk_info_ven_win32 import DiskInfoVenWin32
# from disk_free_win32 import DiskFreeWin32
# from disk_part_win32 import DiskPartWin32
from .log_control import LogControl

DISK_INFO_FILE = 'disk_info_win32.cfg'
DISK_VENDOR_FILE = 'vendor\windows.WMI.cfg'

class DiskInfoWin32():
    def __init__(self, s_arg):
        if sys.platform != "win32":
            print('WIndows Platform Only.')
            sys.exit(1)

        self.s_arg = s_arg
        self.o_common = Common()
        self.log_control = LogControl()
        # self.o_disk_part_win32 = DiskPartWin32()
        self.o_wmi = wmi.GetObject(r"winmgmts:\root\cimv2")
        self.a_cnt_dict = {}
        self.s_dr_type_check = ''

        self.a_disk_flag_include = self.o_common.cfg_parse_read(DISK_VENDOR_FILE, 'INCLUDE')
        self.a_disk_flag_array = self.a_disk_flag_include

    def options(self, s_item):
        a_options_dict = {
                        "Disk Flag" : self.disk_flag
                        , "version" : self.version
                        , "ip info" : self.ipinfo
                        , "Disk Drive Info" : self.drive_info
                        , "diskinfo_ven" : self.diskinfo_ven
                        , "Disk Volume info A" : self.disk_volume_A
                        , "Disk Volume info B" : self.disk_volume_B
                        , "inq -hba" : self.inq_hba

                    }
        return a_options_dict[s_item]()

    def drv_set(self):
        a_drv = win32api.GetLogicalDriveStrings().split("\x00")

        for i in a_drv:
            if i == '':
                a_drv.remove(i)
        return a_drv

    def disk_flag(self):
        a_execute_items = self.o_common.cfg_parse_read(DISK_INFO_FILE, 'disk_flag')
        s_return_disk_flag = ''

        for s_flag, s_vendor in a_execute_items:
            if s_vendor:
                s_where = ''
                if s_vendor in self.a_disk_flag_array:
                    if len(self.a_disk_flag_array[s_vendor]) > 0:
                        s_where = ' ' + self.o_common.s_aes_cipher.decrypt(self.a_disk_flag_array[s_flag])
                s_vendor_tmp = 'VEN_' + s_vendor

            if '32bit' == platform.architecture()[0]:
                if 'SerialNumber' in s_where:
                    s_where = ''

            if s_flag == 'CLOUD':
                i_disk_vendor = len(self.o_wmi.Execquery("SELECT PNPDeviceID FROM WIn32_DiskDrive where Caption ='%s'" % (s_vendor)))
            else:
                i_disk_vendor = len(self.o_wmi.Execquery("SELECT PNPDeviceID FROM WIn32_DiskDrive where PNPDeviceID like '%" + s_vendor_tmp + "%'" + s_where))

            self.a_cnt_dict[s_flag] = i_disk_vendor

        for s_key , s_value in self.a_cnt_dict.items():
            s_return_disk_flag += "%s : %s\n" % (s_key, s_value)

        return s_return_disk_flag.strip()

    """
    def diskpart_disk(self):
        s_rtn = self.o_disk_part_win32.diskpart_check()
        return unicode(s_rtn,'cp949')

    def diskpart_vol(self):
        s_rtn = self.o_disk_part_win32.diskvol_check()
        return unicode(s_rtn,'cp949')

    def diskfree(self):
        o_disk_free_win32 = DiskFreeWin32()
        s_disk_free = o_disk_free_win32.disk_free()
        return s_disk_free
    """
    def version(self):
        s_version_cmd = "wmic os get Caption,CSDVersion /value"
        return self.o_common.get_execute(s_version_cmd).strip()

    def ipinfo(self):
        a_rtn_query = self.o_wmi.ExecQuery("SELECT IPAddress from Win32_NetworkAdapterConfiguration WHERE IPEnabled = 'True'")
        a_ip = []
        for o_rtn in a_rtn_query:
            a_ip.append('ip_addr = ' + o_rtn.IpAddress[0])
        s_rtn = '\n'.join(a_ip)
        return s_rtn

    """
    def fcinfo(self):
        s_version_cmd = "fcinfo"
        return self.o_common.get_execute(s_version_cmd)


    def drive_info(self): # 미사용
        self.o_drive_info_win32 = DriveInfoWin32()
        a_rtn = self.o_drive_info_win32.drv_info()

        if isinstance(a_rtn, list) and len(a_rtn) > 0:
            return "\n".join(a_rtn)
        else:
            return ''

    def fsutil(self):
        s_msg = ''
        for i in self.drv_set():
            if '\\' in i:
                i=i.replace('\\','')
            s_cmd='fsutil volume diskfree %s'%i
            s_msg = s_msg + s_cmd + '\n'
            try:
                s_execute = self.o_common.get_execute(s_cmd)
            except:
                s_execute = 'fsutil error'
            s_msg = s_msg + s_execute + '\n\n'
        return unicode(s_msg,'cp949').strip()
    """

    def drive_info(self):
        s_drive_info = "wmic diskdrive get"
        # s_drive_info = "wmic path Win32_PnPEntity where \"PNPDeviceID like '%VEN%' AND service='disk'\" get"
        return self.o_common.get_execute(s_drive_info).strip()

    def disk_volume_A(self):
        s_disk_volume_a = "inqraid $LETALL -CLI"
        return self.o_common.get_execute(s_disk_volume_a).strip()
        pass

    def disk_volume_B(self):
        s_disk_volume_b = "wmic volume list"
        return self.o_common.get_execute(s_disk_volume_b).strip()

    def diskinfo_ven(self):

        if self.s_dr_type_check.lower() in ('vt', 'vd'):
            self.a_cnt_dict['VT'] = 1

        o_disk_info_ven_win32 = DiskInfoVenWin32(self.a_cnt_dict)

        return o_disk_info_ven_win32.execute()

    def inq_hba(self):
        s_inq_hba = "inq -hba"
        return self.o_common.get_execute(s_inq_hba).strip()

    def main(self):
        s_dr_type = self.o_common.cfg_parse_read('fleta.cfg', 'systeminfo', 'set_device').lower().strip()

        self.s_dr_type_check = s_dr_type
        a_save_type = {
                        'file_name' : s_dr_type + '_' + self.o_common.s_host_name + '.tmp'
                       , 'check_type' : 'diskinfo'
                       , 'execute_type' : self.s_arg
                    }

        a_execute_items = self.o_common.cfg_parse_read(DISK_INFO_FILE, 'diskinfo')
        self.o_common.screenshot(self.o_common.get_agent_head_msg(), a_save_type=a_save_type, b_start=True)
        self.o_common.screenshot(self.o_common.get_agent_default_msg(), a_save_type=a_save_type)

        for s_execute_cmd_name, s_flag in a_execute_items:
            if s_flag.strip() == 'T':
                if s_execute_cmd_name != 'diskinfo_ven':
                    self.o_common.screenshot(self.o_common.get_cmd_title_msg(s_execute_cmd_name), a_save_type=a_save_type)
                print(':::disk_info_win32')
                self.o_common.screenshot(self.options(s_execute_cmd_name), a_save_type=a_save_type)
                print('---disk_info_win32')
        self.o_common.screenshot(self.o_common.get_agent_tail_msg(), a_save_type=a_save_type)
        return True
