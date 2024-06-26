import numpy as np
import socket
import sys
import threading
import time

MAX_UDP_PACKET_SIZE = 2048  # Maximum safe UDP packet size

# class send:
#     def __init__(self, HOST, PORT):
#         self.HOST = HOST
#         self.PORT = PORT
#         self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
#     def stop(self):
#         self.s.close()
    
#     def eth0(self):
#         self.s.connect((self.HOST, self.PORT))
#         print('eth0 starting...')
        
    
#     def send_data(self, data):
#         chunks = np.reshape(data, (-1, MAX_UDP_PACKET_SIZE))
#         for chunk in chunks:
#             self.s.sendto(chunks, (self.HOST, self.PORT))

class send:
    def __init__(self, HOST, PORT):
        self.HOST = HOST
        self.PORT = PORT
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def stop(self):
        self.s.close()
    
    def eth0(self):
        self.s.connect((self.HOST, self.PORT))
        print('eth0 starting...')
        
    def send_data(self, data):
        # Ensure data is in bytes format
        data = bytearray(data)
        # Split data into chunks
        chunks = [data[i:i + MAX_UDP_PACKET_SIZE] for i in range(0, len(data), MAX_UDP_PACKET_SIZE)]
        for i, chunk in enumerate(chunks):
            self.s.sendto(chunk, (self.HOST, self.PORT))
            print(f'Sent chunk {i+1}/{len(chunks)} of size {len(chunk)}')

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
