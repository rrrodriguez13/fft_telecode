import threading
import queue
import os
import time
import numpy as np
from functions_test import writeto
from networking import UdpReceive, NUM_SAMPLES

# configuration
IP_ADDRESSES = ["10.10.10.20", "10.10.10.30", "10.10.10.40", "10.10.10.50"] # each pi has a unique static IP
PORTS = [6372, 6373, 6374, 6375] # using different ports for easy identification
DATA_QUEUE_SIZE = 10000
BLOCKS_PER_FILE = 128

data_queues = {ip: queue.Queue(maxsize=DATA_QUEUE_SIZE) for ip in IP_ADDRESSES}
stop_event = threading.Event()

def receive_data(ip, port):
    UDP = UdpReceive(ip, port)
    UDP.eth0()
    print(f'Listening on {ip}:{port} ...')

    q = data_queues[ip]

    try:
        while not stop_event.is_set():
            data = UDP.get_data()
            if data: 
                q.put(data)
    except KeyboardInterrupt:
        print(f'Data receiver for {ip} interrupted.')
    finally:
        UDP.stop()
        q.put(None)  # Signal to stop processing
        print(f'Receiver for {ip} done.')

def process_data(ip, verbose=True):
    folder = f'output2_{ip}' # creates output folder for numbered list
    prefix = 'data' # prefix for numbered list
    track_files = 0  # counter for the number of files saved

    if not os.path.exists(folder):
        os.makedirs(folder)

    q = data_queues[ip]
    try:
        cnt = 0
        while True:
            if q.qsize() < BLOCKS_PER_FILE:
                time.sleep(0.1)
                continue
            d = b''.join([q.get() for i in range(BLOCKS_PER_FILE)])
            if d is None:
                print("No data received.")
                break

            data = np.frombuffer(d, dtype=np.int8)
            data.shape = (BLOCKS_PER_FILE, -1, 2)

            # saves data to a file
            if verbose:
                print(f"Writing file {track_files}")
                print(f"Current Queue Size {q.qsize()}")
            track_files += 1
            writeto(data, prefix, folder, track_files)

            q.task_done()

            # ensures clean break
            if stop_event is set:
                break
    except Exception as e:
        print(f'Error in data processor for {ip}: {e}')
    finally:
        print(f'Processor for {ip} done.')


if __name__ == "__main__":
    receiver_threads = [threading.Thread(target=receive_data, args=(ip, port)) for ip, port in zip(IP_ADDRESSES, PORTS)]
    processor_threads = [threading.Thread(target=process_data, args=(ip,)) for ip in IP_ADDRESSES]

    for thread in receiver_threads:
        thread.start()
    for thread in processor_threads:
        thread.start()

    for thread in receiver_threads:
        thread.join()
    for thread in processor_threads:
        data_queues[thread.name.split('-')[1]].put(None)  # Signal processor threads to exit
        thread.join()

    print('Main thread done.')
