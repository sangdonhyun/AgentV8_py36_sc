#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2017.11.10
    @author: jhbae
'''
import os
import re
import sys
from lib import common
from subprocess import Popen, PIPE

class DbInfoOracleExecute():
    def __init__(self):
        self.o_common = common.Common()

    def get_execute(self, s_cmd, s_switch_user=None):
        s_contents = ''
        i_uid = None

        if s_switch_user != None:
            i_uid = self.o_common.posix_get_uid(s_switch_user)

        if i_uid != None :
            i_uid = int(i_uid)
        try :
            ON_POSIX = 'posix' in sys.builtin_module_names

            if 'posix' in sys.builtin_module_names:
                if i_uid:
                    o_p = Popen(s_cmd, shell=True, stdout=PIPE, close_fds=False, preexec_fn=self.preexec_fn(i_uid))
                else:
                    o_p = Popen(s_cmd, shell=True, stdout=PIPE, close_fds=ON_POSIX)
            s_contents , stderr = o_p.communicate()

        except Exception as e:
            return "ERROR : Command Error => %s \n %s" % (s_cmd, str(e))

        if s_contents.strip() == '':
            s_contents = stderr

        return s_contents

    def preexec_fn(self, i_uid):
        def set_ids():
            os.setuid(i_uid)
        return set_ids

    def get_oracle_path(self, s_oracle_user):

        s_cmd = "ps -ef |grep tnslsnr | awk '{if ($1 == \"%s\") {print $0}}'|sort|uniq" % (s_oracle_user)
        s_res = self.get_execute(s_cmd)

        if s_res == '':
            # s_cmd = "ps -ef |grep d.bin |awk '{if ($1 == \"%s\") { print system(\"dirname \" $NF)}}'|grep \"/bin\"|sort|uniq" % (s_oracle_user)
            s_cmd = "ps -ef |grep d.bin |awk '{if ($1 == \"%s\") {print $0}}'|sort|uniq" % (s_oracle_user)
            s_res = self.get_execute(s_cmd)

        s_oracle_bin_path = ''
        if s_res != '':
            if isinstance(s_res,bytes):
                s_res = s_res.decode('utf-8')
            a_res = s_res.split('\n')

            for s_ps_proc in a_res:
                a_ps_proc = re.findall("/.+/", s_ps_proc)
                try:
                    s_ps_proc_path = a_ps_proc[0]

                    if os.path.isdir(s_ps_proc_path):
                        o_regex = re.compile(r'.+(\/grid\/).+\/bin\/')
                        o_matchobj = o_regex.search(s_ps_proc_path)
                        s_oracle_bin_path = re.sub(o_matchobj.group(1), '/product/', s_ps_proc_path)

                        if s_oracle_bin_path.endswith('/bin/'):
                            s_oracle_bin_path = s_oracle_bin_path.rstrip('/bin/')
                except Exception as e:
                    print(str(e))
                    pass

        return s_oracle_bin_path

    def get_oracle_grid_path(self, s_oracle_user):
        s_cmd = "ps -ef |grep d.bin |awk '{if ($1 == \"%s\") { print system(\"dirname \" $NF)}}'|grep \"/bin\"|sort|uniq" % (s_oracle_user)

        s_res = self.get_execute(s_cmd)
        s_oracle_bin_path = ''

        s_path_val = ''
        if s_res != '':
            if isinstance(s_res,bytes):
                s_res = s_res.decode('utf-8')
            a_res = s_res.split('\n')
            if os.path.isdir(a_res[0]):
                if a_res[0].endswith('/bin'):
                    s_oracle_bin_path = a_res[0]


            s_path = os.getenv("PATH")
            a_path = s_path.split(":")

            if s_oracle_bin_path not in a_path:
                a_path.insert(0, s_oracle_bin_path)
            s_path_val = ":".join(a_path)
            os.environ['PATH'] = s_path_val
