#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2016.08.03
    @author: jhbae
'''
import wmi
import os

class DiskFreeWin32():
    def __init__(self):
        self.s_sys_ver = os.getenv('OS')

    def disk_free(self):
        o_wmi = wmi.GetObject(r"winmgmts:\root\cimv2")
        s_w_sql = "SELECT SystemName, DeviceID, VolumeSerialNumber, Size, FreeSpace FROM Win32_LogicalDisk WHERE Size > 0"
        a_return = []
        for a_instance_disk_info in o_wmi.ExecQuery(s_w_sql):
            s_system_name = a_instance_disk_info.SystemName
            s_device_id = a_instance_disk_info.DeviceID.replace(":","")
            s_volume_serial = a_instance_disk_info.VolumeSerialNumber
            s_device_size = a_instance_disk_info.Size
            s_device_space = a_instance_disk_info.FreeSpace

            a_return.append('%s,%s,%s,%s,%s,%s,%s,%s\n' %(s_system_name
                                                          , self.s_sys_ver
                                                          , ''
                                                          , ''
                                                          ,s_device_id
                                                          ,s_volume_serial
                                                          ,s_device_size
                                                          ,s_device_space)
                            )

        return "".join(a_return).strip()
