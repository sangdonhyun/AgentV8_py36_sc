#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Created on 2016.08.16
    @author: jhbae
'''
from lib import common
import ftplib
from lib import decode
import os
import fnmatch
import socket
import sys
import shutil
from lib.log_control import LogControl

class FileTransfer():
    def __init__(self):
        self.o_common = common.Common()
        self.o_decode = decode.Decode()
        self.log_control = LogControl()

        self.s_agent_path = self.o_common.s_agent_path
        self.s_transfer_type = self.o_common.cfg_parse_read('fleta.cfg', 'COMMON', 'transfer')
        self.s_file_extensions = [ '*.tmp' , '*.log']

        # Socket Connection Info
        self.a_socket_tuple = self.o_common.cfg_parse_read('fleta.cfg', 'socket')
        # self.a_socket_info = self.o_common.tuple_to_dict(self.a_socket_tuple)
        self.a_socket_info = self.a_socket_tuple

        # Ftp Connection Info
        self.a_ftp_tuple = self.o_common.cfg_parse_read('fleta.cfg', 'ftp')
        self.a_ftp_info = self.a_ftp_tuple

        s_transfer_encode = self.o_common.cfg_parse_read('fleta_config.cfg', 'diskinfo', 'transfer_encode')
        self.s_aes_cipher = self.o_common.s_aes_cipher
        print('s_tranfer_encode :',s_transfer_encode)
        print(type(s_transfer_encode))
        try:
            if s_transfer_encode.upper() == 'T':
                self.b_transfer_encode = True
            else:
                self.b_transfer_encode = False
        except Exception as e:
            self.b_transfer_encode = False


    def socket_transfer(self, s_file_type, b_remove=False):
        s_socket_host = self.a_socket_info['server']
        s_socket_port = int(self.a_socket_info['port'])
        if s_socket_port == '':
            s_socket_port = int(54002)

        s_save_tmp = self.o_common.cfg_parse_read('fleta.cfg', 'save_dir', s_file_type)

        s_save_dir = self.s_agent_path + s_save_tmp

        b_bit = False
        for s_root, s_dirs, s_filenames in os.walk(s_save_dir):
            for s_extension in self.s_file_extensions:
                for s_file in fnmatch.filter(s_filenames, s_extension):
                    s_file_name = os.path.join(s_root, s_file)

                    a_info = {}
                    a_info['FLETA_PASS'] = 'kes2719!'
                    a_info['FILENAME'] = os.path.basename(s_file_name)
                    a_info['DIR'] = s_file_type
                    a_info['FILESIZE'] = os.path.getsize(s_file_name)

                    o_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    o_sock.settimeout(10)
                    b_bit = False

                    s_info_data = self.o_decode.fenc(str(a_info))

                    # ## 업로드파일 인코딩 부분 설정
                    if self.b_transfer_encode:
                        # src , dst
                        s_tmp_res_file = os.path.join(self.o_common.s_tmp_path, s_file)
                        shutil.move(s_file_name, s_tmp_res_file)

                        if os.path.isfile(s_tmp_res_file):
                            s_res_data = self.o_common.file_read(s_tmp_res_file, s_agent_path=False)
                            s_enc_data = self.s_aes_cipher.encrypt(s_res_data)
                            self.o_common.file_write(s_file_name, s_enc_data, s_agent_path=False)

                    try:
                        # Connect to server and send data
                        o_sock.connect((s_socket_host, s_socket_port))
                        final_data = s_info_data
                        if not isinstance(final_data,bytes):
                            final_data = bytes(final_data,'utf-8')
                        o_sock.sendall(final_data)

                        # Receive data from the server and shut down
                        s_received = o_sock.recv(1024)
                        # print(s_received)
                        # print('type:',type(s_received))
                        if isinstance(s_received,bytes):
                            s_received = s_received.decode('utf-8')
                        if s_received == 'READY':
                            s_receive_info = str(s_file_name) + ' / ' + str(a_info['FILESIZE'])
                            self.log_control.logdata('AGENT', 'ACCESS', '40003', str(s_receive_info))
                            with open(s_file_name) as f:
                                s_data_contents = f.read()
                            if not isinstance(s_data_contents,bytes):
                                # s_data_contents = bytes(s_data_contents,'utf-8')
                                s_data_contents = s_data_contents.encode(errors='ignore ')
                            # print('-'*50)
                            # print(os.path.isfile(s_file_name))
                            # print(s_data_contents)
                            # print(s_receive_info)
                            # print('-' * 50)
                            o_sock.sendall(s_data_contents)
                        b_bit = True
                        o_sock.close()
                        if b_remove is True:
                            os.remove(s_file_name)
                    except socket.error as e:
                        b_bit = False
                        self.log_control.logdata('AGENT', 'ERROR', '40001')
                        print(str(e))

        return b_bit

    def ftp_transfer(self, s_file_type, b_remove=False):
        b_bit = True
        s_ftp_host = self.a_ftp_info['server']
        s_ftp_user = self.a_ftp_info['user']
        s_ftp_pass = self.s_aes_cipher.decrypt(self.a_ftp_info['pass'])
        s_ftp_port = self.a_ftp_info['port']
        s_ftp_timeout = self.a_ftp_info['timeout']

        s_save_tmp = self.o_common.cfg_parse_read('fleta.cfg', 'save_dir', s_file_type)
        s_save_dir = self.s_agent_path + s_save_tmp

        if s_ftp_port == '':
            s_ftp_port = 21

        try :
            o_ftp = ftplib.FTP()
            o_ftp.connect(s_ftp_host, s_ftp_port, float(s_ftp_timeout))
            o_ftp.login(s_ftp_user, s_ftp_pass)

            for s_root, s_dirs, s_filenames in os.walk(s_save_dir):
                o_ftp.cwd(s_file_type)

                for s_extension in self.s_file_extensions:
                    for s_file in fnmatch.filter(s_filenames, s_extension):
                        s_file_name = os.path.join(s_root, s_file)

                        # ## 업로드파일 인코딩 부분 설정
                        if self.b_transfer_encode:
                            s_tmp_res_file = os.path.join(self.o_common.s_tmp_path, s_file)
                            shutil.move(s_file_name, s_tmp_res_file)

                            if os.path.isfile(s_tmp_res_file):
                                s_res_data = self.o_common.file_read(s_tmp_res_file, s_agent_path=False)
                                s_enc_data = self.s_aes_cipher.encrypt(s_res_data)
                                self.o_common.file_write(s_file_name, s_enc_data, s_agent_path=False)

                        s_receive_info = str(s_file_name) + ' / ' + str(os.path.getsize(s_file_name))
                        self.log_control.logdata('AGENT', 'ACCESS', '40004', str(s_receive_info))

                        o_f = open(s_file_name, 'rb')
                        o_ftp.storbinary('STOR %s' % (s_file), o_f)
                        o_f.close()

                        if b_remove is True:
                            os.remove(s_file_name)
            o_ftp.quit()
        except Exception as e:
            b_bit = False
            self.log_control.logdata('AGENT', 'ERROR', '40002')

        return b_bit

    def main(self, a_file_info, b_remove=False):
        b_bit = False
        s_allow_transfer = self.o_common.cfg_parse_read('fleta_config.cfg', 'diskinfo', 'allow_transfer')

        if s_allow_transfer == 'T':
            if len(a_file_info) > 0 and isinstance(a_file_info, dict):
                for s_file_type, b_transfer in a_file_info.items() :
                    if b_transfer:
                        if self.s_transfer_type.lower() == 'ftp':
                            b_bit = self.ftp_transfer(s_file_type)
                        else:
                            b_bit = self.socket_transfer(s_file_type, b_remove)
        else :
            b_bit = True
            print ("File Tansfer Check Type is 'F'")
            self.log_control.logdata('AGENT', 'ACCESS', '40005')
        return b_bit
