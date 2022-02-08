# -*- coding: utf-8 -*-
'''
    Created on 2016.08.30
    @author: jhbae
'''
import os
import sys
import platform
import base64
import re
import urllib
import time
import datetime
import hashlib
import tarfile
import socket
import configparser
from subprocess import Popen, PIPE
import py_compile


class CusCommon():
    def __init__(self):
        self.s_agent_path = ''
        o_config = configparser.ConfigParser()
        s_current_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])))

        if os.path.isfile(os.path.join(s_current_path, 'config', 'fleta.cfg')):
            o_config.read(os.path.join(s_current_path, 'config', 'fleta.cfg'))
            self.s_agent_path = o_config.get('COMMON', 'home_dir')
            self.s_version_check = o_config.get('COMMON', 'version_check')

        if self.s_agent_path.strip() == '':
            self.s_agent_path = s_current_path

        self.s_config_path = os.path.join(self.s_agent_path, 'config')
        self.s_host_name = socket.gethostname()
        #20220204 log path :
        # self.LOG_PATH = os.path.join(s_current_path, 'logs')
        try:
            self.LOG_PATH = o_config.get('log', 'log_path')
        except Exception as e:
            print(str(e))
            self.LOG_PATH = os.path.join(s_current_path, 'logs')

        self.CONFIG_LOG_CODE = os.path.join(s_current_path, "config", "logcode.cfg")
        self.o_log_code = configparser.ConfigParser()
        self.o_log_code.read(self.CONFIG_LOG_CODE)

    def cfg_parse_write(self, s_file, s_items, s_set_key, s_set_val):
        s_file_name = self.s_config_path + s_file
        a_config_contents = []

        if os.path.isfile(s_file_name):
            try:
                o_config = configparser.ConfigParser()
                o_config.optionxform = str  # 대소문자 변환 금지.
                o_config.read(s_file_name)
                o_config.set(s_items, s_set_key, s_set_val)
                with open(s_file_name, 'wb') as configfile:
                    o_config.write(configfile)
            except:
                return False

        return True

    def cfg_file_read(self, s_file):
        s_file_name = self.s_config_path + s_file

        if os.path.isfile(s_file_name):
            o_f = open(s_file_name, 'r')
            s_file_contents = o_f.read()
            o_f.close()
        else:
            return s_file_name + " FILE NOT FOUND"
        return s_file_contents

    def cfg_parse_read(self, s_file, s_items, s_get_val=None, s_path=False):
        if s_path:
            s_file_name = self.s_agent_path + '/' + s_file
        else:
            s_file_name = self.s_config_path + '/' + s_file
        a_config_contents = []

        if os.path.isfile(s_file_name):
            try:
                o_config = configparser.ConfigParser()
                o_config.optionxform = str  # 대소문자 변환 금지.
                o_config.read(s_file_name)

                if s_get_val is None:
                    a_config_contents = o_config.items(s_items)
                else:
                    s_get_contents = o_config.get(s_items, s_get_val)
                    return s_get_contents
            except:
                pass
        else:
            return s_file_name + " FILE NOT FOUND"
        return a_config_contents

    def file_read(self, s_file, s_agent_path=True):

        if s_agent_path:
            s_file_name = self.s_agent_path + '/' + s_file
        else:
            s_file_name = s_file
        if os.path.isfile(s_file_name):
            o_f = open(s_file_name, 'r')
            s_file_contents = o_f.read()
            o_f.close()
        else:
            return s_file_name + " FILE NOT FOUND"

        return s_file_contents

    def logdata(self, s_file_name, s_file_type, s_code='', s_refer_val=''):
        if os.path.isdir(self.LOG_PATH) == False:
            os.makedirs(self.LOG_PATH)
        s_refer_val = str(s_refer_val)
        s_data = "[%s] " % (s_code) + self.o_log_code.get('CODE', s_code)
        if s_refer_val != '':
            s_data = s_data + " ==> " + s_refer_val

        today = time.strftime("%Y%m%d", time.localtime(time.time()))
        # filefullname = LOG_PATH + s_file_name + "_" + str(today) + "_" + s_file_type + ".log"
        filefullname = os.path.join(self.LOG_PATH, str(today) + "_" + s_file_name + "_" + s_file_type + ".log")
        try:
            fp = open(filefullname, 'a')
            now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            comment = "[" + str(now) + "] " + str(s_data) + "\n"
            print(comment)
            print(filefullname)
            fp.write(comment)
            fp.close()
        except Exception as e:
            print(str(e))


