#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2016.08.02
    @author: jhbae
'''

from . import common
import os
import sys
import re
import wmi
from .tabulate import tabulate


class DiskInfoVenWin32():
    def __init__(self, a_cnt_dict):

        self.a_cnt_dict = a_cnt_dict
        self.o_common = common.Common()
        self.s_aescipher = self.o_common.s_aes_cipher
        if sys.platform == "win32":
            import ntpath
            s_custom_exec_dir = ntpath.abspath(self.o_common.s_agent_path) + '\scripts'
            os.environ['PATH'] = ';'.join([s_custom_exec_dir, os.getenv('PATH')])

        s_check_type = self.o_common.cfg_parse_read('fleta.cfg', 'systeminfo', 'diskcheck')

        if s_check_type.upper() == 'WMI':
            s_ven_config_file = 'vendor/windows.WMI.cfg'
        else:
            s_ven_config_file = 'vendor/windows.cfg'

        self.s_ven_config_file = s_ven_config_file

    def pshell(self, s_pool_name):
        s_out = self.o_common.get_execute('powershell.exe  "get-storagepool -FriendlyName %s|get-physicaldisk"' % (s_pool_name))

        a_out = s_out.strip().split("\n")
        a_res = []
        for s_out_split in a_out:
            if s_out_split.startswith('FriendlyName'):
                continue
            elif s_out_split.startswith('----'):
                continue
            elif len(s_out_split) < 1:
                continue
            elif re.match("^[^a-zA-Z]", s_out_split):
                continue
            else:
                a_out_val = s_out_split.split()
                a_res.append(a_out_val[0])

        if len(a_res) > 0:
            s_res = ",".join(a_res)
        return s_res

    def storage_pool(self):
        o_wmi = wmi.GetObject(r"winmgmts:\root\Microsoft\Windows\Storage")
        a = o_wmi.Execquery("SELECT AllocatedSize, FriendlyName,  LogicalSectorSize, Name, PhysicalSectorSize, Size, Usage FROM MSFT_StoragePool WHERE isPrimordial = False")
        b_title = False

        a_1 = o_wmi.Execquery('select serialnumber  from MSFT_DISK where Model="Storage space"')

        a_virtual = {}
        for b in a_1:
            c_1 = o_wmi.ExecQuery("select friendlyName from  MSFT_virtualdisk where ObjectId like '%" + str(b.serialnumber) + "%'")
            for c_2 in c_1:
                a_virtual[str(c_2.friendlyName)] = str(b.serialnumber)

        a_header = []
        a_contents = []
        for o_item in a:
            a_drv_dic = {}
            a_drv_dic['AllocatedSize'] = str(o_item.AllocatedSize)
            a_drv_dic['friendlyName'] = str(o_item.friendlyName)
            a_drv_dic['LogicalSectorSize'] = str(o_item.LogicalSectorSize)
            a_drv_dic['Name'] = str(o_item.Name)
            a_drv_dic['PhysicalSectorSize'] = str(o_item.PhysicalSectorSize)
            a_drv_dic['Size'] = str(o_item.Size)
            a_drv_dic['Usage'] = str(o_item.Usage)
            a_drv_dic['PhysicalDisk'] = self.pshell(a_drv_dic['friendlyName'])
            try:
                a_drv_dic['ObjectId'] = a_virtual[a_drv_dic['friendlyName']]
            except:
                a_drv_dic['ObjectId'] = ''
            b = []
            c = []
            for a in sorted(a_drv_dic.keys()):
                b.append(a)
                c.append(str(a_drv_dic[a]))
            if b_title is False:
                a_header = b
                b_title = True
            a_contents.append(c)

        return str(tabulate(a_contents, headers=a_header))

    def get_ven_cmd(self):
        s_ven_rtn = ''
        for s_vendor, i_cnt in self.a_cnt_dict.items():
            if int(i_cnt) > 0:
                a_ven_list = self.o_common.cfg_parse_read(self.s_ven_config_file, s_vendor)
                if len(a_ven_list) > 0:
                    for s_title, s_cmd_enc in sorted(set(a_ven_list).items()):
                        s_cmd_tmp = self.o_common.s_aes_cipher.decrypt(s_cmd_enc)

                        s_cmd_tmp = s_cmd_tmp.split('^')
                        s_title = s_cmd_tmp[0].strip()
                        s_cmd = s_cmd_tmp[1].strip()
                        s_ven_rtn = s_ven_rtn + self.o_common.get_cmd_title_msg(s_title) + "\n"

                        if s_title == 'CLOUD' :
                            self.storage_pool()
                            s_ven_rtn += self.storage_pool() + "\n\n"
                            s_ven_rtn += "###***CLOUD DISK***###" + "\n"
                            s_ven_rtn += self.o_common.get_execute(s_cmd)
                        else:
                            s_ven_rtn = s_ven_rtn + self.o_common.get_execute(s_cmd) + "\n"
        return str(s_ven_rtn, 'cp949')

    def execute(self):
        return self.get_ven_cmd()
