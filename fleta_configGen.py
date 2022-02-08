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
        self.s_dbms_cfg = os.getcwd() + '/config/dbms.cfg'
        self.s_oracle_cfg = os.getcwd() + '/config/oracle.cfg'

        if os.path.isfile(self.s_fleta_cfg):
            self.o_config = configparser.RawConfigParser()
            self.o_config.optionxform = str
            self.o_config.read(self.s_fleta_cfg)

        if os.path.isfile(self.s_dbms_cfg):
            self.o_cfg_dbms = configparser.RawConfigParser()
            self.o_cfg_dbms.optionxform = str
            self.o_cfg_dbms.read(self.s_dbms_cfg)

        if os.path.isfile(self.s_oracle_cfg):
            self.o_cfg_ora = configparser.RawConfigParser()
            self.o_cfg_ora.optionxform = str
            self.o_cfg_ora.read(self.s_oracle_cfg)

        self.screen_clear()

    def screen_clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def is_valid_ip(self, s_ip):
        m = re.match(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$", s_ip)
        return bool(m) and all(map(lambda n: 0 <= int(n) <= 255, m.groups()))

    def set_agent_ip(self):
        i_is_valid = 0
        s_agent_ip = ''
        i_agent_port = ''
        a_ip = {}
        s_agent_custom_ip = ''
        a_agent_info = {'ip' : '', 'port' : ''}

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

                        i_choice = int(input('Enter Your Choice [1-' + str(i_ip_list_cnt) + '] : '))
                        if i_choice == i_ip_list_cnt:
                            s_agent_custom_ip = input('Agent IP : ')

                            if self.is_valid_ip(s_agent_custom_ip):
                                s_agent_ip = s_agent_custom_ip
                        else:
                            if i_choice > i_ip_list_cnt:
                                print ("Invalid number. Try again...")
                                time.sleep(1)
                            else:
                                s_agent_ip = a_ip_list[int(i_choice) - 1]
                    else:
                        if i_agent_port == '':
                            i_agent_port = input('Agent Daemon Port : ')

                        if re.match("^[0-9]{1,5}$", i_agent_port):
                            if s_agent_ip != '' or i_agent_port != '':
                                i_is_valid = 1
                        else:
                            print("ERROR : Try Again Agent Daemon Port Number")
                            i_agent_port = ''
                            time.sleep(1)
                except ValueError as e:
                    print ("Invalid number. Try again...")
                    time.sleep(1)
        a_agent_info['ip'] = s_agent_ip
        a_agent_info['port'] = i_agent_port
        return a_agent_info

    def set_disk_info_wmi(self):
        i_is_valid = 0
        s_set_wmi = ''

        while not i_is_valid:
            if s_set_wmi == '':
                print('IS THIS DISK CHECK TYPE WMI OR DISKPART ?')
                print('1) DEFAULT = WMI , 2)DISKPART = DISKPART')
                s_set_wmi_tmp = input('Enter Your Choice (SELECT NUMBER or CHARACTER) : ')
                s_set_wmi_tmp = str(s_set_wmi_tmp).upper()

                if s_set_wmi_tmp in ('1', 'WMI'):
                    s_set_wmi = 'wmi'

                if s_set_wmi_tmp in ('2', 'DISKPART'):
                    s_set_wmi = 'diskpart'

            if s_set_wmi != '':
                i_is_valid = 1

        return s_set_wmi

    def set_disk_info_device(self):
        i_is_valid = 0
        s_set_device = ''
        while not i_is_valid:
            if s_set_device == '':
                print('IS THIS DR OR VIRTUAL SYSTEM ?')
                print('1) DEFAULT = FS , 2) DR = DR , 3) VIRTUAL = VT, 4)DR VIRTUAL = VT_DR')
                s_set_device_tmp = input('Enter Your Choice (SELECT NUMBER or CHARACTER) : ')
                s_set_device_tmp = str(s_set_device_tmp).upper()

                if s_set_device_tmp in ('1', 'FS'):
                    s_set_device = 'FS'
                elif s_set_device_tmp in ('2', 'DR'):
                    s_set_device = 'DR'
                elif s_set_device_tmp in ('3', 'VT'):
                    s_set_device = 'VT'
                elif s_set_device_tmp in ('4', 'VT_DR'):
                    s_set_device = 'VD'

            if s_set_device != '':
                i_is_valid = 1

        return s_set_device

    def set_srm_ip(self):
        i_is_valid = 0
        s_srm_ip = ''
        i_srm_port = ''
        a_srm_info = {'ip' : '', 'port' : ''}

        while not i_is_valid:
            if s_srm_ip == '':
                s_srm_ip = input('SRM SERVER IP ADDRESS : ')

            if self.is_valid_ip(s_srm_ip) == False:
                print("ERROR : Try Again SRM SERVER IP")
                s_srm_ip = ''
                time.sleep(1)
            else:
                if i_srm_port == '':
                    i_srm_port = input('SRM SERVER WAS Port : ')

                if re.match("^[0-9]{1,5}$", i_srm_port):
                    if s_srm_ip != '' or i_srm_port != '':
                        i_is_valid = 1
                else:
                    print("ERROR : Try Again SERVER SERVER WAS Port Number")
                    i_srm_port = ''
                    time.sleep(1)
        a_srm_info['ip'] = s_srm_ip
        a_srm_info['port'] = i_srm_port
        return a_srm_info

    def set_transfer_conn(self, s_transfer , s_srm_ip_val=''):
        i_is_valid = 0
        s_trans_ip = ''
        i_trans_port = ''
        s_trans_user = ''
        s_trans_pass = ''
        a_trans_con = {'ip' : '', 'port' : '', 'user' : '' , 'pass' : ''}

        while not i_is_valid:
            if s_trans_ip == '':
                s_trans_ip = input('Transfer Connection ip : ')
            else:
                if s_srm_ip_val != '':
                    s_trans_ip = s_srm_ip_val

            if self.is_valid_ip(s_trans_ip) == False:
                print("ERROR : Try Again Transfer Connection IP")
                time.sleep(1)
                s_trans_ip = ''
            else:
                if i_trans_port == '':
                    i_trans_port = input('Transfer Connection port : ')
                    if s_transfer.lower() == 'socket':
                        i_is_valid = 1

                if re.match("^[0-9]{1,5}$", i_trans_port):
                    if s_transfer.lower() == 'ftp':
                        s_trans_user = input('FTP Connection ID : ')
                        s_trans_pass = input('FTP Connection PASSWORD : ')

                        if s_trans_user != '' or s_trans_pass != '':
                            i_is_valid = 1
                        else:
                            print("ERROR : Try Again Transfer Connection ID / Password")
                            time.sleep(1)
                else:
                    print("ERROR : Try Again Transfer Connection Port Number")
                    i_trans_port = ''
                    time.sleep(1)

        a_trans_con['ip'] = s_trans_ip
        a_trans_con['port'] = str(i_trans_port)
        a_trans_con['user'] = s_trans_user
        a_trans_con['pass'] = s_trans_pass

        return a_trans_con

    def set_transfer(self):
        i_is_valid = 0
        a_transfer = {1:'SOCKET', 2:'FTP'}
        while not i_is_valid:
            for i_key, s_trans_type in a_transfer.iteritems():
                sys.stdout.write('%s) %s\n' % (i_key, s_trans_type))
            try:
                i_choice = int(input('Enter Your Choice [1-2] : '))
                if i_choice > 2:
                    print ("Invalid number. Try again...")
                    time.sleep(1)
                else :
                    i_is_valid = 1
            except ValueError as e:
                print ("Invalid number. Try again...")
                time.sleep(1)

        return a_transfer[i_choice]

    def cfg_view(self):
        self.screen_clear()
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
            print("SYSTEM DISK CHECK TYPE".ljust(22) + " : " + self.o_config.get('systeminfo', 'diskcheck'))

        input('\nPressed Enter key........')
        self.screen_clear()

    def set_agent_path(self):
        i_is_valid = 0
        s_agent_path = ''
        while not i_is_valid:
            if s_agent_path == '':
                b_agent_path = input('AGENT Install Path (Default : %s) (Y/N) : ' % os.getcwd())

            if b_agent_path.upper() == 'Y':
                s_agent_path = os.getcwd()
                i_is_valid = 1
            elif b_agent_path.upper() == 'N':
                s_agent_path = input('AGENT PATH > ')
                b_typing_path = input('AGENT Install Path : [%s] Selected (Y/N) : ' % (s_agent_path))

                if b_typing_path.upper() == 'Y':
                    i_is_valid = 1
                else:
                    print("Try Again Agent Install Path")
                    s_agent_path = ''
                    time.sleep(1)
            if os.path.isdir(s_agent_path) is False:
                i_is_valid = 0
                b_agent_path = 'N'
                print("ERROR : Agent Install Directory is not Found.. try again Directory")
                s_agent_path = ''
                time.sleep(1)
        return s_agent_path

    def agent_main(self):
        i_is_valid = 0
        s_srm_ip = ''
        s_menu = """
1. AGENT HOME DIR
2. AGENT DAEMON INFO
3. SRM SERVER INFO
4. DATA TRANSFER CONNECTION SELECT
5. DISK INFO SYSTEM TYPE
6. VIEW CONFIG
7. SAVE CHANGE CONFIG
8. PREV MENU
"""
        while not i_is_valid :
            i_choice = 0

            self.screen_clear()
            print(self.o_common.get_head_msg('FLETA AGENT DISKINFO CONFIG GENERATOR'))
            print(s_menu)
            try:
                i_choice = int(input('Enter Your Choice [1-9] : '))
                if i_choice > 9:
                    print ("Invalid number. Try again...")
                    time.sleep(1)
            except ValueError as e:
                print ("%s is not a valid integer." % e.args[0].split(": ")[1])
                time.sleep(1)

            if i_choice == 1:
                s_home_dir = self.set_agent_path()
                self.o_config.set('COMMON', 'home_dir', s_home_dir)

            elif i_choice == 2:
                a_agent_info = self.set_agent_ip()
                s_agent_ip = a_agent_info['ip']
                s_agent_port = a_agent_info['port']

                self.o_config.set('COMMON', 'agent_ip', s_agent_ip)
                self.o_config.set('COMMON', 'agent_port', s_agent_port)

            elif i_choice == 3:
                a_srm_info = self.set_srm_ip()
                s_srm_ip = a_srm_info['ip']
                s_srm_port = a_srm_info['port']
                self.o_config.set('srm', 'srm_ip', s_srm_ip)
                self.o_config.set('srm', 'srm_port', s_srm_port)

            elif i_choice == 4:
                s_transfer = self.set_transfer()
                self.o_config.set('COMMON', 'transfer', s_transfer)

                if s_srm_ip.strip() != '':
                    a_trans_info = self.set_transfer_conn(s_transfer, s_srm_ip)
                else:
                    a_trans_info = self.set_transfer_conn(s_transfer)

                if s_transfer == 'SOCKET':
                    s_trans_section = 'socket'
                    self.o_config.set(s_trans_section, 'server', a_trans_info['ip'])
                    self.o_config.set(s_trans_section, 'port', a_trans_info['port'])
                elif s_transfer == 'FTP':
                    s_trans_section = 'ftp'
                    s_enc_pw = self.s_aes_cipher.encrypt(a_trans_info['pass'])
                    self.o_config.set(s_trans_section, 'user', a_trans_info['user'])
                    self.o_config.set(s_trans_section, 'pass', s_enc_pw)
                    self.o_config.set(s_trans_section, 'server', a_trans_info['ip'])
                    self.o_config.set(s_trans_section, 'port', a_trans_info['port'])

            elif i_choice == 5:
                s_disk_info_device = self.set_disk_info_device()
                self.o_config.set('systeminfo', 'set_device', s_disk_info_device)
                """
                elif i_choice == 6:
                    s_set_disk_info_wmi = self.set_disk_info_wmi()
                    self.o_config.set('systeminfo','diskcheck', s_set_disk_info_wmi)
                """
            elif i_choice == 6:
                self.cfg_view()

            elif i_choice == 7:
                i_is_valid = 1
                with open(self.s_fleta_cfg , 'wb') as configfile:
                    self.o_config.write(configfile)
            elif i_choice == 8:
                i_is_valid = 1
            else:
                pass

    def mssql_auth(self):
        i_is_valid = 0
        s_mssql_auth_dict = {'user' : '' , 'passwd' : '', 'windows_auth' : 'n'}
        while not i_is_valid:
            s_mssql_auth = input('MSSQL WINDOWS AUTH (Y/N) : ')
            if s_mssql_auth.lower() == 'y':
                i_is_valid = 1
                s_mssql_auth_dict['windows_auth'] = 'y'

            elif s_mssql_auth.lower() == 'n':
                s_mssql_auth_dict['user'] = input('MSSQL AUTH ID : ')
                s_mssql_auth_dict['passwd'] = input('MSSQL AUTH PASSWORD : ')

                if s_mssql_auth_dict['user'] != '' and s_mssql_auth_dict['passwd'] != '':
                    i_is_valid = 1
                else:
                    print ("Invalid User Auth Info. Try again...")
                    time.sleep(1)
            else:
                print ("Invalid Windows Auth. Try again...")
                time.sleep(1)
        return s_mssql_auth_dict

    def oracle_auth(self):
        i_is_valid = 0
        s_oracle_auth_dict = {  'hostname': ''
                              , 'port' : ''
                              , 'user' : ''
                              , 'passwd' : ''
                              , 'sysdba' : 'n'
                              , 'sid' : ''}
        while not i_is_valid:
            s_oracle_auth = input('oracle sysdba AUTH (Y/N) : ')
            if s_oracle_auth.lower() == 'y':
                i_is_valid = 1
                s_oracle_auth_dict['sysdba'] = 'y'

            elif s_oracle_auth.lower() == 'n':
                s_oracle_auth_dict['sid'] = input('oracle USER SERVICE ID (SID) : ')
                s_oracle_auth_dict['user'] = input('oracle User ID : ')
                s_oracle_auth_dict['passwd'] = input('oracle User Password : ')
                s_oracle_auth_dict['hostname'] = input('oracle Hostname(IP or Hostname) : ')
                s_oracle_auth_dict['port'] = input('oracle Port : ')
                s_oracle_auth_dict['tnsname'] = input('oracle TNS Info : ')

                if s_oracle_auth_dict['user'] != '' and s_oracle_auth_dict['passwd'] != '' and s_oracle_auth_dict['sid'] != '':
                    i_is_valid = 1
                else:
                    print ("Invalid User Auth Info. Try again...")
                    time.sleep(1)
            else:
                print ("Invalid ORACLE SYSDBA Auth. Try again...")
                time.sleep(1)
        return s_oracle_auth_dict

    def oracle_sid_list(self):
        i_is_valid = 0
        while not i_is_valid:
            i_int = 0
            a_section = {}
            print("-" * 20)
            for s_section in self.o_cfg_ora.sections():
                i_int = int(i_int) + 1
                a_section[i_int] = str(s_section)
                print(str(i_int) + ") SID : " + str(s_section))
                print("   HOSTNAME : " + self.o_cfg_ora.get(str(s_section), 'hostname'))
                print("   PORT : " + self.o_cfg_ora.get(str(s_section), 'port'))
                print("   USER : " + self.o_cfg_ora.get(str(s_section), 'user'))
                print("   PASSWD : " + self.o_cfg_ora.get(str(s_section), 'passwd'))
                print("   TNS Info : " + self.o_cfg_ora.get(str(s_section), 'tnsname'))
                print("-" * 20)

            s_sid_control_cmd = input("Enter Your Choice(Number : SID remove 1~" + str(i_int) + " , 'x' : prev menu) : ")

            try:
                if s_sid_control_cmd == 'x':
                    i_is_valid = 1
                elif int(s_sid_control_cmd) > 0 and int(s_sid_control_cmd) <= int(i_int) :
                    self.o_cfg_ora.remove_section(a_section[int(s_sid_control_cmd)])
                    with open(self.s_oracle_cfg , 'wb') as configfile_oralce:
                        self.o_cfg_ora.write(configfile_oralce)
                else:
                    print ("Invalid number. Try again...")
            except ValueError as e:
                print ("Invalid number. Try again...")
                time.sleep(1)

    def db_main(self):
        i_is_valid = 0

        s_menu = """
1. MSSQL DB AUTH (only windows NT)
2. ORACLE DB AUTH
3. ORACLE SID USER LIST
4. PREV MENU
"""
        while not i_is_valid :
            i_choice = 0
            self.screen_clear()
            print(self.o_common.get_head_msg('FLETA AGENT DATABASE CONFIG GENERATOR'))
            print(s_menu)
            try:
                i_choice = int(input('Enter Your Choice [1-4] : '))
                if i_choice > 4:
                    print ("Invalid number. Try again...")
                    time.sleep(1)
            except ValueError as e:
                print ("Invalid number. Try again...")
                time.sleep(1)

            if i_choice == 1:
                a_mssql_auth_info = self.mssql_auth()

                self.o_cfg_dbms.set('MSSQL_AUTH', 'windows_auth', a_mssql_auth_info['windows_auth'])

                if a_mssql_auth_info['windows_auth'] == 'n':
                    self.o_cfg_dbms.set('MSSQL_AUTH', 'user', a_mssql_auth_info['user'])

                    s_passwd = self.s_aes_cipher.encrypt(a_mssql_auth_info['passwd'])
                    self.o_cfg_dbms.set('MSSQL_AUTH', 'passwd', s_passwd)

                with open(self.s_dbms_cfg , 'wb') as configfile_dbms:
                    self.o_cfg_dbms.write(configfile_dbms)

            elif i_choice == 2:
                a_oracle_auth_info = self.oracle_auth()
                self.o_cfg_dbms.set('ORACLE_AUTH', 'sysdba', a_oracle_auth_info['sysdba'])
                with open(self.s_dbms_cfg , 'wb') as configfile_dbms:
                    self.o_cfg_dbms.write(configfile_dbms)

                if a_oracle_auth_info['sysdba'] == 'n':
                    self.o_cfg_ora.add_section(a_oracle_auth_info['sid'])
                    self.o_cfg_ora.set(a_oracle_auth_info['sid'], 'user', a_oracle_auth_info['user'])

                    s_passwd = self.s_aes_cipher.encrypt(a_oracle_auth_info['passwd'])
                    self.o_cfg_ora.set(a_oracle_auth_info['sid'], 'passwd', s_passwd)
                    with open(self.s_oracle_cfg , 'wb') as configfile_oralce:
                        self.o_cfg_ora.write(configfile_oralce)
            elif i_choice == 3:
                self.oracle_sid_list()
            elif i_choice == 4:
                i_is_valid = 1
            else:
                pass

    def main(self):
        i_is_valid = 0
        s_menu = """
1. AGENT Config
2. DB Auth Config
3. EXIT
"""
        while not i_is_valid :
            i_choice = 0
            self.screen_clear()
            print(self.o_common.get_head_msg('FLETA AGENT CONFIG GENERATOR'))
            print(s_menu)
            try:
                i_choice = int(input('Enter Your Choice [1-3] : '))
                if i_choice > 3:
                    print ("Invalid number. Try again...")
                    time.sleep(1)

            except ValueError as e:
                print ("Invalid number. Try again...")
                time.sleep(1)
            print()
            if i_choice == 1:
                self.agent_main()
            elif i_choice == 2:
                self.db_main()
            elif i_choice == 3:
                i_is_valid = 1
            else:
                pass

if __name__ == '__main__':
    try:
        AgentConfigGen().main()
    except KeyboardInterrupt:
        pass
    finally:
        sys.exit(1)
