import argparse
import os
import threading
import queue
import ugradio
import numpy as np
from functions_test import send
import datetime
import time

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

def format_time(seconds_elapsed):
    # Extract components from total seconds
    hours, remainder = divmod(seconds_elapsed, 3600)
    minutes, remainder = divmod(remainder, 60)
    seconds, milliseconds = divmod(remainder, 1)
    milliseconds, microseconds = divmod(milliseconds * 1e3, 1)
    microseconds, nanoseconds = divmod(microseconds * 1e3, 1)

    # Format the time as HH:MM:SS.mmmuuuunnn
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}.{int(milliseconds):03}{int(microseconds):03}{int(nanoseconds):03}"

def data_capture():
    try:
        a = 0
        b = num_samples
        
        # Capture the start time of the data collection
        t_start = time.time()

        while not stop_event.is_set():
            lst = np.arange(a, b)  # list of integers to attach to data
            
            # calculates t1 and t2 as the time elapsed since t_start
            t1 = time.time() - t_start
            data = sdr.capture_data(num_samples)  # data
            t2 = time.time() - t_start
            
            data.shape = (-1, 2)  # data shape
            i = data[:, 0]  # first column
            q = data[:, 1]  # second column
            data = i + 1j*q

            # calculates the time difference
            time_diff = t2 - t1

            # prints elapsed time between recorded times
            print(f"t1 (seconds elapsed): {t1:.6f}")
            print(f"t2 (seconds elapsed): {t2:.6f}")
            print("")
            print("Time Difference: {:.6f}".format(time_diff))  # prints difference in recorded times
            print("")

            array = np.vstack((lst, data))  # array defined as 2 columns for integers and data
            print(f"Captured data shape: {array.shape}")  # prints shape of data captured

            data_queue.put(array)  # puts the queue into array
            
            # adds num_samples to continue collection past one sample packet size
            a += num_samples
            b += num_samples
    except KeyboardInterrupt:
        stop_event.set()
    finally:
        data_queue.put(None)  # signal sender threads to exit
        print("Capture thread done.")

def data_sender():
    try:
        cnt = 0
        while not stop_event.is_set() or not data_queue.empty():
            data_array = data_queue.get()
            if data_array is None:
                break
            print(f"Sending data shape: {data_array.shape}")  # prints shape of data being sent
            print("")
            UDP.send_data(data_array)
            cnt += 1
            print(f"Sent Data! [cnt={cnt}]")
            print("")
    except Exception as e:
        print(f"Error in data_sender: {e}")
    finally:
        UDP.stop()
        print("Data transfer stopped.")


# increases the number of sender threads to handle data faster
num_sender_threads = 3  # can adjust based on what system can handle
capture_thread = threading.Thread(target=data_capture)
sender_threads = [threading.Thread(target=data_sender) for _ in range(num_sender_threads)]

# starts threads
capture_thread.start()
for thread in sender_threads:
    thread.start()

# joins threads to wait for completion
capture_thread.join()
for thread in sender_threads:
    thread.join()

print("All threads have completed.")
