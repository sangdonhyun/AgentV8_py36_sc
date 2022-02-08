#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2016.07.29
    @author: jhbae
'''
import os
import sys
import signal
import threading
from subprocess import call , PIPE
from time import strftime, localtime, sleep

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0]))))

from threading import Thread
import  lib.cron_schedule as cron_schedule
from lib.common import Common
from lib.log_control import LogControl

class SrmSchedule():
    def __init__(self):
        self.o_common = Common()
        self.b_execute_check_bit = True
        self.b_execute_check_bit2 = True
        self.log_control = LogControl()

    def cron_checker(self, s_cron_item, s_file='fleta_diskinfo'):
        b_cron_checker = cron_schedule.schedule_check(s_cron_item)

        if b_cron_checker:
            if sys.platform == 'win32':
                import ntpath
                s_dir = self.o_common.s_agent_path
                s_cmd = '%s/%s.exe' % (s_dir, s_file)
                s_cmd_version = '%s/version_check.exe' % (s_dir)
            else:
                s_dir = self.o_common.s_agent_path
                s_cmd = '%s/%s.pyc' % (s_dir, s_file)
                s_cmd_version = '%s/version_check.pyc' % (s_dir)

            # self.log_control.logdata('CRON', 'ACCESS', '10005', s_cmd_version)
            self.log_control.logdata('CRON', 'ACCESS', '10005', s_cmd)

            try:
                if sys.platform == 'win32':
                    call(s_cmd, shell=True)
                else:
                    self.log_control.logdata('CRON', 'ACCESS', '10005', [sys.executable, s_cmd_version])
                    self.log_control.logdata('CRON', 'ACCESS', '10005', [sys.executable, s_cmd])
                    call([sys.executable, s_cmd])

            except Exception as e:
                self.log_control.logdata('CRON', 'ERROR', '10010', "CALL ERROR : " + str(e))

        return b_cron_checker

    def schedule_parse(self, s_schedule):
        a_time = s_schedule.split(":")

        if isinstance(a_time, list) :
            a_schedule_time = {
                               'min': a_time[0]
                               , 'hour': a_time[1]
                               , 'day': a_time[2]
                               , 'month': a_time[3]
                               , 'weekday': a_time[4]
                            }
        return cron_schedule.schedule_valid_check(a_schedule_time)

    def main_schedule(self):
        s_schedule_format = self.o_common.cfg_file_read('sched.format')
        if self.b_execute_check_bit:
            if self.schedule_parse(s_schedule_format):
                s_schedule = s_schedule_format.replace(":", " ").strip()
                if s_schedule != '':
                    try:
                        s_schedule_time = strftime("%Y-%m-%d %H:%M:%S")
                        b_rtn = self.cron_checker(s_schedule, 'fleta_diskinfo')

                        if b_rtn:
                            self.b_execute_check_bit = False

                            s_executed_time = strftime("%Y-%m-%d %H:%M:%S")
                            s_schedule_contents = """
                            SCHEDULED DATE=%s\nEXECUTED  DATE=%s""" % (s_schedule_time, s_executed_time)
                            self.o_common.cfg_file_write('sched.date', s_schedule_contents.strip())
                            self.b_execute_check_bit = True
                    except KeyboardInterrupt:
                        self.log_control.logdata('CRON', 'ERROR', '10011')
                        signal.signal(signal.SIGINT, self.signal_handler)
                    except Exception as e:
                        self.log_control.logdata('CRON', 'ERROR', '10012', str(e))
            else :
                self.log_control.logdata('CRON', 'ERROR', '10008', s_schedule_format)

    def symevent_schedule(self):
        s_schedule_format = self.o_common.cfg_file_read('sched_symevent.format')
        if self.b_execute_check_bit2:
            if self.schedule_parse(s_schedule_format):
                s_schedule = s_schedule_format.replace(":", " ").strip()
                if s_schedule != '':
                    try:
                        self.b_execute_check_bit2 = False
                        b_rtn = self.cron_checker(s_schedule, 'fleta_sym_event')
                        self.b_execute_check_bit2 = True
                    except KeyboardInterrupt:
                        self.log_control.logdata('CRON', 'ERROR', '10011')
                        signal.signal(signal.SIGINT, self.signal_handler)
                    except Exception as e:
                        self.log_control.logdata('CRON', 'ERROR', '10012', str(e))
            else :
                self.log_control.logdata('CRON', 'ERROR', '10008', s_schedule_format)

    def signal_handler(self, signal, frame):
        pass

    def main(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        while (1):
            if strftime('%S', localtime()) == '00':
                self.log_control.logdata('CRON', 'ACCESS', '10001', strftime("%Y-%m-%d %H:%M:%S"))
                try:
                    t1 = threading.Thread(target=self.main_schedule)
                    t1.start()

                    try:
                        s_sym_event_usage = self.o_common.cfg_parse_read('symEvent.cfg', 'SYMEVENT', 'usage')
                    except:
                        s_sym_event_usage = 'F'

                    if s_sym_event_usage == 'T':

                        t2 = threading.Thread(target=self.symevent_schedule)
                        t2.start()

                except KeyboardInterrupt:
                    self.log_control.logdata('CRON', 'ERROR', '10011')
                except Exception as e:
                    self.log_control.logdata('CRON', 'ERROR', '10011', str(e))
                    sys.exit(1)
            sleep(1)