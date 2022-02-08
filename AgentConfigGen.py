#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2016.09.26
    @author: jhbae
'''

import sys
import os
import base64
import hashlib
import configparser
import re
import socket
import time
from lib.common import Common

class AgentConfigGen():
    def __init__(self):
        self.o_common = Common()
        self.s_aes_cipher = self.o_common.s_aes_cipher
        self.s_fleta_cfg = os.path.join(self.o_common.s_config_path, 'fleta.cfg')


        if os.path.isfile(self.s_fleta_cfg):
            self.o_config = configparser.RawConfigParser()
            self.o_config.optionxform = str
            self.o_config.read(self.s_fleta_cfg)
        print(self.o_common.s_config_path)
        if os.path.isfile(os.path.join(self.o_common.s_config_path, 'HSRM.ini')):
            a_setup_tmp = self.o_common.cfg_parse_read('HSRM.ini', 'SETUP')
            # self.a_setup = self.o_common.tuple_to_dict(a_setup_tmp)
            self.a_setup = a_setup_tmp

        else:
            print('[ERROR] HSRM.ini File Not Found.')

    def _en(self, _in):
        return base64.b64encode(_in)

    def fenc(self, s_str):
        s_encode_tmp = self._en(s_str)
        s_encode = self._en(s_encode_tmp)

        s_encode_hash = hashlib.md5(s_encode_tmp).hexdigest()
        s_encode = s_encode.replace('=', '@')
        s_encode_val = s_encode + '@' + s_encode_hash
        return s_encode_val

    def screen_clear(self, b_head=True):
        os.system('cls' if os.name == 'nt' else 'clear')

        if b_head:
            print(self.o_common.get_head_msg('FLETA AGENT CONFIG GENERATOR'))

    def is_valid_ip(self, s_ip):
        m = re.match(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$", s_ip)
        return bool(m) and all([0 <= int(n) <= 255 for n in m.groups()])

    def set_ip(self, s_socket_host, s_socket_port):

        a_info = {}
        s_data = ''
        a_info['FLETA_PASS'] = 'kes2719!'
        a_info['MYIP'] = 'kes2719!'

        s_info_data = self.fenc(str(a_info))

        try:
            o_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            o_sock.settimeout(2)
            o_sock.connect((s_socket_host, int(s_socket_port)))
            o_sock.sendall(s_info_data)
            s_data = o_sock.recv(1024)
            o_sock.close()
        except:
            try:
                a_host_info = socket.getaddrinfo(socket.gethostname(), None)

                for a_sock in a_host_info:
                    s_ip = a_sock[4][0]
                    s_ip = s_ip.strip()
                    if self.is_valid_ip(s_ip):
                        if s_ip == '127.0.0.1' or re.match('192\.168.+', s_ip):
                            pass
                        else :
                            s_data = s_ip
                            break
            except:
                s_data = ''
        return s_data

    def cfg_view(self):
        self.screen_clear(b_head=False)
        print(self.o_common.get_head_msg('VIEW CONFIG'))

        print("AGENT HOME DIR".ljust(22) + " : " + self.o_config.get('COMMON', 'home_dir'))
        print("AGENT INFO")
        print(" - ip ".ljust(22) + " : " + self.o_config.get('COMMON', 'agent_ip'))
        print(" - port ".ljust(22) + " : " + self.o_config.get('COMMON', 'agent_port'))
        print("SRM SERVER INFO")
        print(" - ip " .ljust(22) + " : " + self.o_config.get('srm', 'srm_ip'))
        print(" - port " .ljust(22) + " : " + self.o_config.get('srm', 'srm_port'))

        s_transfer_type = self.o_config.get('COMMON', 'transfer')
        print("TRANSFER CONN INFO")
        print(" - type ".ljust(22) + " : " + s_transfer_type.upper())
        print(" - ip".ljust(22) + " : " + self.o_config.get(s_transfer_type.lower(), 'server'))
        print(" - port".ljust(22) + " : " + self.o_config.get(s_transfer_type.lower(), 'port'))

        print("SYSTEM DEVICE TYPE".ljust(22) + " : " + self.o_config.get('systeminfo', 'set_device'))

        if os.name == 'nt':
            print("SYSTEM DISK CHECK TYPE".ljust(22) + " : " + self.o_config.get('systeminfo', 'diskcheck'))

    def agent_main(self):
        i_is_valid = 0

        while not i_is_valid :

            self.screen_clear()
            s_home_dir = os.getcwd()
            self.o_config.set('COMMON', 'home_dir', s_home_dir)

            # SRM IP SETTING
            self.o_config.set('srm', 'srm_ip', self.a_setup["HSRM_IP"])
            self.o_config.set('srm', 'srm_port', self.a_setup["HSRM_PORT"])

            # AGENT_PORT
            self.o_config.set('COMMON', 'agent_port', self.a_setup["AGENT_PORT"])

            # RECEIVER PORT
            self.o_config.set('socket', 'server', self.a_setup["HSRM_IP"])
            self.o_config.set('socket', 'port', self.a_setup["RECV_PORT"])

            # FSTYPE
            self.o_config.set('systeminfo', 'set_device', self.a_setup["FSTYPE"])

            # AGENT IP
            s_agent_ip = self.set_ip(s_socket_host=self.a_setup["HSRM_IP"], s_socket_port=self.a_setup["RECV_PORT"])

            if s_agent_ip.strip() == '':
                while 1:
                    s_agent_custom_ip = input('Agent IP : ')

                    if self.is_valid_ip(s_agent_custom_ip):
                        s_agent_ip = s_agent_custom_ip
                        break

            self.o_config.set('COMMON', 'agent_ip', s_agent_ip)

            with open(self.s_fleta_cfg , 'wb') as configfile:
                self.o_config.write(configfile)

            if self.a_setup['DAEMON'].lower() != 'none':
                s_task = "SCHTASKS /Create /SC DAILY /TN AGENT_CHECK /TR %s\\fletaDaemonCheck.bat /ST %s /NP /RL HIGHEST /F" % (s_home_dir, self.a_setup['DAEMON'])
                self.o_common.get_execute(s_task)

            s_task_check = "SCHTASKS /query | findstr AGENT_CHECK"
            s_task_rtn = self.o_common.get_execute(s_task_check)

            self.cfg_view()

            if len(s_task_rtn) > 0:
                print(s_task_rtn)
            print("#"*37)
            print("  Fleta Agent Config Setup Complete")
            print("#"*37)

            print("#"*37)
            print("  Fleta Agent Daemon Start")
            s_daemon_check = os.path.join(s_home_dir, 'fletaDaemonCheck.bat')
            os.system(s_daemon_check)
            print("#"*37)
            input('\nPressed Enter key........')
            i_is_valid = 1



if __name__ == '__main__':
    try:
        AgentConfigGen().agent_main()
    except KeyboardInterrupt:
        print("EXCEPT")
        pass
    finally:
        sys.exit(1)
