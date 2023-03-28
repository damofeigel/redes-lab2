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
        path = self.directory + '/' + filename
        # Check if file exists
        if not os.path.isfile(path):
            self.send(error_messages[FILE_NOT_FOUND0] + EOL)
        # Check if filename is valid
        for c in filename:
            if (c == " "):
                self.send(error_messages[INVALID_ARGUMENTS]+ EOL)
        
        buf = error_messages[CODE_OK] + EOL
        filesize = os.stat(filename).st_size
        buf += str(filesize) + EOL

        self.send(buf)

    def get_slice(self, filename, offset, size):
        path = self.directory + "/" + filename
        if not os.path.isfile(path):
            self.send(error_messages[FILE_NOT_FOUND] + EOL)
        
        filesize = os.stat(filename).st_size

        if offset and size < 0 :
            self.send(error_messages[INVALID_ARGUMENTS] + EOL)
        if offset > filesize:
            self.send(error_messages[BAD_OFFSET])

        buf = error_messages[CODE_OK] + EOL
        with open(path, 'r') as file:
            file.seek(offset)
            buf = file.read(size)
        # Codificamos a base64 y enviamos
        buf64_bytes = b64encode(buf.b64encode('ascii'))
        buf64 = base64_bytes.decode('ascii')
    
        buf = error_messages[CODE_OK] + EOL + buf64 + EOL 
        self.send(buf)
  
    def quit(self):
        self.send(error_messages[CODE_OK] + EOL)
        self.socket.close()
        
    def handle(self):
        """
        Atiende eventos de la conexión hasta que termina.
        """
        # TODO: check error
        while True:
            # el mensaje deberia ser un comando   
            data = self.socket.recv(4096).decode('ascii') 
            if len(data) == 0:
                self.send(error_messages[BAD_REQUEST] + EOL)
                break
            
            argv = data.split()
            match argv[0]:
                case "get_file_listing":
                    # Dar error si hay otro argumento?
                    self.get_file_listing()
                case "get_metadata":
                    # la misma funcion checkea que el 
                    # segundo argumento sea valido
                    if len(argv) != 2:
                        self.send(error_messages[INVALID_ARGUMENTS] + EOL)
                    self.get_metadata(argv[1])
                case "get_slice":
                    if len(argv) != 4:
                        self.send(error_messages[INVALID_ARGUMENTS] + EOL)
                    self.get_slice(argv[1], argv[2], argv[3])
                case quit:
                    self.quit()
                case _:
                    self.send(error_messages[INVALID_COMMAND] + EOL)