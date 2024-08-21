import numpy as np
import socket

PORT = 6373
NUM_SAMPLES = 2048

# Networking classes
class UdpSend:
    def __init__(self, host, port=PORT, verbose=False):
        self.host = host
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.verbose = verbose
    
    def stop(self):
        self.s.close()
    
    def eth0(self):
        self.s.connect((self.host, self.port))
        if self.verbose:
            print('eth0 starting...')
            print(f'Yelling on port {self.host}')
        
    def send_data(self, data):
        assert data.ndim == 2
        for i in range(data.shape[0]):
            self.send_bytes(data[i].tobytes())
            if self.verbose:
                print(f'Sent chunk {i+1}/{data.shape[0]} of size {data.shape[1]}')

    def send_bytes(self, chunk):
        self.s.sendto(chunk, (self.host, self.port))

class UdpReceive:
    def __init__(self, host, port=PORT):
        self.host = host
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.settimeout(5)
        
    def eth0(self):
        # Bind to all interfaces
        self.s.bind(('', self.port))
        print(f'Listening on port {self.port} ...')
    
    def set_up(self):
        try:
            print('Searching for data ...')
            data, addr = self.s.recvfrom(2*NUM_SAMPLES)
            print('Received data!\n')
            return data
        except socket.timeout:
            print('No data received, waiting for next packet ...')
            print("\n")
        
    def stop(self):
        self.s.close()
