
# coding=utf-8

###############################################################
#  PyNLPl - FreeLing Library
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Radboud University Nijmegen
#
#       Licensed under GPLv3
#
# Classe modificada por Pedro Thompson, usando como base o arquivo freeling.py do pacote original PyNLPl
###############################################################

import socket
import os

def check_server(msg_to_raise):
    def check(fun):
        def fun_wrapper(*args):
            try:
                fun(*args)
            except:
                raise Exception(msg_to_raise)
        return fun_wrapper
    return check


class FreeLingClient(object):

    @check_server('Server not ready')
    def __init__(self, host, port, encoding='utf-8', timeout=15.0):
        """Initialise the client, set channel to the path and filename where the server's .
        in and .out pipes are (without extension)"""
        self.encoding = encoding
        self.BUFSIZE = 10240
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(timeout)
        self.socket.connect((host, int(port)))
        self.encoding = encoding
        self.socket.sendall('RESET_STATS\0'.encode(encoding))
        r = self.socket.recv(self.BUFSIZE)
        r = r.decode()
        if not r.strip('\0') == 'FL-SERVER-READY':
            raise Exception()

    def process(self, sourcewords_s, debug=False):
        """Process a list of words, passing it to the server and realigning the output with the original words"""

        sourcewords_s += '\n\0'

        self.socket.send(sourcewords_s.encode(self.encoding))
        #if debug: print("Sent:",sourcewords_s.encode(self.encoding),file = sys.stderr)

        done = False
        data = ''
        while not done:
            buffer = self.socket.recv(self.BUFSIZE)
            #if debug: print("Buffer: ["+repr(buffer)+"]",file=sys.stderr)
            if buffer[-1] == 0:
                data += buffer[:-1].decode()
                done = True
                break
            else:
                data += buffer.decode()

            #if debug: print("Received:",data,file=sys.stderr)

        return data

    @staticmethod
    @check_server('Server could not be turned on.')
    def turn_server_ON(config_file, port):
        os.system('analyze -f ' + config_file + ' --outlv tagged --server --port ' + str(port))
