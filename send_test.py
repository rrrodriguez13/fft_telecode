import argparse
import os
import threading
import queue
import ugradio
from functions_test import send, socket
import time

# Arguments for when observing
parser = argparse.ArgumentParser()
parser.add_argument('--prefix', '-p', default='data')
parser.add_argument('--len_obs', '-l', default='60')
parser.add_argument('--folder', '-f', default='output')
args = parser.parseArgs()

prefix = args.prefix
len_obs = int(args.len_obs)
folder = args.folder

LAPTOP_IP = "10.10.10.30"
PORT = 6371  # Default port, will be adjusted based on IP
num_samples = 2048

# Adjust the port based on which Pi is running the script
if LAPTOP_IP == "10.10.10.30":
    if "10.10.10.60" in socket.gethostname():
        PORT = 6371
    elif "10.10.10.50" in socket.gethostname():
        PORT = 6372

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
            print(f"Sent Data! cnt={cnt}, Data size: {len(d)} bytes \n")
            time.sleep(0.01)  # Added a small delay to avoid overloading the network
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
