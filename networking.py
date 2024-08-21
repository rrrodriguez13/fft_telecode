import numpy as np
import socket

# Networking classes
class UdpSend:
    def __init__(self, HOST, PORT, verbose=False):
        self.HOST = HOST
        self.PORT = PORT
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.verbose = verbose
    
    def stop(self):
        self.s.close()
    
    def eth0(self):
        self.s.connect((self.HOST, self.PORT))
        if self.verbose:
            print('eth0 starting...')
            print(f'Yelling on port {self.HOST}')
        
    def send_data(self, data):
        assert data.ndim == 2
        for i in range(data.shape[0]):
            self.send_bytes(data[i].tobytes())
            if self.verbose:
                print(f'Sent chunk {i+1}/{data.shape[0]} of size {data.shape[1]}')

    def send_bytes(self, chunk):
        self.s.sendto(chunk, (self.HOST, self.PORT))

class UdpReceive:
    def __init__(self, HOST, PORT):
        self.HOST = HOST
        self.PORT = PORT
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.settimeout(5)
        
    def eth0(self):
        # Bind to all interfaces
        self.s.bind(('', self.PORT))
        print(f'Listening on port {self.PORT} ...')
    
    def set_up(self):
        try:
            print('Searching for data ...')
            data, addr = self.s.recvfrom(2*num_samples)
            print('Received data!\n')
            return data
        except socket.timeout:
            print('No data received, waiting for next packet ...')
            print("\n")
        
    def stop(self):
        self.s.close()
