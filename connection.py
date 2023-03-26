# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

import socket
from constants import *
from base64 import b64encode

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
        pass

    def send(self, message):
        # TODO: Enviar mensaje al servidor, decode? 
        total_sent = 0
        while len(message) > total_sent: 
            sent = self.socket.send(message[total_sent:])
            total_sent += sent

    def get_file_listing(self):
        buf = error_messages[CODE_OK] + EOL
        for dir in os.listdir(self.directory):
            buf += dir + " " + EOL
        buf + EOL

        self.send(buf)
        
    def get_metadata(self, filename):
        # TODO: checkear espacios? errores 
        path = self.directory + '/' + filename
        
        if not os.path.isfile(path):
            self.send(error_messages[FILE_NOT_FOUND])
        
        for c in filename:
            if (c == " "):
                self.send(error_messages[INVALID_ARGUMENTS])

        buf = error_messages[CODE_OK] + EOL
        filesize = os.stat(filename).st_size
        buf += str(filesize) + EOL

        self.send(buf)

    def get_slice(self, filename, offset, size):
        
        path = self.directory + "/" + filename
        if not os.path.isfile(path):
            self.send(error_messages[FILE_NOT_FOUND])
        
        filesize = os.stat(filename).st_size

        if offset and size < 0 :
            self.send(error_messages[INVALID_ARGUMENTS])
        if offset > filesize:
            self.send(error_messages[BAD_OFFSET])

        buf = error_messages[CODE_OK] + EOL
        with open(path, 'r') as file:
            f.seek(offset)
        # Falta encode, y enviar!

    def quit(self):
        self.send(error_messages[CODE_OK])
        self.socket.close()
        
    def handle(self):
        """
        Atiende eventos de la conexión hasta que termina.
        """ 
        pass
