import threading
import queue
import os
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from functions_test import writeto
from networking import UdpReceive, NUM_SAMPLES
from time import sleep

# Configuration
IP_ADDRESSES = ["10.10.10.20", "10.10.10.30", "10.10.10.40", "10.10.10.50"]  # each device has a unique static IP
PORTS = [6372, 6373, 6374, 6375]  # using different ports for easy identification
DATA_QUEUE_SIZE = 10000
BLOCKS_PER_FILE = 128

data_queues = {ip: queue.Queue(maxsize=DATA_QUEUE_SIZE) for ip in IP_ADDRESSES}  # queue for data
plot_queues = {ip: queue.Queue(maxsize=10) for ip in IP_ADDRESSES}  # queue for plotting
stop_event = threading.Event()

# Parameters for Time and Phase comparison
sampling_rate = 2.2e6  # sample rate in Hz
num_samples = 2048  # number of samples
offset = 0
time_num = 12 * num_samples
t = np.arange(time_num) * 1 / sampling_rate
phazor = np.exp(2 * np.pi * 1j * 0.2e6 * t)  
time = t * 1e3  # time in milliseconds

# functions
def radian_formatter(x, pos):
    """Formats the y-axis in multiples of π."""
    return f'{x / np.pi:.1f}π' if x != 0 else '0'

def receive_data(ip, port):
    """Receives data from a UDP source."""
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
        q.put(None)  # signal to stop processing
        print(f'Receiver for {ip} done.')

def process_data(ip, verbose=True):
    """Processes data, writes to files, and queues data for live plotting."""
    folder = f'output_{ip}'  # creates output folder for numbered list
    prefix = 'data'  # prefix for numbered list
    track_files = 0  # counter for the number of files saved

    if not os.path.exists(folder):
        os.makedirs(folder)

    q = data_queues[ip]
    plot_q = plot_queues[ip]  # gets the corresponding plot queue

    try:
        while True:
            if q.qsize() < BLOCKS_PER_FILE:
                sleep(0.1)
                continue

            d = b''.join([q.get() for i in range(BLOCKS_PER_FILE)])
            if d is None:
                print("No data received.")
                break

            data = np.frombuffer(d, dtype=np.int8)
            data.shape = (BLOCKS_PER_FILE, -1, 2)

            # Converts to complex data and add to plot queue
            complex_data = data[..., 0] + 1j * data[..., 1]
            if not plot_q.full():
                plot_q.put(complex_data)

            # Saves data to a file
            if verbose:
                #print(f"Writing file {track_files}")  # comment out with 'writeto' below to avoid confusion
                print(f'Plotting file {track_files}')
                print(f"Current Queue Size {q.qsize()}")
            track_files += 1
            #writeto(data, prefix, folder, track_files) # comment out to not save data 

            q.task_done()

            # Ensure clean break
            if stop_event.is_set():
                break
    except Exception as e:
        print(f'Error in data processor for {ip}: {e}')
    finally:
        print(f'Processor for {ip} done.')

# Main
if __name__ == "__main__":
    receiver_threads = [threading.Thread(target=receive_data, args=(ip, port)) for ip, port in zip(IP_ADDRESSES, PORTS)]
    processor_threads = [threading.Thread(target=process_data, args=(ip,)) for ip in IP_ADDRESSES]

    # starts receiver and processor threads
    for thread in receiver_threads:
        thread.start()
    for thread in processor_threads:
        thread.start()

    # Plots in the main thread
    plt.ion()  # enables interactive mode
    plt.style.use('bmh')
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_title('Time and Phase Comparison', fontsize=20)
    ax.set_xlabel('Time [milliseconds]', fontsize=16)
    ax.set_ylabel('Phase [radians]', fontsize=16)
    ax.tick_params(axis='x', labelsize=14)
    ax.tick_params(axis='y', labelsize=14)
    ax.set_xlim(0, time[:time_num].max())
    ax.set_ylim(-np.pi-0.1, np.pi+0.1)
    ax.yaxis.set_major_formatter(FuncFormatter(radian_formatter))
    lines = {ip: ax.plot([], [], label=ip)[0] for ip in IP_ADDRESSES}
    ax.legend(loc='upper right', framealpha=1, frameon=True, facecolor='lightgray', edgecolor='k', fontsize=14)

    try:
        while not stop_event.is_set():
            for ip in IP_ADDRESSES:
                plot_q = plot_queues[ip]
                if not plot_q.empty():
                    data_comp = plot_q.get()
                    phase_data = np.unwrap(np.angle(data_comp.ravel()[offset:offset+time_num] * phazor)) / np.pi
                    lines[ip].set_data(time[:len(phase_data)], phase_data)
            #ax.relim()
            #ax.autoscale_view()
            plt.pause(0.1)  # Adjust to control update speed
    except KeyboardInterrupt:
        stop_event.set()
    finally:
        for thread in receiver_threads + processor_threads:
            thread.join()

    print("Main thread done.")
