import argparse
import os
import time
import ugradio
import functions
from functions import send
import threading
import queue

# Arguments for when observing
parser = argparse.ArgumentParser()
parser.add_argument('--prefix', '-p', default='data')
parser.add_argument('--len_obs', '-l', default='60')
parser.add_argument('--folder', '-f', default='output')
args = parser.parse_args()

prefix = args.prefix
len_obs = int(args.len_obs)
folder = args.folder

LAPTOP_IP = "192.168.0.234"
PORT = 6371
num_samples = 2048

if not os.path.exists(folder):
    os.makedirs(folder)

# sets up SDR
sdr = ugradio.sdr.SDR(sample_rate=3.2e6, center_freq=125.2e6, direct=False)
# sets up network connection
UDP = send(LAPTOP_IP, PORT)

# Create a queue for thread communication
data_queue = queue.Queue()

def producer():
    try:
        while True:
            d = sdr.capture_data(num_samples)
            data_queue.put(d)
            print("Captured Data and put in queue! \n")
    except KeyboardInterrupt:
        print("Data capture stopped ...")
        UDP.stop()
    finally:
        print("Producer done.")

def consumer():
    try:
        while True:
            d = data_queue.get()
            if d is None:
                break
            UDP.send_data(d)
            print("Sent Data from queue! \n")
            data_queue.task_done()
    except KeyboardInterrupt:
        UDP.stop()
    finally:
        print("Consumer done.")

# Start producer and consumer threads
producer_thread = threading.Thread(target=producer)
consumer_thread = threading.Thread(target=consumer)

producer_thread.start()
consumer_thread.start()

producer_thread.join()
data_queue.put(None)  # Signal consumer to exit
consumer_thread.join()

print("All done.")
