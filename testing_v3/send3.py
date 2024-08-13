import argparse
import os
import threading
import queue
import ugradio
from functions3 import send

# Arguments for when observing
parser = argparse.ArgumentParser()
parser.add_argument('--prefix', '-p', default='data')
parser.add_argument('--len_obs', '-l', default='60')
parser.add_argument('--folder', '-f', default='output')
args = parser.parse_args()

prefix = args.prefix
len_obs = int(args.len_obs)
folder = args.folder

LAPTOP_IP = "10.10.10.30"
PORT = 6373 # corresponds to IP address (must change for each pi)
num_samples = 2048

if not os.path.exists(folder):
    os.makedirs(folder)

# sets up SDR
sdr = ugradio.sdr.SDR(sample_rate=3.2e6, center_freq=145.2e6, direct=False)

# sets up network connection
UDP = send(LAPTOP_IP, PORT)

data_queue = queue.Queue(maxsize=0)
stop_event = threading.Event()

def data_sender():
    try:
        cnt = 0
        while not stop_event.is_set() or not data_queue.empty():
            d = data_queue.get()
            if d is None:
                break
            UDP.send_data(d)
            cnt += 1
            print(f"Sent Data! cnt={cnt} \n")
    except KeyboardInterrupt:
        UDP.stop()
        print("Data transfer stopped ...")
    finally:
        UDP.stop()
        print("Done.")

sender_thread = threading.Thread(target=data_sender)
sender_thread.start()

try:
    while not stop_event.is_set():
        d = sdr.capture_data(num_samples)
        data_queue.put(d)
except KeyboardInterrupt:
    stop_event.set()
finally:
    data_queue.put(None)  # Signal sender thread to exit
    sender_thread.join()
    print("Main thread done.")
