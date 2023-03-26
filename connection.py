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
        with self.socket as s:
            while True:
                if len(message) <= 0:
                    break
                s.send(message)
            

    def get_file_listing(self):
        buf = error_messages[CODE_OK] + EOL
        for dir in os.listdir(self.directory):
            buf += dir + " " + EOL
        buf + EOL
        #self.send(buf)
        
    def handle(self):
        """
        Atiende eventos de la conexión hasta que termina.
        """ 
        pass
