# -*- coding: utf-8 -*-
'''
    Created on 2018.04.18
    @author jhbae
'''
import os
import sys
import time
import re
import datetime
import urllib.request, urllib.parse, urllib.error
import subprocess

from .common import Common
from .file_transfer import FileTransfer

class FletaSymEvent():
    def __init__(self):
        self.o_common = Common()
        self.o_file_transfer = FileTransfer()
        # sym cmd path add
        self.sym_cmd_path()

    def sym_cmd_path(self):
        s_sym_cmd_dir = self.o_common.cfg_parse_read('symEvent.cfg', 'PATH', 'path')
        try:
            if sys.platform == "win32":
                os.environ['PATH'] = ';'.join([s_sym_cmd_dir, os.getenv('PATH')])
            else:
                os.environ['PATH'] = ':'.join([s_sym_cmd_dir, os.getenv('PATH')])
        except:
            pass

    def getNow(self, s_time_format='%Y-%m-%d %H:%M:%S'):
        return time.strftime(s_time_format)

    def get30Min(self , s_time_format='%m/%d/%Y:%H:%M:00'):
        s_now = datetime.datetime.now()
        s_tdate = s_now - datetime.timedelta(minutes=30)
        s_date_time = s_tdate.strftime(s_time_format)
        return s_date_time

    def getEvtMsg10(self):
        s_date_time = self.get30Min()
        s_cmd = 'symevent list -start %s' % s_date_time
        return s_cmd

    def execute(self, s_cmd):
        o_p = subprocess.Popen(s_cmd.split(), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out, err = o_p.communicate()

        if err is None :
            return out
        else :
            return err

    def symEventExecute(self):
        s_cdate = self.getNow('%Y%m%d%H%M00')
        s_bdate = self.get30Min('%Y%m%d%H%M00')

        a_save_type = {
                        'file_name' : "%s_%s_%s.tmp" % (self.o_common.s_host_name, s_cdate, s_bdate)
                       , 'check_type' : 'SYM'
                       , 'execute_type' : 'EVENT'
                    }
        # header
        s_title = 'SYM EVENT'
        self.o_common.screenshot(self.o_common.get_agent_head_msg(s_title), a_save_type=a_save_type, b_start=True)

        # date
        self.o_common.screenshot(self.o_common.get_cmd_title_msg('date'), a_save_type=a_save_type)
        self.o_common.screenshot(s_cdate, a_save_type=a_save_type)

        # start time
        self.o_common.screenshot(self.o_common.get_cmd_title_msg('starttime'), a_save_type=a_save_type)
        self.o_common.screenshot(s_bdate, a_save_type=a_save_type)

        # Sym Event
        s_cmd = self.getEvtMsg10()
        s_rtn = self.execute(s_cmd)
        self.o_common.screenshot(self.o_common.get_cmd_title_msg('symevent'), a_save_type=a_save_type)
        self.o_common.screenshot(s_rtn, a_save_type=a_save_type)
        self.o_common.screenshot(self.o_common.get_agent_tail_msg(False), a_save_type=a_save_type)

        s_save_path = self.o_common.s_agent_path + self.o_common.cfg_parse_read('fleta.cfg', 'save_dir', 'SYM.EVENT')
        s_out_file = os.path.join(s_save_path, a_save_type['file_name'])

        # File Transfer
        a_res = {}
        b_rtn = False

        if os.path.isfile(s_out_file) and os.path.getsize(s_out_file) > 0:
            a_res['SYM.EVENT'] = True
            b_rtn = self.o_file_transfer.main(a_res, b_remove=True)
        self.end_msg(b_rtn, s_out_file)

    def end_msg(self, b_status, s_out_file):
        if b_status:

            print('#' * 40)
            print('SymEvent Check Success')
            print('#' * 40)
        else:
            print('#' * 40)
            print('SymEvent Check FAIL Transfer Error')
            print('#' * 40)

    def url_check(self):
        # symEventcheck
        s_cfg_url = self.o_common.cfg_parse_read('symEvent.cfg', 'CHECKURL', 'url')
        s_event_usage = self.o_common.cfg_parse_read('symEvent.cfg', 'SYMEVENT', 'usage')
        s_srm_ip = self.o_common.cfg_parse_read('fleta.cfg', 'srm', 'srm_ip')
        s_srm_port = self.o_common.cfg_parse_read('fleta.cfg', 'srm', 'srm_port')
        s_ip = self.o_common.cfg_parse_read('fleta.cfg', 'COMMON', 'agent_ip')

        s_param = '?serverIp=%s&serverNm=%s&event=%s' % (s_ip, self.o_common.s_host_name,s_event_usage)

        if s_cfg_url == '':
            return False

        try :
            s_cfg_url = re.sub('^\/{1,2}', '', s_cfg_url)

            s_url = 'http://%s:%s/%s' % (s_srm_ip, s_srm_port, s_cfg_url) + s_param
            o_url_res = urllib.request.urlopen(s_url)
            if o_url_res.code == 200:
                s_read_val = o_url_res.read().strip().upper()
                if s_read_val == 'T':
                    return True
                else:
                    return False
            else:
                return False
        except:
            return False

    def symEvent(self):
        if self.url_check() is True:
            self.symEventExecute()
