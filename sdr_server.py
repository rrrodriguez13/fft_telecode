import socket
import numpy as np
import ugradio
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--port', '-p', type=int, default=65432)
args = parser.parse_args()

# Initialize SDR
sdr = ugradio.sdr.SDR(sample_rate=3.2e6, center_freq=125.2e6, direct=False)

def send_data(sock, addr):
    try:
        while True:
            data = sdr.capture_data()
            if data.size > 0:
                sock.sendto(data.tobytes(), addr)
                print(f"Sent {len(data.tobytes())} bytes of data to {addr}")
            else:
                print("No data captured")
    except KeyboardInterrupt:
        print("Stopping server!")
        sdr.close()
    except Exception as e:
        print(f"Error during data capture or sending: {e}")

# Set up socket
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock.bind(('0.0.0.0', args.port))
    print(f'Server listening on port {args.port}')
    while True:
        try:
            message, addr = sock.recvfrom(4096)
            if message == b'requesting data':
                print(f'Received data request from {addr}')
                send_data(sock, addr)
        except socket.error as e:
            print(f"Socket error: {e}")
        except Exception as e:
            print(f"General error: {e}")
