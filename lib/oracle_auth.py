#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2017.11.14
    @author: jhbae
'''
import os
import sys
from . import common
import traceback
from .db_info_oracle_getuser import DbInfoOracleExecute
import configparser
from pickle import FALSE
from .log_control import LogControl

class OracleAuth():
    def __init__(self):
        self.o_common = common.Common()
        self.s_aes_cipher = self.o_common.s_aes_cipher
        self.bAgentInner = True        
        self.log_control = LogControl()

        a_get_oracle_auth_cfg = self.get_oracle_auth_cfg()

        self.s_sysdba_check = a_get_oracle_auth_cfg['sysdba']
        # self.s_multi_check = a_get_oracle_auth_cfg['multiuser']
        self.s_switch_user = a_get_oracle_auth_cfg['switchuser']
        self.s_custom_path = a_get_oracle_auth_cfg['custompath']
        
        self.s_Oraport = ''
        self.s_OraHost = ''
        self.s_OtaTNS = ''
        try:
            if 'port' in list(a_get_oracle_auth_cfg.keys()):
                self.s_Oraport = a_get_oracle_auth_cfg['port'].strip()
            if 'hostname' in list(a_get_oracle_auth_cfg.keys()):
                self.s_OraHost = a_get_oracle_auth_cfg['hostname'].strip()
            if 'tns' in list(a_get_oracle_auth_cfg.keys()):
                self.s_OraTNS = a_get_oracle_auth_cfg['tns'].strip()
        except:
            pass
            
        #### editing #### ################
        self.s_unable_root = 'N'
        try:
            listAuthCFG = list(a_get_oracle_auth_cfg.keys())
            if 'unable_root' in listAuthCFG:
                self.s_unable_root = a_get_oracle_auth_cfg['unable_root']
            self.sMultiUser = ''
            self.s_oratab = ''
            if 'multi-user' in listAuthCFG:
                self.sMultiUser = a_get_oracle_auth_cfg['multi-user']
            if 'oratab' in listAuthCFG:
                self.s_oratab = a_get_oracle_auth_cfg['oratab']
            print('switch : ', self.s_switch_user, 'sysdba : ', self.s_sysdba_check, 'multi : ', self.sMultiUser)
        
        except:
            sErrorMsg = traceback.format_exc().strip()
            self.log_control.logdata('AGENT', 'ERROR', '30011', sErrorMsg)
            
        #if self.s_unable_root is 'y':
        #    self.get_multi_oracle_config()
        #### ####### #### ################
        self.b_oraclequery = self.o_common.cfg_parse_read('fleta_config.cfg', 'oraclequery', 'usage')
        
    def get_oracle_auth_cfg(self):
        try:
            a_auth_info_tuple = self.o_common.cfg_parse_read('dbms.cfg', 'ORACLE_AUTH')
            a_auth_info = self.o_common.tuple_to_dict(a_auth_info_tuple)
            asKeys = list(a_auth_info.keys())
            if not 'sysdba' in asKeys:
                sErrorMsg = 'oracle_auth.py [get_oracle_auth_cfg] : No Configuration(sysdba) for Oracle SQL. Check config/dbms.cfg'
                self.log_control.logdata('AGENT', 'ERROR', '30011', sErrorMsg)
                
            if not 'switchuser' in asKeys:
                sErrorMsg = 'oracle_auth.py [get_oracle_auth_cfg] : No Configuration(switchuser) for Oracle SQL. Check config/dbms.cfg'
                self.log_control.logdata('AGENT', 'ERROR', '30011', sErrorMsg)
                
            if not 'custompath' in asKeys:
                sErrorMsg = 'oracle_auth.py [get_oracle_auth_cfg] : No Configuration(custompath) for Oracle SQL. Check config/dbms.cfg'
                self.log_control.logdata('AGENT', 'ERROR', '30011', sErrorMsg)
                
            return a_auth_info
        except:
            print('Get Oracle Auth CFG Error')

    def oracle_command(self, s_switch_user, s_sid, s_command=None):
        
        if self.b_oraclequery  is 'F':
            s_silent = '-S'
        else:
            s_silent = ''
            
        s_oracle_command = ''
        s_pre_command = ''
        s_ora_home = ''
        b_adjust_unable_root = False
        
        # try:
        if 'y' in self.s_unable_root.lower(): # root be unable to query
            s_ora_home_, s_pre_command_ = self.get_multi_oracle_config(s_switch_user, s_sid)
            s_ora_home += s_ora_home_
            s_pre_command += s_pre_command_
            print ("pre_command : %s" %s_pre_command)
            #print "Unable Root Query\n"
        # except Exception as e:
        #     sErrorMsg = traceback.format_exc().strip()
        #     self.log_control.logdata('AGENT', 'ERROR', '30011', sErrorMsg)
            
        a_rtn_auth = {}
        s_export_sid = ""
        try:
            a_rtn_auth = self.oracle_auth(s_switch_user, s_sid, s_ora_home, s_pre_command)
            s_export_sid = "export ORACLE_SID=%s;" % (s_sid)
        except Exception as e:
            sErrorMsg = traceback.format_exc().strip()
            self.log_control.logdata('AGENT', 'ERROR', '30011', sErrorMsg)
            
        print('AUTH check : ', a_rtn_auth)
        if a_rtn_auth:
            print("array returned authorizations")
            s_auth_val = ''
            if a_rtn_auth['user'] != '': 
                s_auth_val = "%s sqlplus %s %s " % (s_export_sid, s_silent, a_rtn_auth['user'])
#                if s_pre_command == '':
#                    s_auth_val = "%s sqlplus %s %s " % (s_export_sid, s_silent, a_rtn_auth['user'])
#                else:
#                    s_auth_val = "%s %s \"sqlplus %s %s " % (s_export_sid, s_pre_command, s_silent, a_rtn_auth['user'])                  
            else:
                if s_pre_command != '':
                    if a_rtn_auth['sysdba'] != '':
                        s_auth_val = "%s \"%ssqlplus %s %s " % (s_pre_command, s_export_sid, s_silent, a_rtn_auth['sysdba'])
                    else:
                        s_auth_val = "%s \"%ssqlplus %s" % (s_pre_command, s_export_sid, s_silent)
                        
                    b_adjust_unable_root = True
                else:
                    if a_rtn_auth['sysdba'] != '':
                        s_auth_val = "%s sqlplus %s %s " % (s_export_sid, s_silent, a_rtn_auth['sysdba'])
                    else:
                        s_auth_val = "%s sqlplus %s" % (s_export_sid, s_silent)
                        
            s_command_tmp = ''
            if s_command.endswith('.sql'):
                s_command_tmp = s_auth_val + " < %s" % (s_command)
                if b_adjust_unable_root is True:
                    s_command_tmp += '\"'
            else:
                s_command_tmp = s_command
                if b_adjust_unable_root is True:
                    s_command_tmp += '\"'
                    
            print('command sql : ', s_command_tmp)
            s_commands = ''
            if a_rtn_auth['multi'] is True or s_command_tmp != '':
                s_commands = s_command_tmp
            elif a_rtn_auth['su'] != '' :
                s_command_tmp = a_rtn_auth['custompath'] + s_command_tmp
                s_commands = a_rtn_auth['su'].replace("[command]", s_command_tmp)
            else:
                s_commands = ''
                
            print('AUTH::', s_commands)
            s_oracle_command = s_commands.strip()
            s_oracle_command += '\n'
            
        print('Oracle Command Check:', s_oracle_command)
        
        if 'y' in self.s_unable_root.lower() and 'n' in self.sMultiUser.lower():
            return False, s_oracle_command, b_adjust_unable_root
        return a_rtn_auth['multi'], s_oracle_command, b_adjust_unable_root
        
    def oracle_auth(self, s_switch_user, s_sid, s_ora_home, s_pre_command):
        a_sql_cmd = {
                    'su' : ''
                    , 'sysdba' : ''
                    , 'user' : ''
                    , 'multi' : False
                    , 'custompath' : ''
                }
                
        if self.s_switch_user == '' :  # switch user 'y' and root be able to query
            ### editing - by YiC ###
            if self.s_unable_root.lower().strip() == 'y' : 
                a_sql_cmd['su'] = '%s "[command]"' % (s_pre_command)
            else:     
                a_sql_cmd['su'] = 'su - %s -c "[command]"' % (s_switch_user)
            ### 20210219 - Editing
            if not 'n' in s_switch_user.lower() and len(s_switch_user) > 2:
                a_sql_cmd['su'] = 'su - %s -c "[command]"' % (s_switch_user)
            ########## editing - by YiC ##########
            
            if self.s_custom_path.lower() == 'y':
                a_sql_cmd['custompath'] = self.custom_oracle_path(s_sid)

        else :  # switch user 'n' and root be able to query
            s_oracle_export_path = DbInfoOracleExecute().get_oracle_path(s_switch_user)
            print("Oracle export path : %s" %s_oracle_export_path)
            ### editing for failure to get oracle export path ###
            if s_oracle_export_path !='':
                if 'y' in self.s_unable_root.lower(): # root be unable to execute query
                    a_sql_cmd['multi'] = True
                #if os.path.isfile(os.path.join(s_oracle_export_path, 'bin', 'sqlplus')):
                #    a_sql_cmd['multi'] = self.export_oracle_path(s_oracle_export_path, s_switch_user, s_sid)
            else:
                ### "Need to check oracle export path" 
                ### print "Fail to get \'oracle export path\' "
                s_oracle_home = ''
                if self.s_custom_path == 'n' and not s_ora_home == '': 
                    s_oracle_home += s_ora_home
                else :
                    s_oracle_home += self.o_common.cfg_parse_read('custom_path.cfg', 'export_path', 'ORACLE_HOME')
                    
                os.environ['ORACLE_HOME'] = s_oracle_home
                if os.path.isfile(os.path.join(s_oracle_home, 'bin', 'sqlplus')):
                    a_sql_cmd['multi'] = self.export_oracle_path(s_oracle_home, s_switch_user, s_sid)
        
        if 'y' in self.s_sysdba_check.lower() and len(self.s_sysdba_check) < 4:
            a_sql_cmd['sysdba'] = "'/ as sysdba\'"
        else:
            a_sql_cmd['user'] = self.oracle_user_auth(s_sid)
        
        print('SQL CMD : ', a_sql_cmd, '==>', self.s_sysdba_check)
        if self.sMultiUser.lower().strip() == 'y' :
            s_oracle_export_path = DbInfoOracleExecute().get_oracle_path(s_switch_user)
            if os.path.isdir(s_oracle_export_path):
                a_sql_cmd['multi'] = self.export_oracle_path(s_oracle_export_path, s_switch_user, s_sid)
                
        return a_sql_cmd
        
    def export_oracle_path(self, s_oracle_export_path, s_switch_user, s_sid):
        
        if self.s_custom_path.lower() == 'n':
            try:
                i_uid = self.o_common.posix_get_uid(s_switch_user)
                os.environ['ORACLE_HOME'] = s_oracle_export_path
                if s_sid != '+ASM':
                    os.environ['ORACLE_SID'] = s_sid
                    
                a_path_tmp = os.environ['PATH'].split(":")
                #print 'ORACLE EXPORT PATH : ', s_oracle_export_path
                if os.environ.get('ORACLE_HOME') + '/bin' not in a_path_tmp:
                    os.environ['PATH'] = ':'.join([os.environ['ORACLE_HOME'] + '/bin', os.environ['PATH']])
            except:
                i_uid = None
                print('Oracle Uid Check Error')
                return False
                
        return True
        
    def custom_oracle_path(self, s_sid):
        s_sid_export = 'ORACLE_SID=%s; export ORACLE_SID;' % s_sid
        a_export_path_dic = self.o_common.cfg_parse_read('custom_path.cfg', 'export_path')
        s_export_path = ''
        
        if len(a_export_path_dic) > 0:
            a_export_path = self.o_common.tuple_to_dict(a_export_path_dic)
            a_export_path_key = sorted(a_export_path.keys())
            
            for s_key in a_export_path_key:
                s_export_memory = 'export %s;' % (s_key)
                a_export_path[s_key] = a_export_path[s_key].replace('$', '\\$')
                s_export_path += '%s=%s;' % (s_key, a_export_path[s_key]) + s_export_memory
                
        s_export = s_sid_export + s_export_path
        
        return s_export
        
    def oracle_user_auth(self, s_sid):
        s_sql_cmd = ''
        a_auth_info = {}
        if os.path.isfile(self.o_common.s_agent_path + '/config/oracle.cfg'):
            a_auth_info = self.o_common.tuple_to_dict(self.o_common.cfg_parse_read('oracle.cfg', s_sid))
            
        a_auth_ora = {}
        if os.path.isfile(self.o_common.s_agent_path + '/config/orauser.cfg'):
            a_auth_ora = self.o_common.tuple_to_dict(self.o_common.cfg_parse_read('orauser.cfg', 'Oracle Author'))
            
        asAuthKey = list(a_auth_info.keys())
        if len(asAuthKey) > 0:
            if not 'hostname' in asAuthKey:
                a_auth_info['hostname'] = ''
            if not 'port' in asAuthKey:
                a_auth_info['port'] = ''
            if not 'tnsname' in asAuthKey:
                a_auth_info['tnsname'] = ''
        asAuthKey = list(a_auth_info.keys())
        
        #print 'user auth', a_auth_info
        asAuthOraKey = list(a_auth_ora.keys())
        bConfigOracleMulti = False
        if len(asAuthKey) > 0 or len(asAuthOraKey) > 0:
            sHost = ''
            sPort = ''
            sTNS = ''
            
            ##### Network Domain Component => "hostname":"port"/"SID" #####
            ##### hostname = Predefined DB host #####
            if  len(asAuthKey) > 0 and 'hostname' in asAuthKey:
                sHost = a_auth_info['hostname'].strip()
                bConfigOracleMulti = True
            else:
                sHost = self.s_OraHost
                
            if  len(asAuthKey) > 0 and 'port' in asAuthKey:
                sPort = a_auth_info['port'].strip()
            else:
                sPort = self.s_Oraport
                
            ##### TNS Network Full Domain #####
            ##### tnsname = defined TNS domain #####
            if  len(asAuthKey) > 0 and 'tnsname' in asAuthKey:
                sTNS = a_auth_info['tnsname'].strip()
            else:
                sTNS = self.s_OraTNS
                
            ##### Getting ID/Password from Oracle configuration(orauser.cfg) #####
            s_user = ''
            s_password = ''
            
            if len(asAuthOraKey) > 0:
                if 'user' in asAuthOraKey and 'passwd' in asAuthOraKey:
                    try:
                        s_user = self.o_common.s_aes_cipher.decrypt(a_auth_ora['user'].strip())
                    except:
                        s_user = a_auth_ora['user'].strip()
                        
                    try:
                        s_password = self.o_common.s_aes_cipher.decrypt(a_auth_ora['passwd'].strip())
                    except:
                        s_password = a_auth_ora['passwd'].strip()
            else:
                if 'user' in asAuthKey and 'passwd' in asAuthKey:
                    s_user = a_auth_info['user'].strip()
                    s_password = a_auth_info['passwd'].strip()
                    
            if s_user == '':
                sErrorMsg = 'oracle_auth.py [oracle_user_auth] : No Configuration(user) for Oracle SQL. Check config/orauser.cfg or config/oracle.cfg'
                self.log_control.logdata('AGENT', 'ERROR', '30011', sErrorMsg)
                return ''
                
            if s_password == '':
                sErrorMsg = 'oracle_auth.py [oracle_user_auth] : No Configuration(password) for Oracle SQL. Check config/orauser.cfg or config/oracle.cfg'
                self.log_control.logdata('AGENT', 'ERROR', '30011', sErrorMsg)
                return ''
                
            s_hostname = sHost
            s_port = sPort
            s_tnsname = sTNS
            s_tns_tnsname = ''
            s_tns_host = ''
            s_tns_port = ''
            s_network = ''
            
            if s_hostname != '':
                s_tns_host = s_hostname
            if s_port != '':
                s_tns_port = s_port
                if s_hostname == '':
                    s_tns_host = self.o_common.s_host_name
                    
            if s_tnsname != '':
                s_tns_tnsname = s_tnsname
                
            if s_tns_tnsname != '':
                s_network = s_tns_tnsname
            elif s_tns_host != '' and s_tns_port != '':
                s_network = "%s:%s/%s" % (s_tns_host, s_tns_port, s_sid)
                
            listSpecial = ['!','#','$','%','*','&']
            for sSpe in listSpecial:
                if sSpe in s_password:
                    sValidOptTMP = "\ " + sSpe
                    sValidOpt = sValidOptTMP.replace(' ', '')
                    s_password = s_password.replace(sSpe, sValidOpt)
                    
            if s_network != '' and bConfigOracleMulti == True:
                s_sql_cmd = '%s/%s@%s' % (s_user, s_password, s_network)
            else:
                s_sql_cmd = '%s/%s' % (s_user, s_password)
        else:
            return ''
        return s_sql_cmd
        
    ##### editing #####
    def get_multi_oracle_config(self, s_user, s_sid):
        d_MultiOra_info = self.o_common.tuple_to_dict(self.o_common.cfg_parse_read('multi_oracle.cfg', s_sid))
        listSec = self.o_common.cfg_section_read('multi_oracle.cfg')
        # print('d_MultiOra_info :',d_MultiOra_info)
        # print(listSec)
        # iSection = len(listSec)
        # 20220203 sdhyun
        try:
            iSection = int(d_MultiOra_info['quote'])
        except Exception as e:
            print(str(e))
            iSection = -1


        s_ora_home = ''
        s_pre_cmd = ''
        # print('get_multi_oracle_config :')
        # print(d_MultiOra_info)
        # print(s_user, s_sid)
        if isinstance(s_user,bytes):
            s_user = s_user.decode('utf-8')
        # print(s_user, s_sid)
        #print(len(d_MultiOra_info))
        #print(list(d_MultiOra_info.keys()))
        #print(d_MultiOra_info['user'] != s_user)
        print('iSection :',iSection)
        if len(d_MultiOra_info) > 0  and 'user' in list(d_MultiOra_info.keys()):
            if d_MultiOra_info['user'] != s_user:
                print("Not matched user")
                sUser = d_MultiOra_info['user']
            else:
                sUser = s_user
            if iSection > -1:
                s_pre_cmd += 'echo %s | su - %s -c' %(d_MultiOra_info['quote'], sUser)
            else:
                s_pre_cmd += 'su - %s -c' %(sUser)
            s_ora_home += '%s' %(d_MultiOra_info['orahome'])
        else:
            s_pre_cmd += 'echo 1 | su - {} -c'.format(s_user)
            
        return s_ora_home, s_pre_cmd