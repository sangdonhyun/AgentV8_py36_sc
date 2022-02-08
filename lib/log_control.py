#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2016.05.17
    @author: jhbae
'''
import time
import os
import sys
import configparser

s_agent_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])))


# CONFIG_LOG_CODE = s_agent_path + "/config/logcode.cfg"



class LogControl(object):
    def __init__(self):
        self.logPath=self.getLogPath()
        CONFIG_LOG_CODE = os.path.join(s_agent_path ,'config','logcode.cfg')
        self.o_log_code = configparser.ConfigParser()
        self.o_log_code.read(CONFIG_LOG_CODE)
    def getLogPath(self):
        
        cfg=configparser.RawConfigParser()
        cfgFile=os.path.join(s_agent_path,'config','fleta.cfg')
        cfg.read(cfgFile)
        
        try:
            LOG_PATH= cfg.get('log','log_path').strip()
            
            if LOG_PATH == '':
                LOG_PATH = os.path.join(s_agent_path,'logs')
        except:
            LOG_PATH = os.path.join(s_agent_path,'logs')
        if not os.path.isdir(LOG_PATH):
            os.makedirs(LOG_PATH)
        return LOG_PATH
    
    def logdata(self, s_file_name, s_file_type, s_code='', s_refer_val=''):
        if os.path.isdir(self.logPath) == False:
            os.makedirs(self.logPath)
        s_refer_val = str(s_refer_val)
        s_data = "[%s] " % (s_code) + self.o_log_code.get('CODE', s_code)
        if s_refer_val != '':
            s_data = s_data + " ==> " + s_refer_val

        today = time.strftime("%Y%m%d", time.localtime(time.time()))
        # filefullname = LOG_PATH + s_file_name + "_" + str(today) + "_" + s_file_type + ".log"
        filefullname = os.path.join(self.logPath, str(today) + "_" + s_file_name + "_" + s_file_type + ".log")
        try:
            fp = open (filefullname, 'a')
            now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            comment = "[" + str(now) + "] " + str(s_data) + "\n"
            print(comment)
            print(filefullname)
            fp.write(comment)
            fp.close()
        except Exception as e:
            print(str(e))

if __name__=='__main__':
    LogControl().logdata('AGENT', 'ERROR', '20012')
