#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2016.09.26
    @author: jhbae
'''

import sys
import os
import configparser
import re
import socket
import time
from lib.common import Common


class AgentConfigGen():
    def __init__(self):
        self.o_common = Common()
        self.s_aes_cipher = self.o_common.s_aes_cipher
        self.s_fleta_cfg = os.getcwd() + '/config/fleta.cfg'

        if os.path.isfile(self.s_fleta_cfg):
            self.o_config = configparser.RawConfigParser()
            self.o_config.optionxform = str
            self.o_config.read(self.s_fleta_cfg)

    def screen_clear(self, b_head=True):
        os.system('cls' if os.name == 'nt' else 'clear')

        if b_head:
            print()
            self.o_common.get_head_msg('FLETA AGENT CONFIG GENERATOR')

    def is_valid_ip(self, s_ip):
        m = re.match(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$", s_ip)
        return bool(m) and all(map(lambda n: 0 <= int(n) <= 255, m.groups()))

    def set_agent_ip(self):
        i_is_valid = 0
        s_agent_ip = ''
        i_agent_port = ''
        a_ip = {}
        s_agent_custom_ip = ''
        a_agent_info = {'ip': '', 'port': ''}

        for a_sock in socket.getaddrinfo(socket.gethostname(), None):
            s_ip = a_sock[4][0]
            if self.is_valid_ip(s_ip):
                a_ip[s_ip] = ''
        a_ip_list = a_ip.keys()
        i_ip_list_cnt = len(a_ip_list) + 1

        if len(a_ip_list) > 0:
            sys.stdout.write('Enter Your Choice AGENT IP \n')
            while not i_is_valid:
                try:

                    if s_agent_ip == '':
                        for i in range(len(a_ip_list)):
                            sys.stdout.write('%s) %s\n' % (i + 1, a_ip_list[i]))
                        print(str(i_ip_list_cnt) + ") Not Match IP")

                        i_choice = int(raw_input('Enter Your Choice [1-' + str(i_ip_list_cnt) + '] : '))
                        if i_choice == i_ip_list_cnt:
                            s_agent_custom_ip = raw_input('Agent IP : ')

                            if self.is_valid_ip(s_agent_custom_ip):
                                s_agent_ip = s_agent_custom_ip
                        else:
                            if i_choice > i_ip_list_cnt:
                                print("Invalid number. Try again...")
                                time.sleep(1)
                            else:
                                s_agent_ip = a_ip_list[int(i_choice) - 1]
                    else:
                        i_agent_port = input('Agent Daemon Port (Default : 54001) : ')
                        if i_agent_port == '':
                            i_agent_port = '54001'

                        print()
                        i_agent_port
                        if re.match("^[0-9]{1,5}$", i_agent_port):
                            if s_agent_ip != '' or i_agent_port != '':
                                i_is_valid = 1
                        else:
                            print()
                            "ERROR : Try Again Agent Daemon Port Number"
                            i_agent_port = ''
                            time.sleep(1)
                except ValueError as e:
                    print("Invalid number. Try again...")
                    time.sleep(1)
        a_agent_info['ip'] = s_agent_ip
        a_agent_info['port'] = i_agent_port
        return a_agent_info

    def set_disk_info_wmi(self):
        i_is_valid = 0
        s_set_wmi = ''

        while not i_is_valid:
            self.screen_clear()

            if s_set_wmi == '':
                print('IS THIS DISK CHECK TYPE WMI OR DISKPART ?')
                print('1) DEFAULT = WMI , 2)DISKPART = DISKPART')
                s_set_wmi_tmp = input('Enter Your Choice (SELECT NUMBER or CHARACTER) : ')
                s_set_wmi_tmp = str(s_set_wmi_tmp).upper()

                if s_set_wmi_tmp in ('1', 'WMI'):
                    s_set_wmi = 'wmi'
                elif s_set_wmi_tmp in ('2', 'DISKPART'):
                    s_set_wmi = 'diskpart'

            if s_set_wmi != '':
                i_is_valid = 1

        return s_set_wmi

    def set_disk_info_device(self):
        i_is_valid = 0
        s_set_device = ''
        while not i_is_valid:
            self.screen_clear()
            if s_set_device == '':
                print()
                'IS THIS DR OR VIRTUAL SYSTEM ?'
                print()
                '1) DEFAULT = FS, 2) DR = DR, 3) VIRTUAL = VT, 4) DR VIRTUAL = VT_DR'
                s_set_device_tmp = input('Enter Your Choice (SELECT NUMBER or CHARACTER Default : FS) : ')
                s_set_device_tmp = str(s_set_device_tmp).upper()

                if s_set_device_tmp in ('1', 'FS'):
                    s_set_device = 'FS'
                elif s_set_device_tmp in ('2', 'DR'):
                    s_set_device = 'DR'
                elif s_set_device_tmp in ('3', 'VT'):
                    s_set_device = 'VT'
                elif s_set_device_tmp in ('4', 'VT_DR'):
                    s_set_device = 'VD'
                else:
                    s_set_device = 'FS'

            if s_set_device != '':
                i_is_valid = 1

        return s_set_device

    def set_srm_ip(self):
        i_is_valid = 0
        s_srm_ip = ''
        a_srm_info = {'ip': '', 'port': ''}

        while not i_is_valid:
            self.screen_clear()
            if s_srm_ip == '':
                s_srm_ip = input('SRM SERVER IP : ')

            if self.is_valid_ip(s_srm_ip) == False:
                print()
                "ERROR : Try Again SRM SERVER IP"
                s_srm_ip = ''
                time.sleep(1)
            else:
                i_srm_port = input('SRM SERVER WAS Port (Default : 80) : ')

                if i_srm_port.strip() == '':
                    i_srm_port = '80'

                if re.match("^[0-9]{1,5}$", i_srm_port):
                    if s_srm_ip != '' or i_srm_port != '':
                        i_is_valid = 1
                else:
                    print()
                    "ERROR : Try Again SERVER SERVER WAS Port Number"
                    i_srm_port = ''
                    time.sleep(1)

        a_srm_info['ip'] = s_srm_ip
        a_srm_info['port'] = str(i_srm_port)

        print()
        a_srm_info
        return a_srm_info

    def set_transfer_conn(self, s_transfer, s_srm_ip_val=''):
        i_is_valid = 0
        s_trans_ip = ''
        i_trans_port = ''
        a_trans_con = {'ip': '', 'port': ''}

        if s_srm_ip_val != '':
            s_trans_ip = s_srm_ip_val

        b_port = True
        while not i_is_valid:
            self.screen_clear()

            if s_trans_ip == '':
                s_trans_ip = input('Transfer Connection ip : ')

            if self.is_valid_ip(s_trans_ip) == False:
                print()
                "ERROR : Try Again Transfer Connection IP"
                time.sleep(1)
                s_trans_ip = input('Transfer Connection ip : ')
            else:
                if b_port:
                    if s_transfer.lower() == 'socket':
                        i_trans_port_tmp = '54002'
                    else:
                        i_trans_port_tmp = '21'
                i_trans_port = input('Transfer Connection port Default(%s): ' % i_trans_port_tmp)

                if i_trans_port.strip() == '':
                    i_trans_port = i_trans_port_tmp

                if re.match("^[0-9]{1,5}$", i_trans_port):
                    i_is_valid = 1
                else:
                    print("ERROR : Try Again Transfer Connection Port Number")
                    i_trans_port = ''
                    b_port = False
                    time.sleep(1)

        a_trans_con['ip'] = s_trans_ip
        a_trans_con['port'] = str(i_trans_port)

        return a_trans_con

    def set_transfer(self):
        i_is_valid = 0
        a_transfer = {1: 'SOCKET', 2: 'FTP'}
        while not i_is_valid:
            self.screen_clear()

            sys.stdout.write('Enter Your Choice Transfer Type \n')
            for i_key, s_trans_type in a_transfer.iteritems():
                sys.stdout.write('%s) %s\n' % (i_key, s_trans_type))
            try:
                i_choice = int(input('Enter Your Choice [1-2] : '))
                if i_choice > 2:
                    print("Invalid number. Try again...")
                    time.sleep(1)
                else:
                    i_is_valid = 1
            except ValueError as e:
                print("%s is not a valid integer." % e.args[0].split(": ")[1])
                time.sleep(1)

        return a_transfer[i_choice]

    def cfg_view(self):
        self.screen_clear(b_head=False)
        print(self.o_common.get_head_msg('VIEW CONFIG'))

        print("AGENT HOME DIR".ljust(22) + " : " + self.o_config.get('COMMON', 'home_dir'))
        print("AGENT INFO")
        print(" - ip ".ljust(22) + " : " + self.o_config.get('COMMON', 'agent_ip'))
        print(" - port ".ljust(22) + " : " + self.o_config.get('COMMON', 'agent_port'))
        print("SRM SERVER INFO")
        print(" - ip ".ljust(22) + " : " + self.o_config.get('srm', 'srm_ip'))
        print(" - port ".ljust(22) + " : " + self.o_config.get('srm', 'srm_port'))

        s_transfer_type = self.o_config.get('COMMON', 'transfer')
        print("TRANSFER CONN INFO")
        print(" - type ".ljust(22) + " : " + s_transfer_type.upper())
        print(" - ip".ljust(22) + " : " + self.o_config.get(s_transfer_type.lower(), 'server'))
        print(" - port".ljust(22) + " : " + self.o_config.get(s_transfer_type.lower(), 'port'))

        print("SYSTEM DEVICE TYPE".ljust(22) + " : " + self.o_config.get('systeminfo', 'set_device'))

        if os.name == 'nt':
            print()
            "SYSTEM DISK CHECK TYPE".ljust(22) + " : " + self.o_config.get('systeminfo', 'diskcheck')

    def agent_main(self):
        i_is_valid = 0

        while not i_is_valid:
            self.screen_clear()

            s_home_dir = os.getcwd()
            self.o_config.set('COMMON', 'home_dir', s_home_dir)

            a_agent_info = self.set_agent_ip()
            s_agent_ip = a_agent_info['ip']
            s_agent_port = a_agent_info['port']

            self.o_config.set('COMMON', 'agent_ip', s_agent_ip)
            self.o_config.set('COMMON', 'agent_port', s_agent_port)

            a_srm_info = self.set_srm_ip()
            s_srm_ip = a_srm_info['ip']
            s_srm_port = a_srm_info['port']
            self.o_config.set('srm', 'srm_ip', s_srm_ip)
            self.o_config.set('srm', 'srm_port', s_srm_port)

            s_transfer = self.set_transfer()
            self.o_config.set('COMMON', 'transfer', s_transfer)

            if s_srm_ip.strip() != '':
                a_trans_info = self.set_transfer_conn(s_transfer, s_srm_ip)
            else:
                a_trans_info = self.set_transfer_conn(s_transfer)

            if s_transfer == 'SOCKET':
                s_trans_section = 'socket'
            elif s_transfer == 'FTP':
                s_trans_section = 'ftp'

            self.o_config.set(s_trans_section, 'server', a_trans_info['ip'])
            self.o_config.set(s_trans_section, 'port', a_trans_info['port'])

            s_disk_info_device = self.set_disk_info_device()
            self.o_config.set('systeminfo', 'set_device', s_disk_info_device)
            """
            if os.name == 'nt':
                s_set_disk_info_wmi = self.set_disk_info_wmi()
                self.o_config.set('systeminfo','diskcheck', s_set_disk_info_wmi)
            """
            with open(self.s_fleta_cfg, 'wb') as configfile:
                self.o_config.write(configfile)

            self.cfg_view()
            print("#" * 37)
            print("  Fleta Agent Config Setup Complete")
            print("#" * 37)
            input('\nPressed Enter key........')
            i_is_valid = 1


if __name__ == '__main__':
    try:
        AgentConfigGen().agent_main()
    except KeyboardInterrupt:
        print()
        "EXCEPT"
        pass
    finally:
        sys.exit(1)
