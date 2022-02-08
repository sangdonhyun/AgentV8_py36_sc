#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2016.07.26
    @author: jhbae
'''
import subprocess
import os
import sys
from lib.common import Common
from subprocess import PIPE, STDOUT

class DaemonControl():
    def __init__(self):
        self.b_windows = sys.platform == 'win32'
        self.o_common = Common()

    def start(self, s_process_file_name, s_pid_file, b_rtn=False):
            """ Create process file, and save process ID of detached process """
            i_pid = ""
            s_process_file_name = self.o_common.s_agent_path + s_process_file_name

            if self.b_windows:
                # start child process in detached state
                DETACHED_PROCESS = 0x00000008
                import ntpath
                s_process_file_name = ntpath.abspath(s_process_file_name)
                s_pid_file = ntpath.abspath(s_pid_file)
                if os.path.isfile(s_process_file_name + '.exe'):
                    p = subprocess.Popen([s_process_file_name, "child"], creationflags=DETACHED_PROCESS)
                    i_pid = p.pid
                else:
                    print(('[START ERROR] ' + s_process_file_name + '.exe File Not Found'))
                    sys.exit(1)

            else:
                s_process_file_name = s_process_file_name + '.pyc'
                if os.path.isfile(s_process_file_name):
                    p = subprocess.Popen(['nohup', sys.executable, s_process_file_name, "child"]
                                         , stdout=open('/dev/null', 'w')
                                         , stderr=open('logs/daemon_error.log', 'a')
                                         , close_fds=True)

                    i_pid = p.pid
                else:
                    print(('[START ERROR] ' + s_process_file_name + ' File Not Found'))
                    sys.exit(1)

            print("Service " + str(i_pid) + " started")

            # create processfile to signify process has started
            with open(s_pid_file, 'w') as f:
                f.write(str(i_pid))
            f.close()


    def stop(self, s_process_file_name, s_pid_file, b_rtn=False):
        """ Kill the process and delete the process file """

        i_proc_id = ""
        try:
            with open(s_pid_file, "r") as f:
                i_proc_id = f.readline()
            f.close()
        except IOError:
            print("process file does not exist, but that's ok <3 I still love you")

        if i_proc_id:
            if self.b_windows:
                try:
                    o_kill_process = subprocess.Popen(['taskkill.exe', '/PID', i_proc_id, '/F'], stdout=PIPE, stderr=PIPE)
                    o_kill_process.communicate()
                except Exception as e:
                    print(e)
                    print("could not kill " + i_proc_id)
                else:
                    print("Service " + i_proc_id + " stopped")
            else:
                try:
                    subprocess.Popen(['kill', '-9', i_proc_id])
                except Exception as e:
                    print(e)
                    print("could not kill " + i_proc_id)
                else:
                    print("Service " + i_proc_id + " stopped")

            os.remove(s_pid_file)
