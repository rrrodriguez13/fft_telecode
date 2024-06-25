import numpy as np
import socket
import sys
import threading
import time

MAX_UDP_PACKET_SIZE = 65507  # Maximum safe UDP packet size

class send:
    def __init__(self, HOST, PORT, HOST1, PORT1, size):
        self.HOST = HOST
        self.PORT = PORT
        self.HOST1 = HOST1
        self.PORT1 = PORT1
        self.size = int(size)
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
        self.send_data(self.s, self.HOST, self.PORT)
        print('eth0 sent data...')
    
    def udp1(self):
        self.send_data(self.s1, self.HOST1, self.PORT1)
        print('eth1 sent data...')
    
    def send_data(self, sock, host, port):
        data = bytearray(self.size)
        chunks = [data[i:i+MAX_UDP_PACKET_SIZE] for i in range(0, len(data), MAX_UDP_PACKET_SIZE)]
        for chunk in chunks:
            sock.sendto(chunk, (host, port))

class receive:
    def __init__(self, HOST, PORT):
        self.HOST = HOST
        self.PORT = PORT
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def eth0(self):
        self.s.bind((self.HOST, self.PORT))
        print('Set up connection...')
    
    def set_up(self):
        data, addr = self.s.recvfrom(MAX_UDP_PACKET_SIZE)
        print('received data:', data)
    
    def stop(self):
        self.s.close()
