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
    def send(self, message, codification="ascii"):
        message = message.encode("ascii")

        total_sent = 0
        while message:
            total_sent = self.socket.send(message)
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

        with open(path, 'r') as file:
            file.seek(offset)
            buf = file.read(size)
        # Codificamos a base64 y enviamos
        buf64_bytes = b64encode(buf.encode('ascii'))
        buf64 = buf64_bytes.decode('ascii')

        buf = create_error_msg(CODE_OK) + buf64 + EOL
        self.send(buf)

    def quit(self):
        self.send(create_error_msg(CODE_OK))
        self.socket.close()

    def handle(self):
        """
        Atiende eventos de la conexión hasta que termina.
        """
        while True:
            # el mensaje deberia ser un comando
            data = self.socket.recv(4096).decode('ascii')
            while not EOL in data:
                data += self.socket.recv(4096).decode('ascii')
            if len(data) == 0:
                self.send(create_error_msg(BAD_REQUEST))
                break

            if '/n' in data:
                self.send(create_error_msg(BAD_EOL))
                break

            argv = data.split()

            try:
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
                        break

                    case (
                            ['get_file_listing', *_] | ['get_metadata', *_] |
                            ['get_file_slice', *_] | ['quit', *_] ):
                        self.send(create_error_msg(INVALID_ARGUMENTS))

                    case _:
                        self.send(create_error_msg(INVALID_COMMAND))
            except Exception:
                #self.send(create_error_msg(INTERNAL_ERROR))
                print(f"Unexpected {Exception=}, {type(Exception)=}")
                self.socket.close()
                break
