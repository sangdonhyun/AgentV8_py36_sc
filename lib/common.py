#!/usr/bin/env pythons
# -*- coding: utf-8 -*-
'''
    Created on 2016.07.27
    @author: jhbae
'''

import os
import io
import platform
import sys
# import lib.commands
from subprocess import Popen, PIPE
import configparser
from time import strftime, localtime, time
import socket

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'python_module'))

from lib.aescipher import AESCipher
from lib.log_control import LogControl

# sys.reload(sys)
# sys.setdefaultencoding('utf-8')
if os.name == 'posix':
    ON_POSIX = True
else:
    ON_POSIX = False
# ON_POSIX = 'posix' in sys.builtin_module_names


class Common():
    def __init__(self, ConfigParser=None):
        s_aes_key = 'kes2719!'

        self.s_aes_cipher = AESCipher(s_aes_key)
        self.log_control = LogControl()

        self.s_agent_path = ''
        o_config = configparser.ConfigParser()

        s_current_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])))

        if os.path.isfile(os.path.join(s_current_path, 'config', 'fleta.cfg')):
            o_config.read(os.path.join(s_current_path, 'config', 'fleta.cfg'))
            self.s_agent_path = o_config.get('COMMON', 'home_dir')

        if self.s_agent_path.strip() == '':
            self.s_agent_path = s_current_path

        self.s_config_path = self.s_agent_path + '/config/'
        self.s_data_path = self.s_agent_path + '/data/'
        self.s_tmp_path = self.s_agent_path + '/tmp/'
        self.s_host_name = socket.gethostname()
        try:
            self.b_screen = self.cfg_parse_read('fleta_config.cfg', 'screenshot', 'usage')
        except:
            self.b_screen = 'F'

        try:
            self.b_commands = self.cfg_parse_read('fleta_config.cfg', 'outcommands', 'usage')
        except:
            self.b_commands = 'F'

    def check_dir(self, s_save_path):
        if os.path.exists(s_save_path):
            pass
        else:
            try:
                os.mkdir(s_save_path)
            except:
                return False
        return True

    def get_version(self):
        s_file_name = self.s_agent_path + '/version_module'

        s_version = 'init'
        if os.path.isfile(s_file_name):
            o_f = open(s_file_name, 'r')
            s_version = o_f.read()
            o_f.close()
        return s_version.strip()

    def get_head_msg(self, s_title):
        s_head = "=" * 101
        s_head += "\n" + s_title.center(101, ' ')
        s_head += "\n" + "=" * 101

        return s_head

    def get_now_time(self):
        return strftime("%Y-%m-%d %H:%M:%S", localtime(time()))

    def get_contents_msg(self, s_msg):
        s_content = "\n" + s_msg

        return s_content

    def get_msg(self, s_title, s_msg):
        s_return_display = self.get_head_msg(s_title)
        s_return_display += self.get_contents_msg(s_msg)

        return s_return_display

    def get_agent_head_msg(self, s_title='FletaAgent Job Script'):
        s_execute_date = self.get_now_time()
        s_version = self.get_version()
        s_agent_head = ''

        s_agent_head = s_agent_head + '#' * 79 + '\n'
        s_agent_head = s_agent_head + '#   ' + ' ' * 74 + '#\n'
        s_agent_head = s_agent_head + '#   ' + 'Description  : ' + s_title.ljust(59) + '#\n'
        s_agent_head = s_agent_head + '#   ' + 'HOSTNAME     : ' + self.s_host_name.ljust(59) + '#\n'
        s_agent_head = s_agent_head + '#   ' + 'EXECUTE DATE : ' + s_execute_date.ljust(59) + '#\n'
        s_agent_head = s_agent_head + '#   ' + 'VERSION      : ' + s_version.ljust(59) + '#\n'
        s_agent_head = s_agent_head + '#   ' + ' ' * 74 + '#\n'
        s_agent_head = s_agent_head + '#' * 79 + '\n\n'

        return s_agent_head

    def get_agent_tail_msg(self, b_default_msg=True):
        s_agent_tail = '\n'

        if b_default_msg:
            s_fleta_config_path = self.s_config_path + 'fleta.cfg'

            # get fleta.cfg
            s_fleta_cfg = self.cfg_file_read('fleta.cfg')

            # get schedule
            s_sched_format = self.cfg_file_read('sched.format')

            # get user name
            try:
                import getpass
                s_user_name = getpass.getuser()
            except:
                s_user_name = ''

            s_agent_tail = s_agent_tail + '#' * 79 + '\n'
            s_agent_tail = s_agent_tail + 'CONFIG FILE : %s \n' % (s_fleta_config_path)
            s_agent_tail = s_agent_tail + '#' * 79 + '\n'
            s_agent_tail = s_agent_tail + '\n'
            s_agent_tail = s_agent_tail + '%s' % (s_fleta_cfg.strip())
            s_agent_tail = s_agent_tail + '\n\n'
            s_agent_tail = s_agent_tail + '#' * 79 + '\n'
            s_agent_tail = s_agent_tail + 'USER : %s \n' % (s_user_name)
            s_agent_tail = s_agent_tail + '#' * 79 + '\n'
            s_agent_tail = s_agent_tail + '\n'
            s_agent_tail = s_agent_tail + '#' * 79 + '\n'
            s_agent_tail = s_agent_tail + 'SCHEDULE : %s \n' % (s_sched_format)
            s_agent_tail = s_agent_tail + '#' * 79 + '\n'

        s_agent_tail = s_agent_tail + '\n'
        s_agent_tail = s_agent_tail + '#' * 79 + '\n'
        s_agent_tail = s_agent_tail + '#' * 79 + '\n'
        s_agent_tail = s_agent_tail + '#' * 11 + '  END : %s\n' % (self.get_now_time())
        s_agent_tail = s_agent_tail + '#' * 79 + '\n'
        s_agent_tail = s_agent_tail + '#' * 79 + '\n'

        return s_agent_tail

    def get_agent_default_msg(self):
        s_cfg_ip = self.cfg_parse_read('fleta.cfg', 'COMMON', 'agent_ip').strip()

        if s_cfg_ip:
            s_ip = s_cfg_ip
        else:
            s_ip = socket.gethostbyname(self.s_host_name)

        s_os = os.getenv('OS')

        if s_os is None:
            s_os_type = " ".join(platform.uname()) + self.s_host_name
        else:
            s_os_type = s_os + ' ' + self.s_host_name

        s_default_msg = '###***date time***###\n'
        s_default_msg += strftime('%Y%m%d%H%M%S') + '\n'
        s_default_msg += '\n###***uname -a***###\n'
        s_default_msg += '%s\n' % (s_os_type)
        s_default_msg += '\n###***host ip***###\n'
        s_default_msg += '%s is %s' % (self.s_host_name, s_ip)
        return s_default_msg

    def get_cmd_title_msg(self, s_cmd_name, b_title=True):
        if b_title:
            s_cmd_title = "\n###***%s***###\n" % (s_cmd_name.strip())
        else:
            s_cmd_title = "\n%s\n" % (s_cmd_name)
        try:
            self.log_control.logdata('AGENT', 'ACCESS', '30011', str(s_cmd_name))
        except:
            pass
        return s_cmd_title

    def cfg_read(self, s_file, ConfigParser=None):
        s_file_name = self.s_config_path + s_file
        o_config = ConfigParser.ConfigParser()
        o_config.read(s_file_name)
        return o_config

    def cfg_parse_write(self, s_file, s_items, s_set_key, s_set_val, ConfigParser=None):
        s_file_name = self.s_config_path + s_file
        a_config_contents = []

        if os.path.isfile(s_file_name):
            try:
                o_config = ConfigParser.ConfigParser()
                o_config.optionxform = str  # 대소문자 변환 금지.
                o_config.read(s_file_name)
                o_config.set(s_items, s_set_key, s_set_val)
                with open(s_file_name, 'wb') as configfile:
                    o_config.write(configfile)
            except:
                return False

        return True

    def cfg_parse_read(self, s_file, s_items, s_get_val=None):
        # s_file_name = self.s_config_path + s_file
        s_file_name = os.path.join(self.s_agent_path,'config',s_file)
        # print('config path :',self.s_config_path)
        # print('s_file_name',s_file_name,os.path.isfile(s_file_name))
        # print('s_items :', s_items, type(s_items))
        # print('s_get_val :', s_get_val, type(s_get_val))
        a_config_contents = []

        if os.path.isfile(s_file_name):

            o_config = configparser.ConfigParser()
            o_config.optionxform = str  # 대소문자 변환 금지.
            o_config.read(s_file_name)

            if s_get_val is None:
                # a_config_contents = o_config.read_dict(s_items)
                if s_items in o_config.keys():
                    a_config_contents = o_config[s_items]
            else:

                s_get_contents = o_config.get(s_items, s_get_val)
                # print('s_get_contents :', s_get_contents)
                return s_get_contents

        else:
            return s_file_name + " FILE NOT FOUND"

        if ON_POSIX is True:
            try:
                if isinstance(a_config_contents,list):

                    a_config_contents = list(sorted(set(a_config_contents)))
                    new_list = list()
                    for l_key in a_config_contents:
                        new_list.append(list(l_key))
                    a_config_contents = new_list
            except Exception as e:
                pass

        return a_config_contents

    def cfg_section_read(self, s_file, ConfigParser=None):
        s_file_name = self.s_config_path + s_file
        a_config_contents = []

        if os.path.isfile(s_file_name):
            try:
                o_config = ConfigParser.ConfigParser()
                o_config.optionxform = str  # 대소문자 변환 금지.
                o_config.read(s_file_name)
                a_config_contents = o_config.sections()
            except:
                pass
        return a_config_contents

    def file_write(self, s_file, s_contents, s_agent_path=True):

        if s_agent_path:
            s_file_name = os.path.join(self.s_agent_path, s_file)
        else:
            s_file_name = s_file
        if isinstance(s_contents,bytes):
            s_contents = s_contents.decode('utf-8')
        o_f = open(s_file_name, 'w')
        o_f.write(str(s_contents))
        o_f.close()

    def file_read(self, s_file, s_agent_path=True):

        if s_agent_path:
            s_file_name = os.path.join(self.s_agent_path, s_file)
        else:
            s_file_name = s_file
        if os.path.isfile(s_file_name):
            o_f = open(s_file_name, 'r')
            s_file_contents = o_f.read()
            o_f.close()
        else:
            return s_file_name + " FILE NOT FOUND"
        return s_file_contents

    def cfg_file_read(self, s_file):
        s_file_name = self.s_config_path + s_file

        if os.path.isfile(s_file_name):
            o_f = open(s_file_name, 'r')
            s_file_contents = o_f.read()
            o_f.close()
        else:
            return s_file_name + " FILE NOT FOUND"
        return s_file_contents

    def cfg_file_write(self, s_file, s_contents, IOErroras=None):
        s_file_name = self.s_config_path + s_file
        if os.path.isfile(s_file_name):
            try:
                o_f = open(s_file_name, 'w')
                o_f.write(s_contents)
                o_f.close()
            except IOErroras as e:
                return "%s 파일 Write 중 오류가 발생하였습니다. \n%s" % (s_contents, str(e))

            return True

    def data_file_wrtie(self, s_contents, a_save_type, b_start, e=None, IOErroras=None, unicode=None):
        # a_save_dir = self.tuple_to_dict(self.cfg_parse_read('fleta.cfg', 'save_dir'))
        # py36 add
        a_save_dir = self.cfg_parse_read('fleta.cfg', 'save_dir')
        s_check_type = a_save_type['check_type'] + '.' + a_save_type['execute_type']
        s_save_path = self.s_agent_path + a_save_dir[s_check_type]

        if self.check_dir(s_save_path):
            s_save_file_name = s_save_path + a_save_type['file_name']

            if b_start:
                s_write_type = 'w'
            else:
                s_write_type = 'a'

            with open(s_save_file_name,s_write_type) as f:
                f.write(s_contents)

            # o_f = open(s_save_file_name, s_write_type)
            #
            # if isinstance(s_contents,bytes):
            #     o_f.write(s_contents.encode('utf-8')+'\n')


            # o_f.close()

        else:
            print('directory not found')
        return True

    def screenshot(self, s_contents, a_save_type='', b_start=False, b_display=True, unicode=None):

        if self.b_screen == 'F':
            pass
        else:
            print('type :',type(s_contents))
            if isinstance(s_contents,bytes):
                s_contents = s_contents.decode('utf-8',"ignore")
                print('screenshot :',s_contents)

        self.data_file_wrtie(s_contents, a_save_type, b_start)

    def get_execute(self, s_cmd, e=None, Exceptionas=None):
        s_contents = ''

        try:
            if self.b_commands is 'F':
                o_p = Popen(s_cmd, shell=True, stdout=PIPE, stderr=PIPE, close_fds=ON_POSIX)
                # s_contents = o_p.stdout.read().strip()
                s_contents, stderr = o_p.communicate()

                if s_contents.strip() == '':
                    s_contents = stderr
            else:
                s_contents = os.popen(s_cmd.strip()).read()

            if s_contents != '' and sys.platform == "win32":
                s_contents = s_contents.replace('\r', '')
        except Exception as e:
            return "Command Error : %s \n %s" % (s_cmd, e)

        return s_contents

    def tuple_to_dict(self, a_tuple_tmp):
        # dict((x, y) for x, y in a_tuple_tmp)
        dict_map = dict()
        for key in a_tuple_tmp:
            dict_map[key] = a_tuple_tmp[key]
        return dict_map

    def get_user_pid_posix(self, s_process_name):
        if s_process_name.strip():
            i_uid_cnt = self.get_execute("ps -ef |grep %s | egrep -v \"su -|grep\" |wc -l" % s_process_name)
            if int(i_uid_cnt) > 0:
                s_userid = self.get_execute(
                    "cat /etc/passwd | grep `ps -ef |grep %s | egrep -v \"su -| grep\" |awk '{print $1;}'` |cut -d: -f1" % s_process_name)
            else:
                s_userid = ""
        return s_userid

    def get_db_head(self, s_db_type, s_instance='', s_user=''):
        import datetime
        s_msg = ''
        s_msg = s_msg + '#' * 50 + '\n'
        s_msg = s_msg + '#' + ('HOSTNAME : %s' % (self.s_host_name)).ljust(48) + '#\n'
        s_msg = s_msg + '#' + ('DATABASE : %s' % (s_db_type)).ljust(48) + '#\n'

        if s_instance != '':
            s_msg = s_msg + '#' + ('INSTANCE : %s' % (s_instance)).ljust(48) + '#\n'

        if s_user != '':
            s_msg = s_msg + '#' + ('USER     : %s' % (s_user)).ljust(48) + '#\n'

        s_msg = s_msg + '#' + ('DATE     : %s' % datetime.datetime.now()).ljust(48) + '#\n'
        s_msg = s_msg + '#' * 50 + '\n'
        return s_msg

    def posix_get_uid(self, s_uname):
        try:
            import pwd
            o_pw = pwd.getpwnam(s_uname)
            s_uid = o_pw.pw_uid
            return s_uid
        except:
            return None

