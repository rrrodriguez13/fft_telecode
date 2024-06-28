import time
import numpy as np
from functions import send, MAX_UDP_PACKET_SIZE, perform_power, shift

LAPTOP_IP = "192.168.0.234"
PORT = 6371

num_samples = 2048

def capture_data(size):
    # Simulate data capture, replace with actual data capture logic
    return np.random.randn(size, 2)  # Random data for simulation

def compute_spectrum(data):
    d = data[..., 0] + 1j * data[..., 1]
    pwr = shift(np.mean(perform_power(np.fft.fft(d)), axis=0))
    return pwr

def sender_main():
    UDP = send(LAPTOP_IP, PORT)
    UDP.eth0()
    print('Everything initialized...')
    try:
        print('Starting loop... \n')
        while True:
            raw_data = capture_data(num_samples)
            spectrum = compute_spectrum(raw_data)
            UDP.send_data(spectrum)
            time.sleep(1)
            print("Sent data!")
    except KeyboardInterrupt:
        UDP.stop()
        print('UDP Stopped...')
    finally:
        print('Done.')

if __name__ == "__main__":
    # send script (not receiving)
    sender_main()
