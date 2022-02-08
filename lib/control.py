#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2016.07.20
    @author: jhbae
'''
import os
import re
import sys
import socket
import json
import platform
import subprocess
from lib import cron_schedule
from subprocess import PIPE, STDOUT
from fleta_agent_info import FletaAgentInfo
from lib.common import Common
from lib.daemon_control import DaemonControl
from lib.log_control import LogControl

class Control():

    def __init__(self, parent_args):
        self.argument = parent_args
        self.o_control = FletaAgentInfo()
        self.o_common = Common()
        self.s_hostname = socket.gethostname()
        self.b_windows = sys.platform == 'win32'
        self.s_log_dir = self.o_common.s_agent_path + '/logs/'
        self.s_process_file_name = os.path.realpath(__file__)
        self.o_daemon_control = DaemonControl()
        self.o_log_control = LogControl()

    def process_control(self, s_proc_file_name, s_process_type):
        # #중복실행 체크가 필요할듯...
        DETACHED_PROCESS = 0x00000008
        if self.b_windows:
            o_p = subprocess.Popen(s_proc_file_name, creationflags=DETACHED_PROCESS, stdout=PIPE, stderr=PIPE)
        else:
            o_p = subprocess.Popen(['/bin/sh', s_proc_file_name], stdout=PIPE, stderr=PIPE)
        """
        s_output = p.stdout.read()
        s_perror = p.stderr.read()
        """

        s_output , s_perror = o_p.communicate()

        if s_output.strip():
            self.o_log_control.logdata('AGENT', 'ACCESS', '30011', '%s' % (s_process_type))
            return str(s_output)
        else:
            self.o_log_control.logdata('AGENT', 'ERROR', '30011', "[Error] => %s \n %s" % (s_process_type, str(s_perror)))
            return str("Agent Check Fail\n\n") + str(s_perror)

    def file_read(self, s_file_path):
        if os.path.isfile(s_file_path):
            s_file_contents = ''
            if os.path.getsize(s_file_path) < 51200:  # # 50KB 이하일경우
                o_f = open(s_file_path, 'r')
                s_file_contents = o_f.read()
                o_f.close()
            else :
                with open(s_file_path) as o_f:
                    a_line_offsets = [0]
                    for s_line in o_f:
                        # do some jobs for line
                        a_line_offsets.append(s_line)
                i_line_total = len(a_line_offsets)
                i_line_offset = i_line_total - 300
                s_file_contents = "".join(a_line_offsets[i_line_offset:i_line_total])
        else :
            s_file_contents = 'File Open Fail : [%s] File Not Found.' % (s_file_path)
        return s_file_contents.strip()

    def log_list(self):
        a_log_file = {
                       'Access Log' : []
                      , 'Error Log' : []
                    }
        if os.path.isdir(self.s_log_dir) :
            a_file_names = os.listdir(self.s_log_dir)
            for s_log_file in a_file_names:
                s_log_file_tmp = s_log_file.replace('.log', '')
                if re.search('_ACCESS', s_log_file_tmp):
                    a_log_file['Access Log'].append(s_log_file_tmp)
                elif re.search('_ERROR', s_log_file_tmp) :
                    a_log_file['Error Log'].append(s_log_file_tmp)
        return json.dumps(a_log_file)

    def system_uname(self):
        s_uname = ' '.join(platform.uname())
        return s_uname

    # control Start
    def fleta_info(self):
        s_fleta_info = self.o_control.info()
        s_title = "Agent INFO  - %s" % (self.s_hostname)
        return self.o_common.get_msg(s_title, s_fleta_info)

    def sched_change(self):
        s_str = self.argument.strip()
        s_file_path = self.o_common.s_config_path + '/sched.format'
        o_f_read = open(s_file_path, 'r')
        s_sched_before = o_f_read.read()
        o_f_read.close()

        a_time = s_str.split(":")

        if isinstance(a_time, list) :
            a_schedule_time = {
                               'min': a_time[0]
                               , 'hour': a_time[1]
                               , 'day': a_time[2]
                               , 'month': a_time[3]
                               , 'weekday': a_time[4]
                            }
            m_rtn = cron_schedule.schedule_valid_check(a_schedule_time)
        else :
            s_sched_change_get = "[%s] The schedule you entered is invalid." % (s_str)

        if m_rtn is True:
            o_f = open(s_file_path, 'w')
            o_f.write(s_str)
            o_f.close()

            s_sched_change_get = """
* The Agent schedule has been changed.
  - Before the change : %s
  - After the change : %s""" % (s_sched_before , s_str)

        elif m_rtn == False:
            s_sched_change_get = "[%s] The schedule you entered is invalid." % (s_str)
        else :
            s_sched_change_get = m_rtn
        s_title = "Agent Schedule Change - %s" % (self.s_hostname)

        s_rtn_msg = self.o_common.get_msg(s_title, s_sched_change_get)
        self.o_log_control.logdata('AGENT', 'ACCESS', '30011', s_rtn_msg)
        return s_rtn_msg

    def sched_date_get(self):
        s_file_path = self.o_common.s_config_path + '/sched.format'
        s_sched_date_get = self.file_read(s_file_path)
        s_title = "Agent Schedule - %s" % (self.s_hostname)
        s_rtn_msg = self.o_common.get_msg(s_title, s_sched_date_get)
        return s_rtn_msg

    def sched_form_get(self):
        s_file_path = self.o_common.s_config_path + '/sched.date'
        s_sched_form_get = self.file_read(s_file_path)
        s_title = "Agent Schedule Execute Check - %s" % (self.s_hostname)

        s_rtn_msg = self.o_common.get_msg(s_title, s_sched_form_get)
        return s_rtn_msg

    def sched_restart(self):
        s_process_file_name = 'fleta_schedule'
        s_pid_name = 'fleta_schedule.pid'
        s_pid_path = self.o_common.s_agent_path + "/pid/"
        s_pid_file = s_pid_path + s_pid_name

        # self.o_daemon_control.stop(s_process_file_name, s_pid_file, False)

        # schedule down
        try:
            a_os_info = platform.uname()
        except:
            a_os_info = []

        try:
            if a_os_info[0] == 'SunOS' and a_os_info[2] == '5.10':
                if os.path.isfile('/usr/ucb/ps'):
                    o_schedule_ps = os.popen("/usr/ucb/ps -auxww | grep fleta_s|grep -v 'grep'|awk '{print $2}'")
                else:
                    o_schedule_ps = os.popen("ps -ef | grep fleta_s | grep -v 'grep'|awk '{print $2}'")
            else:
                o_schedule_ps = os.popen("ps -ef | grep fleta_s | grep -v 'grep'|awk '{print $2}'")

            s_schedule_ps = o_schedule_ps.read().strip()
        except:
            s_schedule_ps = ''

        if len(s_schedule_ps) > 0 and s_schedule_ps != '':
            for i_sched_pid in s_schedule_ps.split('\n'):
                try:
                    subprocess.Popen(['kill', '-9', i_sched_pid])
                except:
                    pass

        self.o_daemon_control.start('/' + s_process_file_name, s_pid_file, False)
        if self.b_windows:
            s_proc_file_name = self.o_common.s_agent_path + '/version_check.exe'
        else:
            s_proc_file_name = self.o_common.s_agent_path + '/version.sh'
        self.process_control(s_proc_file_name, 'schedule restart')

        return 'T'

    def log_view(self):
        s_file = "%s.log" % (self.argument)
        s_file_path = self.s_log_dir + s_file
        s_log_view = self.file_read(s_file_path)
        s_title = "Agent Log %s - %s " % (s_file, self.s_hostname)

        s_rtn_msg = self.o_common.get_msg(s_title, s_log_view)
        return s_rtn_msg

    def diskinfo_check(self):
        if self.b_windows:
            s_proc_file_name = self.o_common.s_agent_path + '/fleta_diskinfo.exe'
        else:
            s_proc_file_name = self.o_common.s_agent_path + '/fleta_diskinfo.sh'
        return self.process_control(s_proc_file_name, 'diskinfo check')

    def fleta_patch(self):
        if self.b_windows:
            s_proc_file_name = self.o_common.s_agent_path + '/version_check.exe'
        else:
            s_proc_file_name = self.o_common.s_agent_path + '/version.sh'
        return self.process_control(s_proc_file_name, 'agent patch')

    # def fleta_rollback(self):
