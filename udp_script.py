import numpy as np
import socket
import sys
import threading
import time

class send:
    def __init__(self, HOST, PORT, HOST1, PORT1, size):
        self.HOST = HOST
        self.PORT = PORT
        self.HOST1 = HOST1
        self.PORT1 = PORT1
        self.size = bytearray(int(size))
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def stop(self):
        self.s.close()
        self.s1.close()
        self.thrd.join()
    
    def eth0(self):
        self.s.connect((self.HOST, self.PORT))
        print('eth0 starting...')
        
    def eth1(self):
        self.s1.connect((self.HOST1, self.PORT1))
        print('eth1 starting...')
    
    def udp0(self):
        self.thrd = threading.Thread(target=self.udp1)
        self.thrd.start()
        x = self.size
        self.s.sendto(x, (self.HOST, self.PORT))
        print('eth0 sent data...')
    
    def udp1(self):
        x = self.size
        self.s1.sendto(x, (self.HOST1, self.PORT1))
        print('eth1 sent data...')

class receive:
    def __init__(self, HOST, PORT):
        self.HOST = HOST
        self.PORT = PORT
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def eth0(self):
        self.s.bind((self.HOST, self.PORT))
        print('Set up connection...')
    
    def set_up(self):
        data, addr = self.s.recvfrom(int(900e6 + 57))
        print('received data:', data)
    
    def stop(self):
        self.s.close()
