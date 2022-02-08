#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import sys
import signal
import threading
import os
import base64
import configparser
import socket
import platform
from wsgiref.simple_server import make_server
from cgi import parse_qs
from subprocess import Popen, PIPE

from lib.control import Control
from lib.daemon_control import DaemonControl
from lib.common import Common
from lib.log_control import LogControl

s_conf_file = 'config/fleta_config.cfg'

class Webshite():
    def __init__(self):
        self.o_common = Common()
        self.allow_response_keys = ['cmd', 'argu', 'cipher']
        self.log_control = LogControl()


    def signal_handler(self, signal, frame):
        pass

    def b64_decode(self, s_encode_str):
        return base64.decodestring(s_encode_str).strip()

    def grains(self, environ, start_response):
        s_cmd = ''
        self.environ = environ
        self.start = start_response
        status = '200 OK'
        response_headers = [('Content-Type', 'text/plain')]

        self.start(status, response_headers)

        if environ['REQUEST_METHOD'] == 'GET':

            a_query_string = parse_qs(environ['QUERY_STRING'])  # turns the qs to a dict
            i_mis_count = len(list(set(self.allow_response_keys) - set(a_query_string.keys())))

            if len(a_query_string) > 1:
                if i_mis_count > 0:
                    self.log_control.logdata('AGENT', 'ERROR', '50010')
                    return 'Miss Match Not Argument - ' + str(list(set(self.allow_response_keys) - set(a_query_string.keys())))

                try:
                    s_cmd = self.b64_decode(a_query_string['cmd'][0])
                    s_argument = self.b64_decode(a_query_string['argu'][0])
                except Exception as e:
                    self.log_control.logdata('AGENT', 'ERROR', '50006', str(e))
                    return '[ERROR]Miss Match Argument %s' % (str(e))
        else:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            request_body = environ['wsgi.input'].read(request_body_size)
            a_query_string = parse_qs(request_body)  # turns the qs to a dict
            return 'From POST: %s' % ''.join('%s: %s' % (k, v) for k, v in a_query_string.iteritems())

        if s_cmd:
            if os.path.isfile(s_conf_file):
                self.fleta_config = configparser.ConfigParser()
                self.fleta_config.read(s_conf_file)
            else :
                self.log_control.logdata('AGENT', 'ERROR', '50007', str(s_conf_file))
                return "ERROR : " + s_conf_file + "FILE NOT FOUND"

            try :

                s_checker_action = self.fleta_config.get('action', s_cmd)
                if s_checker_action.strip() != 'T':
                    self.log_control.logdata('AGENT', 'ERROR', '50008', str(s_cmd))
                    return "Not Execute Action [%s]" % (s_cmd)
            except Exception as e:
                self.log_control.logdata('AGENT', 'ERROR', '50009', str(s_cmd))
                return "NOT MATCH FletaAgent Command!!"

            try :
                s_args = ''
                if s_argument != 'F':
                    s_args = s_argument
                o_control = Control(s_args)
                s_str_func = 'o_control.%s' % (s_cmd)
                s_response = eval(s_str_func)()
            except Exception as e:
                s_response = str(e)
                self.log_control.logdata('AGENT', 'ERROR', '50009', "2" + str(s_response))
                return s_response
        else :
            s_response = ''
        return s_response

    def run(self):
        s_agent_port = self.o_common.cfg_parse_read('fleta.cfg', 'COMMON', 'agent_port')

        if s_agent_port.strip() == '':
            i_agent_port = int(54001)
        else:
            i_agent_port = int(s_agent_port)
        try:
            srv = make_server('', i_agent_port, self.grains)
            srv.serve_forever()

        except KeyboardInterrupt:
            signal.signal(signal.SIGINT, self.signal_handler)
        while True:
            try:
                threading.Thread(target=srv.handle_request()).start()
            except Exception as e:
                self.log_control.logdata('AGENT', 'ERROR', '50003', str(e))

