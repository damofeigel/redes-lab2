from constants import *
import os

lol = 'get_file_listing\r\nget_file_listing\r\n'.encode('ascii')
lol = lol.decode('ascii')

lol = lol.split('\r\n')
if lol[-1] != '':
    print("mal ahi")
else:
    lol = lol[:-1]

print(lol)  
for command in lol:
    if '\n' in command:
        print("mal ahi 2")

print(lol)