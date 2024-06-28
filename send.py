import time
import numpy as np
from functions import send, MAX_UDP_PACKET_SIZE

LAPTOP_IP = "192.168.0.234"
RPI_IP = "192.168.0.235"
PORT = 6371

def capture_data(size):
    # send a bunch of zeros for now, replace with actual data later
    return [0] * size

def sender_main():
    UDP = send(LAPTOP_IP, PORT)
    #UDP.eth0()
    print('Everything initialized...')
    try:
        print('Starting loop... \n')
        while True:
            # 3 chunks being sent
            data = capture_data(3*MAX_UDP_PACKET_SIZE)
            UDP.send_data(data)
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
