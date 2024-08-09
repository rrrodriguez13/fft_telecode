import numpy as np
import time
from functions import send

# Configuration
IP_ADDRESSES = ["10.10.10.40", "10.10.10.50"]
PORTS = [6371, 6372]  # Ensure each IP uses a unique port

# Generate some random data
data = np.random.randint(0, 255, size=(2048, 2), dtype=np.uint8)

def main():
    try:
        for ip, port in zip(IP_ADDRESSES, PORTS):
            UDP = send(ip, port)
            UDP.eth0()
            UDP.send_data(data)
            UDP.stop()

    except KeyboardInterrupt:
        print("Sending interrupted.")
    finally:
        print("Sending done.")

if __name__ == '__main__':
    main()
