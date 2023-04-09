# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

import os
from constants import *
from base64 import b64encode

def create_error_msg(msg_code):
    assert valid_status(msg_code)
    buf = f"{msg_code} {error_messages[msg_code]}" + EOL
    return buf

class Connection(object):
    """
    Conexión punto a punto entre el servidor y un cliente.
    Se encarga de satisfacer los pedidos del cliente hasta
    que termina la conexión.
    """

    def __init__(self, socket, directory):
        # FALTA: Inicializar atributos de Connection
        self.socket = socket
        self.directory = directory
        self.connected = True

    def send(self, message):
        total_sent = 0
        while message:
            total_sent = self.socket.send(message.encode("ascii"))
            assert total_sent > 0
            message = message[total_sent:]

    def get_file_listing(self):
        buf = create_error_msg(CODE_OK)
        for dir in os.listdir(self.directory):
            buf += dir + " " + EOL
        buf += EOL

        self.send(buf)

    def get_metadata(self, filename):
        path = self.directory + '/' + filename
        # Check if file exists
        if not os.path.isfile(path):
            self.send(create_error_msg(FILE_NOT_FOUND))
            return
        # Check if filename is valid
        for c in filename:
            if c not in VALID_CHARS:
                self.send(create_error_msg(INVALID_ARGUMENTS))
                return

        buf = create_error_msg(CODE_OK)
        filesize = os.stat(path).st_size
        buf += str(filesize) + EOL
        self.send(buf)

    def get_slice(self, filename, offset, size):
        offset = int(offset)
        size = int(size)

        path = self.directory + "/" + filename
        if not os.path.isfile(path):
            self.send(create_error_msg(FILE_NOT_FOUND))
            return

        filesize = os.stat(path).st_size

        if offset < 0 and size < 0 :
            self.send(create_error_msg(INVALID_ARGUMENTS))
            return

        if offset > filesize:
            self.send(create_error_msg(BAD_OFFSET))
            return

        if offset + size > filesize:
            self.send(create_error_msg(BAD_OFFSET))
            return
        
        size_max = size

        with open(path, "rb") as file:
            file.seek(offset)
            buf = file.read(size)    
            size_max -= size

        buf64_bytes = b64encode(buf)
        buf64 = buf64_bytes.decode('ascii')
        buf = create_error_msg(CODE_OK) + buf64 + EOL

        self.send(buf)
    


    def quit(self):
        self.send(create_error_msg(CODE_OK))
        self.socket.close()

    def aux(self, argv):
        match argv:
            case ['get_file_listing']:
                self.get_file_listing()

            case ['get_metadata', filename]:
                self.get_metadata(filename)

            case ['get_slice', filename, offset, size]:
                if not (offset.isdigit() and size.isdigit()):
                    self.send(create_error_msg(INVALID_ARGUMENTS))
                else:
                    self.get_slice(filename, offset, size)

            case ['quit']:
                self.quit()
                self.connected = False

            case (
                    ['get_file_listing', *_] | ['get_metadata', *_] |
                    ['get_slice', *_] | ['quit', *_] ):
                self.send(create_error_msg(INVALID_ARGUMENTS))

            case _:    
                self.send(create_error_msg(INVALID_COMMAND))

    def handle(self):
        """
        Atiende eventos de la conexión hasta que termina.
        """
        MAX_BYTES = 2**14
        while self.connected:
            # el mensaje deberia ser un comando
            data = self.socket.recv(1024).decode('ascii')
            while not EOL in data:
                data += self.socket.recv(1024).decode('ascii')
                if len(data) > MAX_BYTES:
                    self.send(create_error_msg(BAD_REQUEST))
                    self.connected = False
                    self.socket.close()
                    break
                    
            if not self.connected: 
                break

            data_list = data.split(EOL)

            if data_list[-1] != '':
                self.send(create_error_msg(BAD_EOL))
                self.connected = False
                self.socket.close()
                break
            
            else:
                data_list = data_list[:-1]
            
            for command in data_list:
                if '\n' in command:
                    self.send(create_error_msg(BAD_EOL))
                    self.connected = False
            
            if not self.connected:
                self.socket.close()
                break
            for command in data_list:
                argv = command.split()
                try:
                    self.aux(argv)  
                except Exception as e:
                    print(e)
                    self.send(create_error_msg(INTERNAL_ERROR))
                    self.socket.close()
                    self.connected = False