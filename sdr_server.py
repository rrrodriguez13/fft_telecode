import socket
import numpy as np
import ugradio
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--port', '-p', type=int, default=65432)
args = parser.parse_args()

# Initialize SDR
sdr = ugradio.sdr.SDR(sample_rate=3.2e6, center_freq=125.2e6, direct=False)

def send_data(conn):
    try:
        while True:
            data = sdr.capture_data()
            conn.sendall(data.tobytes())
    except KeyboardInterrupt:
        print("Stopping server!")
        sdr.close()
        conn.close()

# Set up socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(('0.0.0.0', args.port))
    s.listen()
    print(f'Server listening on port {args.port}')
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        send_data(conn)
