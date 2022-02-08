#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2016.09.21
    @author: jhbae
'''

import os
import sys
import re
import platform
import socket
from time import localtime, strftime, strptime, ctime
import datetime

# # CRON ITER CHECK
from lib.common import Common
import croniter

class FletaAgentInfo():
    def __init__(self):
        self.o_common = Common()
        self.s_cfg_version = self.o_common.file_read('/version_cfg')
        self.s_module_version = self.o_common.file_read('/version_module')

    def schedule_time_check(self):
        return self.o_common.cfg_file_read('sched.format')

    def schedule_execute_check(self):
        return self.o_common.cfg_file_read('sched.date')

    def agent_listen_port_check(self):
        if sys.platform == 'win32':
            s_search_type = 'findstr'
        else:
            s_search_type = 'grep'

        s_cmd = 'netstat -na | %s 54001' % (s_search_type)
        return self.o_common.get_execute(s_cmd)

    def agent_pid_check(self):
        s_pid_info = ''
        s_pid_dir = self.o_common.s_agent_path + '/pid'
        for root, dirs, files in os.walk(s_pid_dir):
            for s_file in files:
                if s_file.endswith(".pid"):
                    s_ext_file = s_file.replace('.pid', '')
                    s_pid_info += s_ext_file + ' = ' + self.o_common.file_read(os.path.join('/pid', s_file)) + "\n"
        if s_pid_info == '':
            s_pid_info = 'Agent Process NOT FOUND'
        return s_pid_info.strip()

    def agent_alive_check(self):
        if sys.platform == 'win32':
            o_task_list = 'tasklist /FI "imagename eq %s_*" /FI "imagename ne fleta_agent_info*"' % ('fleta')
        else:

            try:
                a_os_info = platform.uname()
            except:
                a_os_info = []

            if a_os_info[0] == 'SunOS' and a_os_info[2] == '5.10':
                if os.path.isfile('/usr/ucb/ps'):
                    o_task_list = '/usr/ucb/ps -auxww | grep %s| grep -v fleta_agent_info |grep -v grep' % ('fleta_')
                else:
                    o_task_list = 'ps -ef | grep %s| grep -v fleta_agent_info |grep -v grep' % ('fleta_')
            else:
                o_task_list = 'ps -ef | grep %s| grep -v fleta_agent_info |grep -v grep' % ('fleta_')

        s_alive_info = self.o_common.get_execute(o_task_list).strip() + "\n"

        try:
            s_alive_info = s_alive_info.encode('utf-8') + '\n'
        except:
            s_alive_info = unicode(s_alive_info, 'ms949').encode('utf-8') + '\n'
        return s_alive_info.strip()


    def data_dir_check(self):
        s_file_info = ''
        for root, dirs, a_files in os.walk(self.o_common.s_data_path):
            if a_files:
                for files in a_files:
                    s_files = ''.join(files)
                    s_file_path = os.path.join(root, s_files)
                    s_path = os.path.normpath(s_file_path)
                    s_filesize = os.path.getsize(s_path)

                    s_file_info += s_file_path
                    s_file_info += '\t'
                    s_file_info += str(ctime(os.path.getctime(s_path)))
                    s_file_info += '\t'
                    s_file_info += 'SIZE : ' + str(s_filesize)

                    s_file_info += '\n'
        return s_file_info


    def remote_port_check(self):
        s_srm_ip = self.o_common.cfg_parse_read('fleta.cfg', 'srm', 'srm_ip')
        s_srm_was_port = self.o_common.cfg_parse_read('fleta.cfg', 'srm', 'srm_port')
        s_srm_recv_ip = self.o_common.cfg_parse_read('fleta.cfg', 'socket', 'server')
        s_srm_recv_port = self.o_common.cfg_parse_read('fleta.cfg', 'socket', 'port')

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((s_srm_ip, int(s_srm_was_port)))
        if result == 0:
            b_was = 'True'
        else:
            b_was = 'False'

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((s_srm_recv_ip, int(s_srm_recv_port)))
        if result == 0:
            b_recv = 'True'
        else:
            b_recv = 'False'

        s_remote = 'SRM WAS %s = ' % (s_srm_was_port) + b_was
        s_remote += '\n'
        s_remote += 'SRM Recv %s = ' % (s_srm_recv_port) + b_recv

        return s_remote

    def cron_next_time_check(self, s_cron_time, s_cron_schedule):
        s_cron_time = s_cron_time.replace(":", " ")
        s_now_time = localtime()

        try:
            base = datetime.datetime(s_now_time.tm_year, s_now_time.tm_mon, s_now_time.tm_mday, s_now_time.tm_hour, s_now_time.tm_min)
            iter = croniter.croniter(s_cron_time, base)
        except Exception as e:
            print (str(e))
            return "NEXT SCHEDULED CHECK FAIL"

        return str(iter.get_next(datetime.datetime))

    def main(self):
        print("*" * 50)
        print("  SRM AGENT STATUS CHECK [" + self.o_common.get_now_time() + "]")
        print("*" * 50)
        print()
        print("::::: Agent Version :::::")
        print("Config Version = %s" % (self.s_cfg_version))
        print("Module Version = %s" % (self.s_module_version))
        print()
        print("::::: Process PID File Check :::::")
        print(self.agent_pid_check())
        print()
        print("::::: Process Alive Check :::::")
        print(self.agent_alive_check())
        print()
        print("::::: Listen Port Check :::::")
        print(self.agent_listen_port_check())
        print()
        print("::::: Agent Schedule :::::")
        s_cron_job = self.schedule_time_check()
        print(s_cron_job)
        print()
        print("::::: Agent Last Executed Time :::::")
        s_cron_schedule = self.schedule_execute_check()
        print(s_cron_schedule)
        print()
        print("::::: Agent Next Executed Time :::::")
        print(self.cron_next_time_check(s_cron_job, s_cron_schedule))

        print()
        print("::::: Agent Data Directory File Check :::::")
        print(self.data_dir_check())

        print()
        print("::::: SRM Remote Port Connection Check :::::")
        print(self.remote_port_check())
        print("=" * 50)

        input("Press Enter to continue...")

    def info(self):
        s_rtn = ''
        s_rtn += "*"*80 + '\n'
        s_rtn += "  SRM AGENT STATUS CHECK [" + self.o_common.get_now_time() + "]\n"
        s_rtn += "*"*80 + '\n'
        s_rtn += "\n::::: Agent Version :::::" + '\n'
        s_rtn += "Config Version = %s" % (self.s_cfg_version) + '\n'
        s_rtn += "Module Version = %s" % (self.s_module_version) + '\n'
        s_rtn += "\n::::: Process PID File Check :::::" + '\n'
        s_rtn += self.agent_pid_check() + '\n'
        s_rtn += "\n::::: Process Alive Check :::::" + '\n'
        s_rtn += self.agent_alive_check() + '\n'
        s_rtn += "\n::::: Listen Port Check :::::" + '\n'
        s_rtn += self.agent_listen_port_check() + '\n'
        s_rtn += "\n::::: Agent Schedule :::::" + '\n'
        s_cron_job = self.schedule_time_check() + '\n'
        s_rtn += s_cron_job
        s_rtn += "\n:::::  Agent Last Executed Time :::::" + '\n'
        s_cron_schedule = self.schedule_execute_check() + '\n'
        s_rtn += s_cron_schedule
        s_rtn += "\n::::: Agent Next Executed Time :::::" + '\n'
        s_rtn += self.cron_next_time_check(s_cron_job, s_cron_schedule) + '\n'
        s_rtn += "\n::::: Agent Data Directory File Check :::::" + '\n'
        s_rtn += self.data_dir_check()
        s_rtn += "\n::::: SRM Remote Port Connection Check :::::" + '\n'
        s_rtn += self.remote_port_check()
        return s_rtn


if __name__ == "__main__":
    FletaAgentInfo().main()
