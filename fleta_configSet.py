'''
Created on 2019. 11. 8.

@author: Administrator
'''

import os
import sys
import re
import socket
import configparser
import lib.common
from io import StringIO
import fleta_diskinfo
import version_check
import subprocess

class ConfigSset():
    def __init__(self):
        self.o_common = lib.common.Common()
        self.s_aes_cipher = self.o_common.s_aes_cipher
        self.setup_cfg = self.get_setup_cfg()
        self.s_current_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])))


    def get_setup_cfg(self):
        cfgFile=os.path.join('config','HSRM.ini')
        cfg=configparser.RawConfigParser()
        cfg.read(cfgFile)
        print(os.path.isfile(cfgFile))
        return cfg
    
    def get_agent_ip(self): 
        try: 
            host_name = socket.gethostname() 
            host_ip = socket.gethostbyname(host_name) 
#             print("Hostname :  ",host_name) 
#             print("IP : ",host_ip)
             
        except: 
            print("Unable to get Hostname and IP")
        return host_ip 
            
    
    
    def is_valid_ipv4(self,ip):
        """Validates IPv4 addresses.
        """
        pattern = re.compile(r"""
            ^
            (?:
              # Dotted variants:
              (?:
                # Decimal 1-255 (no leading 0's)
                [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
              |
                0x0*[0-9a-f]{1,2}  # Hexadecimal 0x0 - 0xFF (possible leading 0's)
              |
                0+[1-3]?[0-7]{0,2} # Octal 0 - 0377 (possible leading 0's)
              )
              (?:                  # Repeat 0-3 times, separated by a dot
                \.
                (?:
                  [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
                |
                  0x0*[0-9a-f]{1,2}
                |
                  0+[1-3]?[0-7]{0,2}
                )
              ){0,3}
            |
              0x0*[0-9a-f]{1,8}    # Hexadecimal notation, 0x0 - 0xffffffff
            |
              0+[0-3]?[0-7]{0,10}  # Octal notation, 0 - 037777777777
            |
              # Decimal notation, 1-4294967295:
              429496729[0-5]|42949672[0-8]\d|4294967[01]\d\d|429496[0-6]\d{3}|
              42949[0-5]\d{4}|4294[0-8]\d{5}|429[0-3]\d{6}|42[0-8]\d{7}|
              4[01]\d{8}|[1-3]\d{0,9}|[4-9]\d{0,8}
            )
            $
        """, re.VERBOSE | re.IGNORECASE)
        return pattern.match(ip) is not None
    
    
    
    def set_config(self,agent_ip):
        cfgcontent="""
[ftp]
server = 121.170.193.207
user = fletaFTP
timeout = 5
pass = MfmNWa/dtZt6SN+m0rbfpg==
port = 21

[socket]
port = 54002
server = 121.170.193.207

[systeminfo]
set_device = FS
diskcheck = WMI

[srm]
srm_port = 80
srm_ip = 121.170.193.207

[COMMON]
agent_ip = 10.10.10.68
version_check = T
transfer = SOCKET
home_dir = D:\workspace\agentV8
agent_port = 54001
agent_execute = 10

[save_dir]


[log]
log_remove = 30
        """
        cfgFile=os.path.join('config','fleta.cfg')
        
        cfg=configparser.RawConfigParser()
        cfg.optionxform = str
        print(os.path.isfile(cfgFile))
#         if os.path.isfile(cfgFile):
#             cfg.read(cfgFile)
#         else:
        print(cfgcontent)
        cfg.readfp(StringIO(cfgcontent))
        print(cfg.sections())
        
        print(cfg.options('save_dir'))
        
        print(self.setup_cfg.sections())
        server_ip=self.setup_cfg.get('SETUP','HSRM_IP')
        print(server_ip)