class VersionCheck():
    def __init__(self):
        self.o_common = CusCommon()
        # fleta recv get ip
        # s_current_ip = self.cfg_parse_read('fleta.cfg', 'COMMON', 'agent_ip')
        # print('s_current_ip',s_current_ip)
        s_current_ip = self.o_common.cfg_parse_read('fleta.cfg', 'COMMON', 'agent_ip')
        # print('s_current_ip', s_current_ip)
        if s_current_ip:
            pass
        else:
            self.set_ip()

        self.s_current_cfg_version = self.o_common.file_read('version_cfg').strip()
        self.s_current_module_version = self.o_common.file_read('version_module').strip()
        self.file_install_path = os.path.join(self.o_common.s_agent_path, 'patch', 'install')
        self.file_rollback_path = os.path.join(self.o_common.s_agent_path, 'patch', 'rollback')
        self.a_uname = platform.uname()
        self.s_machine = platform.machine()
        self.s_os_type = self.a_uname[0]
        if self.s_os_type.upper() == 'AIX':
            self.s_os_ver = "%s.%s" % (str(self.a_uname[3]), str(self.a_uname[2]))
        else:
            self.s_os_ver = self.a_uname[2]
        self.s_srm_ip = self.o_common.cfg_parse_read('fleta.cfg', 'srm', 'srm_ip')
        self.s_srm_port = self.o_common.cfg_parse_read('fleta.cfg', 'srm', 'srm_port')
        self.s_agent_port = self.o_common.cfg_parse_read('fleta.cfg', 'COMMON', 'agent_port')

        if self.s_srm_ip == '':
            print
            'SRM SERVER IP NOT FOUND'
            sys.exit()

        self.s_srm_http = "%s:%s" % (self.s_srm_ip, self.s_srm_port)
        self.a_ver_msg = {
            'srm': 'Connection OK'
            , 'patch': ''
            , 'patch_res': ''
        }

        b_daemon = self.daemon_check()
        b_sched_daemon_check = self.sched_daemon_check()

        if b_sched_daemon_check is True:
            b_sched_daemon_check = 'T'
        else:
            b_sched_daemon_check = 'F'

        self.a_info = {
            'ip': ''
            , 'hostname': self.o_common.s_host_name
            , 'version_cfg': ''
            , 'version_module': ''
            , 'sys_os': self.s_os_type
            , 'sys_ver': self.s_os_ver
            , 'sys_bit': ''
            , 'daemon_bit': str(b_daemon)
            , 'sched_bit': str(b_sched_daemon_check)
            , 'sys_type': ''
        }

        self.patch_file = ''
        self.s_err_msg = '-'

    def _en(self, _in):
        return base64.b64encode(_in)

    def fenc(self, s_str):
        s_encode_tmp = self._en(s_str)
        s_encode = self._en(s_encode_tmp)

        s_encode_hash = hashlib.md5(s_encode_tmp).hexdigest()
        s_encode = s_encode.replace('=', '@')
        s_encode_val = s_encode + '@' + s_encode_hash
        return s_encode_val

    def set_ip(self):

        a_info = {}
        s_data = ''
        a_info['FLETA_PASS'] = 'kes2719!'
        a_info['MYIP'] = 'kes2719!'
        s_info_data = self.fenc(str(a_info))

        s_socket_host = self.o_common.cfg_parse_read('fleta.cfg', 'socket', 'server')
        s_socket_port = self.o_common.cfg_parse_read('fleta.cfg', 'socket', 'port')

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
                        else:
                            s_data = s_ip
                            break
                    else:
                        host_name = os.popen('hostname').read()
                        s_data = os.popen("cat /etc/hosts | grep %s | awk '{ print $1 }'" % (host_name)).read()
                        # print "ip address : %s" %(s_data)
            except:
                s_data = ''

        if s_data.strip() == '':
            print
            '[ERROR] IP SET ERROR - No Match IP Address'
            sys.exit(1)
        else:
            b_rtn = self.o_common.cfg_parse_write('fleta.cfg', 'COMMON', 'agent_ip', s_data)
            if b_rtn is False:
                print
                '[ERROR] IP SET ERROR - fleta.cfg Write Error'
                sys.exit(1)

            self.o_common.cfg_parse_write('fleta.cfg', 'COMMON', 'home_dir', self.o_common.s_agent_path)

    def is_valid_ip(self, s_ip):
        m = re.match(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$", s_ip)
        return bool(m) and all(map(lambda n: 0 <= int(n) <= 255, m.groups()))

    def sched_daemon_check(self):
        if sys.platform == 'win32':  # Windows
            process = Popen(
                'tasklist.exe /FO CSV /FI "IMAGENAME eq %s"' % 'fleta_schedule.exe',
                stdout=PIPE, stderr=PIPE,
                universal_newlines=True)
            out, err = process.communicate()
            try:
                return out.split("\n")[1].startswith('"fleta_schedule.exe"')
            except:
                return False

        else:  # Posix
            try:
                o_p = os.popen("ps -ef |grep fleta_s|grep -v 'grep'|wc -l", "r")
                i_proc_cnt = o_p.read().strip()
                if int(i_proc_cnt) > 0:
                    return True
                else:
                    return False
            except:
                return False

    def daemon_check(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        print
        self.s_agent_port
        result = sock.connect_ex(('127.0.0.1', int(self.s_agent_port)))
        if result == 0:
            b_daemon = 'T'
        else:
            b_daemon = 'F'
        return b_daemon

    def get_info(self):
        self.s_cfg_version = self.o_common.file_read('version_cfg').strip()
        self.s_module_version = self.o_common.file_read('version_module').strip()

        if len(self.s_cfg_version) < 1:
            self.s_cfg_version = 'init'
        if len(self.s_module_version) < 1:
            self.s_module_version = 'init'

        s_cfg_ip = self.o_common.cfg_parse_read('fleta.cfg', 'COMMON', 'agent_ip')
        if s_cfg_ip:
            s_ip = s_cfg_ip
        else:
            s_ip = socket.gethostbyname(self.o_common.s_host_name)

        if re.search('32', self.s_machine):
            i_bit = 32
        else:
            i_bit = 64

        s_sys_type = ''
        if re.search('windows', self.s_os_type.lower()):
            s_sys_type = 'windows' + '_' + str(i_bit)
        else:
            s_sys_type = 'posix'

        s_cron = self.o_common.cfg_file_read('sched.format')

        self.a_info['ip'] = s_ip
        self.a_info['sys_bit'] = str(i_bit)
        self.a_info['sys_type'] = s_sys_type
        self.a_info['daemon_port'] = self.s_agent_port
        self.a_info['version_cfg'] = self.s_cfg_version
        self.a_info['version_module'] = self.s_module_version
        self.a_info['cron'] = s_cron
        return self.a_info

    def file_download(self, s_patch_info):
        b_return = True
        a_patch_info = s_patch_info.split("||")
        s_down_path = ''

        if len(a_patch_info) > 2:
            s_patch_file_name = os.path.basename(a_patch_info[0])
            s_down_path = 'http://%s/patch/%s' % (self.s_srm_http, s_patch_file_name)

            s_checksum = a_patch_info[1].strip()
            s_file_size = a_patch_info[2].strip()
            self.patch_file = s_patch_file_name

        if s_down_path == '':
            return False

        o_ret_url = urllib.urlopen(s_down_path)

        if o_ret_url.code == 200:
            s_save_file_path = self.file_install_path + s_patch_file_name
            urllib.urlretrieve(s_down_path, s_save_file_path)

            if os.path.isfile(s_save_file_path) == True and int(os.path.getsize(s_save_file_path)) == int(s_file_size):
                s_down_file_md5 = hashlib.md5(open(s_save_file_path, 'rb').read()).hexdigest()
                if s_down_file_md5 != s_checksum:
                    self.o_common.logdata('AGENT', 'ERROR', '20003', str(s_save_file_path))
                    b_return = False
            else:
                b_return = False
                s_rtn = s_save_file_path + "," + str(os.path.getsize(s_save_file_path)) + "," + str(s_file_size)
                self.o_common.logdata('AGENT', 'ERROR', '20005', s_rtn)
        else:
            self.o_common.logdata('AGENT', 'ERROR', '20004', str(o_ret_url.code))
            b_return = False
        return b_return

    def patch_stream(self, s_patch_info, s_flag='ins', b_status=True, s_message=''):
        b_res = False

        if b_status:
            s_status = 'T'
        else:
            s_status = 'F'

        if s_patch_info.strip() != '':
            a_patch_info = s_patch_info.split('@2@')
        else:
            return False

        if len(a_patch_info) < 2:
            pass
        else:

            s_patch = a_patch_info[0]
            s_patch_idx = a_patch_info[1]
            s_current_cfg_version = self.s_cfg_version
            s_current_module_version = self.s_module_version
            s_param = 'ip=%s&hostname=%s&version=%s&flag=%s&message=%s&status=%s&version_cfg=%s&version_module=%s&patch_idx=%s' % (
            self.a_info['ip'], self.a_info['hostname'], s_patch, s_flag, s_message, s_status, s_current_cfg_version,
            s_current_module_version, s_patch_idx)
            s_url = 'http://%s/agent_patch_history.jsp?%s' % (self.s_srm_http, s_param)

            s_url_res = ''

            try:
                o_url_res = urllib.urlopen(s_url)
                if o_url_res.code == 200:
                    if s_flag == 'ins':
                        s_url_res = o_url_res.read().strip()

                        b_res = self.file_download(s_url_res)

                    elif s_flag == 'upd':
                        s_res = o_url_res.read().strip()
                        if str(s_res) == '1':
                            b_res = True
                else:
                    self.o_common.logdata('AGENT', 'ERROR', '20009', str(o_url_res.code))
            except Exception as e:
                self.o_common.logdata('AGENT', 'ERROR', '20002', str(e))
        return b_res

    def get_health_check(self):
        a_get_info_tmp = []
        s_url_res = ''

        try:
            o_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            o_sock.settimeout(2)
            o_sock.connect((self.s_srm_ip, int(self.s_srm_port)))
        except:
            self.o_common.logdata('AGENT', 'ERROR', '20012')
            return 'FAIL'

        for s_key, s_val in self.get_info().items():
            a_get_info_tmp.append(s_key + '=' + s_val)

        if self.s_srm_http:
            s_param = "&".join(a_get_info_tmp)
            s_url = 'http://%s/agent_health.jsp?%s' % (self.s_srm_http, s_param)

        try:
            s_url_res = urllib.urlopen(s_url).read().strip()
        except:
            self.o_common.logdata('AGENT', 'ERROR', '20001', s_url)
            return 'FAIL'
        return s_url_res

    def remove_files(self, a_tar_file_list):
        if len(a_tar_file_list) > 0:
            # #원본 파일 삭제
            if sys.platform != 'win32':
                s_current_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])))
                for s_file_name in a_tar_file_list:
                    if s_file_name.endswith('.py'):
                        try:
                            py_compile.compile(os.path.join(s_current_path, s_file_name))
                            self.o_common.logdata('AGENT', 'ACCESS', '20011', str(s_file_name))
                            os.remove(os.path.join(s_current_path, s_file_name))
                        except Exception as e:
                            self.o_common.logdata('AGENT', 'ERROR', '20010', str(s_file_name))
                            self.o_common.logdata('AGENT', 'ERROR', '20010', str(e))

    def tar_uncompress(self):
        b_uncompress = True

        FILE_ROLLBACK_PATH = self.file_rollback_path
        FILE_INSTALL_PATH = self.file_install_path

        if os.path.isdir(FILE_ROLLBACK_PATH) == True:
            s_down_tar_file = FILE_INSTALL_PATH + self.patch_file

            if os.path.isfile(s_down_tar_file) == True:
                try:
                    with tarfile.open(s_down_tar_file, "r") as o_tar:
                        a_tar_file_list = o_tar.getnames()

                        s_arc_rollback_name = FILE_ROLLBACK_PATH + self.patch_file.replace('.tar', '') + '_ROLLBACK.tar'
                        o_archive_tar = tarfile.open(s_arc_rollback_name, 'w')

                        for s_arc_file_tmp in a_tar_file_list:
                            if sys.platform != 'win32':
                                if s_arc_file_tmp.endswith('.py'):
                                    s_arc_file = self.o_common.s_agent_path + '/' + s_arc_file_tmp + 'c'
                                else:
                                    s_arc_file = self.o_common.s_agent_path + '/' + s_arc_file_tmp
                            else:
                                s_arc_file = self.o_common.s_agent_path + '/' + s_arc_file_tmp
                            if os.path.isfile(s_arc_file):
                                o_archive_tar.add(s_arc_file)
                        o_archive_tar.close()

                        if os.path.isfile(s_arc_rollback_name) == True:
                            try:
                                o_tar.extractall(self.o_common.s_agent_path + '/')
                            except Exception as s_err_msg:
                                self.s_err_msg = s_err_msg
                                self.o_common.logdata('AGENT', 'ERROR', '20007', str(s_err_msg))
                                b_uncompress = False
                        else:
                            self.s_err_msg = 'rollback file not found'
                            self.o_common.logdata('AGENT', 'ERROR', '20006')
                            b_uncompress = False
                    o_tar.close()
                except Exception as s_err_msg:
                    self.s_err_msg = s_err_msg
                    self.o_common.logdata('AGENT', 'ERROR', '20007', str(s_err_msg))
                    b_uncompress = False
                finally:
                    self.remove_files(a_tar_file_list)
        else:

            s_err_msg = 'rollback directory is not found'
            self.o_common.logdata('AGENT', 'ERROR', '20008', str(s_err_msg))
            b_uncompress = False
        return b_uncompress

    def version_msg(self):
        if self.a_ver_msg['patch'] == '':
            b_patch = 'NO'
        else:
            b_patch = 'YES'
        print( "#" * 40)
        print("Version Check".rjust(25))
        print
        print(" - Patch Server Connection")
        print("\t SERVER STATUS : " + str(self.a_ver_msg['srm']))
        print("\t Patch availability : " + str(b_patch))
        print
        print(" - Agent Current Version")
        print("\t CFG VERSION    : %s" % (self.s_current_cfg_version))
        print("\t MODULE VERSION : %s" % (self.s_current_module_version))

        if self.a_ver_msg['patch_res']:
            print
            print(" - Patch Version")
            print("\t CFG VERSION    : %s" % (self.o_common.file_read('version_cfg')))
            print("\t MODULE VERSION : %s" % (self.o_common.file_read('version_module')))
        print("#" * 40)

    def log_remove(self):
        i_log_remove = self.o_common.cfg_parse_read('fleta.cfg', 'log', 'log_remove')
        s_log_path = self.o_common.LOG_PATH

        # 삭제 주기 : 0 일경우 365일 기준으로 삭제
        if int(i_log_remove) < 1:
            i_log_remove = 365

        # ago time check
        days_ago = datetime.datetime.now() - datetime.timedelta(days=int(i_log_remove))
        i_ago_timestamp = time.mktime(days_ago.timetuple())

        if os.path.isdir(s_log_path):
            a_filenames = os.listdir(s_log_path)
            for s_filename in a_filenames:
                s_full_filename = os.path.join(s_log_path,s_filename)
                s_ext = os.path.splitext(s_full_filename)[-1]
                if s_ext == '.log':
                    o_file_stat = os.stat(s_full_filename)
                    i_log_m_time = int(o_file_stat.st_mtime)
                    if int(i_log_m_time) < int(i_ago_timestamp):
                        os.remove(s_full_filename)

    def block_process_check(self):
        if sys.platform != 'win32':  # Posix
            s_s_pid_number = ''
            s_d_pid_number = ''

            s_s_pid_file = os.path.join(self.o_common.s_agent_path, 'pid/fleta_schedule.pid')
            s_d_pid_file = os.path.join(self.o_common.s_agent_path, 'pid/fleta_daemon.pid')
            try:
                if os.path.isfile(s_s_pid_file):
                    o_f = open(s_s_pid_file, 'r')
                    s_s_pid_number = o_f.read().strip()
                    o_f.close()
                if os.path.isfile(s_d_pid_file):
                    o_f2 = open(s_d_pid_file, 'r')
                    s_d_pid_number = o_f2.read().strip()
                    o_f2.close()

                a_pid_number = [s_s_pid_number, s_d_pid_number]
                o_p = os.popen("ps -ef |grep fleta_ |egrep -v 'grep|fleta_d' |awk '{print $2}'", "r")
                a_proc_id = o_p.read().strip().split('\n')

                if len(a_proc_id) > 1:
                    for s_proc in a_proc_id:
                        if s_proc not in a_pid_number:
                            os.system('kill %s' % s_proc)
            except:
                pass

    def main(self):

        self.log_remove()

        self.block_process_check()
        if self.o_common.s_version_check == 'F':
            return False

        b_update = False
        b_rtn = False
        s_status = self.get_health_check()

        if s_status == 'OK':
            b_update = True

        elif s_status == 'FAIL':
            b_update = False
            self.a_ver_msg['srm'] = 'Connection Fail'

        elif re.search('PATCH_', s_status):
            s_patch_check_val = re.sub('^PATCH_', '', s_status)
            self.a_ver_msg['patch'] = 'YES'

            if re.search('@3@', s_patch_check_val):
                for s_patch_check in s_patch_check_val.split('@3@'):
                    b_ins = self.patch_stream(s_patch_check, s_flag='all_ins', b_status=True)
                    if b_ins:
                        b_rtn = self.tar_uncompress()

                    b_update = self.patch_stream(s_patch_check, s_flag='all_upd', b_status=b_rtn,
                                                 s_message=self.s_err_msg)
                self.a_ver_msg['patch_res'] = True
            else:
                b_ins = self.patch_stream(s_patch_check_val, s_flag='ins', b_status=True)
                if b_ins:
                    b_rtn = self.tar_uncompress()

                b_update = self.patch_stream(s_patch_check_val, s_flag='upd', b_status=b_rtn, s_message=self.s_err_msg)

                self.a_ver_msg['patch_res'] = b_update
            self.get_health_check()
        self.version_msg()
        return b_update


if __name__ == "__main__":
    print
    VersionCheck().main()
