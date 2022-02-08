# -*- coding: utf-8 -*-
'''
    Created on 2016.08.02
    @author: jhbae
'''
import re
import os
import sys
from lib.common import Common
import jpype
import jaydebeapi as jdb


class DbInfoOracleJdbc():
    def __init__(self):
        self.o_common = Common()
        self.start_jvm()
        self.cursor = object

    def get_jdbc_cfg(self, s_section, s_type):
        if os.path.isfile(os.path.join(self.o_common.s_config_path, 'jdbc.cfg')):
            s_cfg_get_value = self.o_common.cfg_parse_read('jdbc.cfg', s_section, s_type)
        else:
            return False
        return s_cfg_get_value

    def get_jre_version(self):
        s_jre_version = ''

        try:
            s_jvm_custom_path = self.get_jdbc_cfg('jvm', 'jvm_path')
            if s_jvm_custom_path.strip() != '':
                s_jvm_path = s_jvm_custom_path
            else:
                s_jvm_path = jpype.getDefaultJVMPath()
            a_tmp_ver = re.findall('(\d{1}\.\d{1})', s_jvm_path)
        except:
            a_tmp_ver = []

        if len(a_tmp_ver[0]) > 0 and a_tmp_ver[0].strip() != '':
            s_jdbc_driver = self.get_jdbc_cfg('jar', a_tmp_ver[0])
        else:
            s_jre_version = self.get_jdbc_cfg('jre', 'jre_version')
            if len(s_jre_version) > 0 and re.match('\d{1}\.\d{1}', s_jre_version):
                s_jdbc_driver = self.get_jdbc_cfg('jar', s_jre_version)

        if sys.platform == 'win32':
            s_jdbc_driver = os.path.normpath(s_jdbc_driver)

        s_jdbc_driver_path = self.o_common.s_agent_path + s_jdbc_driver
        return s_jdbc_driver_path

    def start_jvm(self):
        s_jdbc_driver = self.get_jre_version()

        try:
            s_jvm_custom_path = self.get_jdbc_cfg('jvm', 'jvm_path')
            if s_jvm_custom_path.strip() != '':
                s_jvm_path = s_jvm_custom_path
            else:
                s_jvm_path = jpype.getDefaultJVMPath()
            jpype.startJVM(s_jvm_path, "-Djava.class.path=%s" % (s_jdbc_driver))
        except Exception as e:
            print(str(e))
            s_jdbc_path = self.get_jdbc_cfg('jvm', 'jvm_path')

            if bool != type(s_jdbc_path):
                jpype.startJVM("%s", "-Djava.class.path=%s" % (s_jdbc_path, s_jdbc_driver))
            else:
                return False
        return True

    def jdbc_connection(self, a_conn_info):
        s_instance = a_conn_info['instance'].strip()
        s_hostname = a_conn_info['hostname'].strip()
        s_port = a_conn_info['port'].strip()
        s_user = a_conn_info['user'].strip()
        s_password = a_conn_info['passwd'].strip()

        try:
            conn = jdb.connect('oracle.jdbc.driver.OracleDriver'
                               , 'jdbc:oracle:thin:%s/%s@%s:%d/%s'
                               % (s_user, s_password, s_hostname, int(s_port), s_instance)
                               )
            self.cursor = conn.cursor()

        except Exception as e:
            print(str(e))
            return False
        return True

    def get_query_file(self, s_file):
        if sys.platform == 'win32':
            s_query_file = os.path.normpath(s_file)
        else:
            s_query_file = s_file

        s_enc_query = self.o_common.file_read(s_query_file)
        s_dec_query = self.o_common.s_aes_cipher.decrypt(s_enc_query)
        s_dec_query = s_dec_query.strip()

        o_p = re.compile(r"select[^;]+(?=;)", re.IGNORECASE | re.MULTILINE | re.DOTALL)
        a_regex = o_p.findall(s_dec_query)
        return a_regex

    def get_version(self, s_file):
        a_regex = self.get_query_file(s_file)
        s_str = ''
        for s_query in a_regex:
            self.cursor.execute(s_query)
            a_query_result = self.cursor.fetchall()
            for a_data in a_query_result:
                s_str += ''.join(a_data)
                s_str += '\n'
        return s_str

    def get_query(self, s_file):
        s_str = ''

        a_regex = self.get_query_file(s_file)

        ## table space ## 
        if a_regex != '' and len(a_regex) > 0:
            for s_query in a_regex:
                self.cursor.execute(s_query)

                a_query_result = self.cursor.fetchall()

                for a_data in a_query_result:
                    s_str += ','.join([str(i) for i in a_data])
                    s_str += '\n'
                s_str += '\n\n'
        return s_str

    def connection_info(self, s_instance):

        try:
            a_instance_info_tuple = self.o_common.cfg_parse_read('oracle.cfg', s_instance)
            a_instance_info = self.o_common.tuple_to_dict(a_instance_info_tuple)

            a_conn_info = {
                'instance': s_instance
                , 'hostname': a_instance_info['hostname']
                , 'user': a_instance_info['user']
                , 'port': a_instance_info['port']
                , 'passwd': self.o_common.s_aes_cipher.decrypt(a_instance_info['passwd'])
            }
        except:
            print('instance error')
            return False
        return a_conn_info

    def jdbc(self, s_sid):
        a_conn_info = self.connection_info(s_sid)
        if a_conn_info is False:
            print("Check Oracle Connection Instance Info.")
            sys.exit(1)

        return self.jdbc_connection(a_conn_info)