#         print lineset
        
        for opt in self.setup_cfg.options('SETUP'):
            print(opt,self.setup_cfg.get('SETUP',opt))
        
        for opt in cfg.options('save_dir'):
            print(opt,cfg.get('save_dir',opt))
        
        cfg.set('ftp','server',server_ip)
        cfg.set('socket','server',server_ip)
        cfg.set('socket','port',self.setup_cfg.get('SETUP','recv_port'))
        cfg.set('srm','srm_ip',server_ip)
        cfg.set('srm','srm_port',self.setup_cfg.get('SETUP','hsrm_port'))
        cfg.set('COMMON','agent_ip',agent_ip)
        cfg.set('COMMON','agent_port',self.setup_cfg.get('SETUP','agent_port'))
        cfg.set('COMMON','home_dir',self.s_current_path)
        cfg.set('save_dir','EMC.CLONE','/data/EMC.CLONE/')
        cfg.set('save_dir','dbinfo.MAN','/data/dbms_spool//')
        cfg.set('save_dir','dbinfo.SCH','/data/dbms_spool/')
        cfg.set('save_dir','diskinfo.MAN','/data/serverinfo/')
        cfg.set('save_dir','diskinfo.SCH','/data/serverinfo/')
        print(cfg.options('save_dir'))
        with open(cfgFile, 'w') as configfile:
            cfg.write(configfile)
    
        with open(cfgFile) as f:
            lineset=f.read()
        
#         print lineset
    
    def win_cfg(self):
        cfgFile=os.path.join('config','vendor','windows.WMI.cfg')
        with open(cfgFile) as f:
            cfgline=f.read()
        print('windows.WMI.cfg')
        print('-'*50)
        for line in cfgline.splitlines():
            if '=' in line:
                cmd= line.split('=')[0]
        cfg = configparser.RawConfigParser()
        cfg.read(cfgFile)
        for sec in cfg.sections():
            print('[%s]'%sec)
            for opt in cfg.options(sec):
                cmdvalue = cfg.get(sec,opt)
                print(opt,'=',self.s_aes_cipher.decrypt(cmdvalue))
    

    
    def set_task(self):            
        task_time=self.setup_cfg.get('SETUP','DAEMON')
        
        s_task_check = "SCHTASKS /query | findstr AGENT_CHECK"
        task=os.popen(s_task_check).read()
        print(task)
        
        cmd='SCHTASKS /DELETE /F /TN AGENT_CHECK'
        os.popen(cmd).read()
        
        s_task_check = "SCHTASKS /query | findstr AGENT_CHECK"
        task=os.popen(s_task_check).read()
        
        if task.find('AGENT_CHECK') != 0:
            
            if task_time.lower() != 'none':
                s_task = "SCHTASKS /Create /SC DAILY /TN AGENT_CHECK /TR %s\\fletaDaemonCheck.bat /ST %s /NP /RL HIGHEST /F" % (self.s_current_path, task_time)
                os.popen(s_task).read()
                s_task_check = "SCHTASKS /query | findstr AGENT_CHECK"
                task=os.popen(s_task_check).read()
                print(task)
                
    def subprocess_open(self,command):
        popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (stdoutdata, stderrdata) = popen.communicate()
        return stdoutdata, stderrdata

    def process_kill(self,process):
        cmd='tasklist | findstr %s'%process 
        print(cmd)
        out,err=self.subprocess_open(cmd)
        
        if out.find('fleta_daemon') >= 0:
            print('process kill %s'%process)
            cmd='taskkill /F /IM %s'%process
            out,err=self.subprocess_open(cmd)
        
    

    def main(self):
        
        # config/fleta.cfg setting (AGent IP / Server Ip ..etc)
        agent_ip=self.get_agent_ip()
        print('AGENT IP :',agent_ip,self.is_valid_ipv4(agent_ip))
        #fleta.cfg set
        self.set_config(agent_ip)
        #cfg view
        self.win_cfg()
#       #task add 
        #SCHTASKS /query | findstr AGENT_CHECK
        self.set_task()
        
        #diskinfo start  
        dir = 'SCH'
        version_check.VersionCheck().main()
        o_fleta = fleta_diskinfo.Fleta()
        o_fleta.main(dir)
    #  process start
        self.process_kill('fleta_daemon.exe')
        self.process_kill('fleta_schedule.exe')
        os.system('fletaDaemonCheck.bat')
        print('#'*50)
        print('#'*50)
        print('# END CONFIG')
        print('#'*50)
        print('#'*50)

if __name__=='__main__':
    ConfigSset().main()
