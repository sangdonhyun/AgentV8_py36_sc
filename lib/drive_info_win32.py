#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2016.08.02
    @author: jhbae
'''
import wmi

class DriveInfoWin32():
    def __init__(self):
        self.o_wmi = wmi.GetObject(r"winmgmts:\root\cimv2")

    def drvie_wmi(self):        
        a_drv_list = []
        for o_item in self.o_wmi.ExecQuery("SELECT * FROM Win32_DiskDrive"):
            a_drv_dic = {}
            a_drv_dic['BytesPerSector'] = o_item.BytesPerSector
            a_drv_dic['Capabilities'] = o_item.Capabilities
            a_drv_dic['Caption'] = o_item.Caption
            a_drv_dic['ConfigManagerErrorCode'] = o_item.ConfigManagerErrorCode
            a_drv_dic['ConfigManagerUserConfig'] = o_item.ConfigManagerUserConfig
            a_drv_dic['CreationClassName'] = o_item.CreationClassName
            a_drv_dic['Description'] = o_item.Description
            a_drv_dic['DeviceID'] = o_item.DeviceID
            a_drv_dic['Index'] = o_item.Index
            a_drv_dic['InterfaceType'] = o_item.InterfaceType
            a_drv_dic['Manufacturer'] = o_item.Manufacturer
            a_drv_dic['MediaLoaded'] = o_item.MediaLoaded
            a_drv_dic['MediaType'] = o_item.MediaType
            a_drv_dic['Model'] = o_item.Model
            a_drv_dic['Name'] = o_item.Name
            a_drv_dic['Partitions'] = o_item.Partitions
            a_drv_dic['PNPDeviceID'] = o_item.PNPDeviceID
            a_drv_dic['SCSIBus'] = o_item.SCSIBus
            a_drv_dic['SCSILogicalUnit'] = o_item.SCSILogicalUnit
            a_drv_dic['SCSIPort'] = o_item.SCSIPort
            a_drv_dic['SCSITargetId'] = o_item.SCSITargetId
            a_drv_dic['SectorsPerTrack'] = o_item.SectorsPerTrack
            a_drv_dic['Signature'] = o_item.Signature
            a_drv_dic['Size'] = o_item.Size
            a_drv_dic['Status'] = o_item.Status
            a_drv_dic['SystemCreationClassName'] = o_item.SystemCreationClassName
            a_drv_dic['SystemName'] = o_item.SystemName
            a_drv_dic['TotalCylinders'] = o_item.TotalCylinders
            a_drv_dic['TotalHeads'] = o_item.TotalHeads
            a_drv_dic['TotalSectors'] = o_item.TotalSectors
            a_drv_dic['TotalTracks'] = o_item.TotalTracks
            a_drv_dic['TracksPerCylinder'] = o_item.TracksPerCylinder
            a_drv_list.append(a_drv_dic)
        return a_drv_list

    def drv_info(self):
        a_drv_list = self.drvie_wmi()
        a_ret = []
        s_msg =''
        s_msg = s_msg+'#'*80+'\n'
        a_ret.append('#'*80)

        if len(a_drv_list) > 0:
            for i in sorted(a_drv_list):
                s_msg = s_msg + 'DRIVE NUMBER : %s\n' %i['Index']

                a_ret.append('DRIVE NUMBER : %s' %i['Index'])
                s_msg = s_msg + '-'*80+'\n'
                a_ret.append('-'*80)

                for j in list(i.keys()):
                    s_msg = s_msg + '%s : %s\n' %(j,i[j])
                    a_ret.append('%s : %s' %(j,i[j]))
                s_msg = s_msg+'#'*80+'\n'
                a_ret.append('#'*80)
            return a_ret