if __name__ == '__main__':

    o_web_shite = Webshite()
    s_pid_path = Common().s_agent_path + "/pid/"
    a_process = {'Daemon' : {
                          'proc_file' : '/fleta_daemon'
                         , 'pid_name' : 'fleta_daemon.pid'
                        }
                 , 'Schedule' : {
                          'proc_file' : '/fleta_schedule'
                         , 'pid_name' : 'fleta_schedule.pid'
                     }
                }

    o_daemon_control = DaemonControl()


    if os.path.isdir(s_pid_path) == False:
        os.mkdir(s_pid_path)

    def status_write(s_contents):
        try:
            print (s_contents)
            # Common().file_write('/logs/status.log', s_contents)
        except:
            pass

    def help_run():
        try:
            s_contents = "usage: " + __file__ + " start all | stop all |start Daemon or Schedule | stop Daemon or Schedule"
        except NameError:  # We are the main py2exe script, not a module
            s_contents = "usage: " + os.path.abspath(sys.argv[0]) + " start all | stop all |start Daemon or Schedule | stop Daemon or Schedule"

        return status_write(s_contents)

    def start(s_proc_file, s_pid_name):
        s_pid_file = s_pid_path + s_pid_name

        if pid_file_check(s_pid_name) == False:
            o_daemon_control.start(s_proc_file, s_pid_file)
        else:
            return status_write("ERROR : [%s] process is already started" % (s_proc_file.replace('/', '')))

    def stop(s_proc_file, s_pid_name):
        s_pid_file = s_pid_path + s_pid_name

        if pid_file_check(s_pid_name):
            o_daemon_control.stop(s_proc_file, s_pid_file)
        else:
            return status_write("ERROR : [%s] process is already stopped" % (s_proc_file.replace('/', '')))

    def pid_proc_check(s_pid_name='', s_pid=''):

        if sys.platform == 'win32':  # Windows

            process = Popen(
                'tasklist.exe /FO CSV /FI "PID eq %s"' % (str(s_pid)),
                stdout=PIPE, stderr=PIPE,
                universal_newlines=True)
            out, err = process.communicate()
            try :

                return out.split("\n")[1].startswith('"%s.exe"' % (s_pid_name.replace('.pid', '')))
            except :
                return False
        else:  # Posix
            try:
                b_ps_custom = Common().cfg_parse_read('custom_path.cfg', 'ps', 'custom')
            except:
                b_ps_custom = 'F'

            if b_ps_custom is 'T':
                try:
                    s_ps_path = Common().cfg_parse_read('custom_path.cfg', 'ps', 'file')
                except:
                    s_ps_path = '/bin/ps'
            else:
                s_ps_path = '/bin/ps'


            try:
                b_ps_print = Common().cfg_parse_read('custom_path.cfg', 'ps', 'print')
            except:
                b_ps_print = 'F'

            try:
                a_os_info = platform.uname()
            except:
                a_os_info = []

            try:

                if a_os_info[0] == 'SunOS' and a_os_info[2] == '5.10':
                    if os.path.isfile('/usr/ucb/ps'):
                        s_ps_command = "/usr/ucb/ps -auxww | grep %s | grep -v 'grep'|wc -l" % (s_pid_name.replace('.pid', '')[0:7])
                    else:
                        s_ps_command = "%s -ef | grep %s | grep -v 'grep'|wc -l" % (s_ps_path, s_pid_name.replace('.pid', '')[0:7])
                else:
                    s_ps_command = "%s -ef | grep %s | grep -v 'grep'|wc -l" % (s_ps_path, s_pid_name.replace('.pid', '')[0:7])

                if os.path.isfile(s_ps_path) is False:
                    status_write("ps Command File Not Found  ==> %s" % (s_ps_path))
                    sys.exit(1)

                if b_ps_print == 'T':
                    print (s_ps_command)

                o_p = os.popen(s_ps_command, "r")

                i_proc_cnt = o_p.read().strip()

                if 'fleta_daemon' == s_pid_name.replace('.pid', '') and int(i_proc_cnt) < 2:
                    return False

                if len(i_proc_cnt) == 1 and int(i_proc_cnt) < 1:
                    return False
                elif len(i_proc_cnt) > 5:
                    status_write("Process Start Error")
                    sys.exit(1)
                else:
                    return True
            except Exception as e:
                status_write("Process Start Exception Error => %s" % str(e))
                sys.exit(1)

    def pid_file_check(s_pid_name):
        b_rtn = False

        s_pid_file = s_pid_path + s_pid_name

        if os.path.isfile(s_pid_file):
            try:
                s_pid_file = s_pid_path + s_pid_name
                o_f = open(s_pid_file, 'r')
                s_pid = o_f.read().strip()
                o_f.close()

                if len(s_pid) > 0:
                    b_rtn = pid_proc_check(s_pid_name=s_pid_name, s_pid=s_pid)
                else:
                    return False
            except:
                return False
        else:
            b_rtn = pid_proc_check(s_pid_name=s_pid_name)
        return b_rtn


    if len(sys.argv) > 1:
        s_proc_file = ''
        if sys.argv[1] == 'child':
            o_web_shite.run()

        if len(sys.argv) < 3:
            help_run()
            sys.exit(1)

        elif sys.argv[1] == 'start':
            if sys.argv[2] == 'all':
                for s_process_key in a_process:
                    for s_proc in a_process[s_process_key]:
                        if s_proc == 'pid_name':
                            s_pid_name = a_process[s_process_key]['pid_name']
                            s_proc_file = a_process[s_process_key]['proc_file']
                            start(s_proc_file, s_pid_name)

            elif sys.argv[2] == 'Schedule':
                s_pid_name = a_process['Schedule']['pid_name']
                s_proc_file = a_process['Schedule']['proc_file']
                start(s_proc_file, s_pid_name)

            elif sys.argv[2] == 'Daemon':
                s_pid_name = a_process['Daemon']['pid_name']
                s_proc_file = a_process['Daemon']['proc_file']
                start(s_proc_file, s_pid_name)

            else:
                help_run()

        elif sys.argv[1] == 'stop':
            if sys.argv[2] == 'all':
                for s_process_key in a_process:
                    for s_proc in a_process[s_process_key]:
                        if s_proc == 'pid_name':
                            s_pid_name = a_process[s_process_key]['pid_name']
                            s_proc_file = a_process[s_process_key]['proc_file']
                            stop(s_proc_file, s_pid_name)

            elif sys.argv[2] == 'Schedule':
                s_pid_name = a_process['Schedule']['pid_name']
                s_proc_file = a_process['Schedule']['proc_file']
                stop(s_proc_file, s_pid_name)

            elif sys.argv[2] == 'Daemon':
                s_pid_name = a_process['Daemon']['pid_name']
                s_proc_file = a_process['Daemon']['proc_file']
                stop(s_proc_file, s_pid_name)

            else:
                help_run()
    else:
        help_run()


# kill main
os._exit(0)
