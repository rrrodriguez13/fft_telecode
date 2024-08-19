import argparse
import os
import threading
import queue
import ugradio
import numpy as np
from functions_test import send

# arguments for when observing
parser = argparse.ArgumentParser()
parser.add_argument('--prefix', '-p', default='data')
parser.add_argument('--len_obs', '-l', default='60')
parser.add_argument('--folder', '-f', default='output')
args = parser.parse_args()

prefix = args.prefix
len_obs = int(args.len_obs)
folder = args.folder

LAPTOP_IP = "10.10.10.30"
PORT = 6373
num_samples = 2048

if not os.path.exists(folder):
    os.makedirs(folder)

# sets up SDR
sdr = ugradio.sdr.SDR(sample_rate=2.2e6, center_freq=145.2e6, direct=False, gain=10)

# sets up network connection
UDP = send(LAPTOP_IP, PORT)

data_queue = queue.Queue(maxsize=0)  # infinite size queue to prevent data loss
stop_event = threading.Event()

def data_capture():
    try:
        while not stop_event.is_set():
            list_data = np.arange(num_samples)  # List of integers to attach to data
            data = sdr.capture_data(num_samples)  # Capture data

            # Ensure data has the same number of rows as list_data
            if data.shape[0] != list_data.shape[0]:
                raise ValueError(f"Dimension mismatch: list_data has {list_data.shape[0]} rows, but data has {data.shape[0]} rows")

            array = np.column_stack((list_data, data))  # Stack arrays horizontally
            print(f"Captured data: {array.shape}")  # Prints shape of data captured
            data_queue.put(array)
    except KeyboardInterrupt:
        stop_event.set()
    except Exception as e:
        print(f"Error in data_capture: {e}")
    finally:
        data_queue.put(None)  # Signal sender threads to exit
        print("Data capture done.")


def data_sender():
    cnt = 0
    try:
        while not stop_event.is_set() or not data_queue.empty():
            data_array = data_queue.get()
            if data_array is None:
                break
            print(f"Sending data: {data_array.shape}")  # prints shape of data being sent
            UDP.send_data(data_array)
            cnt += 1
            print(f"Sent Data! cnt={cnt}")
    except Exception as e:
        print(f"Error in data_sender: {e}")
    finally:
        UDP.stop()
        print("Data sender thread done.")

# increases the number of sender threads to handle data faster
num_sender_threads = 3  # can adjust based on what system can handle
sender_threads = [threading.Thread(target=data_sender) for _ in range(num_sender_threads)]
capture_thread = threading.Thread(target=data_capture)

# starts threads
capture_thread.start()
for thread in sender_threads:
    thread.start()

# waits for threads to complete
capture_thread.join()
for thread in sender_threads:
    thread.join()

print("All threads have completed.")
