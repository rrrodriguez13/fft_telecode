import threading
import queue
import os
import matplotlib.pyplot as plt
import numpy as np
from functions_test import writeto, initialize_plots, update_plot, correlate_and_plot
from networking import UdpReceive

num_samples = 2048

# Configuration
IP_ADDRESSES = ["10.10.10.60", "10.10.10.50"]
PORTS = [6373, 6372] # using different ports for easy identification
DATA_QUEUE_SIZE = 100

data_queues = {ip: queue.Queue(maxsize=DATA_QUEUE_SIZE) for ip in IP_ADDRESSES}
plot_queues = {ip: queue.Queue(maxsize=DATA_QUEUE_SIZE) for ip in IP_ADDRESSES}
stop_event = threading.Event()

def data_receiver(ip, port):
    UDP = UdpReceive(ip, port)
    UDP.eth0()
    print(f'Listening on {ip}:{port} ...')

    try:
        while not stop_event.is_set():
            data = UDP.set_up()
            if data: 
                data_queues[ip].put(data)
    except KeyboardInterrupt:
        print(f'Data receiver for {ip} interrupted.')
    finally:
        UDP.stop()
        data_queues[ip].put(None)  # Signal to stop processing
        print(f'Receiver for {ip} done.')

def data_processor(ip):
    folder1 = 'num_output' # creates output folder for numbered list
    folder2 = 'data_output' # creates output folder for actual data
    prefix1 = 'num' # prefix for numbered list
    prefix2 = 'data' # prefix for data
    track_files = 0  # counter for the number of files saved

    if not os.path.exists(folder1):
        os.makedirs(folder1)

    if not os.path.exists(folder2):
        os.makedirs(folder2)

    try:
        while True:
            data = data_queues[ip].get()
            if data is None:
                print("No data received. Do better.")
                break

            signal = np.frombuffer(data, dtype=np.int8)
            #print(signal.shape)
            signal.shape = (2, -1)
            print(f"Data shape for {ip}: {signal.shape}")

            num_row = signal[0] # first row of array (num)
            data_row = signal[1] # second row of array (data)

            # Save the data to a file
            track_files += 1
            writeto(num_row, prefix1, folder1, track_files)
            writeto(data_row, prefix2, folder2, track_files)

            # Put the data in the plot queue
            plot_queues[ip].put((data_row, track_files))

            data_queues[ip].task_done()
    except Exception as e:
        print(f'Error in data processor for {ip}: {e}')
    finally:
        plot_queues[ip].put(None)  # Signal to stop plotting
        print(f'Processor for {ip} done.')

def plot_data():
    fig, axs, lines = initialize_plots(IP_ADDRESSES)
    last_signal = {ip: None for ip in IP_ADDRESSES}
    counters = {ip: 0 for ip in IP_ADDRESSES}  # Initialize counters for each IP

    try:
        while not stop_event.is_set():
            # Process data from each IP address
            for ip in IP_ADDRESSES:
                if not plot_queues[ip].empty():
                    item = plot_queues[ip].get()
                    if item is None:
                        continue

                    signal, track_files = item  # Unpack the signal and track_files from the item tuple
                    try:
                        update_plot(signal, fig, lines[IP_ADDRESSES.index(ip)])
                        last_signal[ip] = signal

                        # Update the counter and plot title
                        counters[ip] += 1
                        axs[IP_ADDRESSES.index(ip)].set_title(f'Signal Data for {ip} [cnt: #{counters[ip]}]')

                    except Exception as e:
                        print(f'Error updating plot for {ip}: {e}')

            # Correlate signals if we have data from both IPs
            if len(IP_ADDRESSES) >= 2:
                ip1, ip2 = IP_ADDRESSES[:2]
                if last_signal[ip1] is not None and last_signal[ip2] is not None:
                    correlate_and_plot(last_signal[ip1], last_signal[ip2], fig, axs)
            
            # This pause causes the live plotter to close for some reason
            #plt.pause(0.01)  # Small pause to update the plots in real-time

    except KeyboardInterrupt:
        print('Plotting interrupted.')
    finally:
        print('Plotting done.')

if __name__ == "__main__":
    receiver_threads = [threading.Thread(target=data_receiver, args=(ip, port)) for ip, port in zip(IP_ADDRESSES, PORTS)]
    processor_threads = [threading.Thread(target=data_processor, args=(ip,)) for ip in IP_ADDRESSES]
    plotting_thread = [threading.Thread(target=plot_data)]

    for thread in receiver_threads:
        thread.start()
    for thread in processor_threads:
        thread.start()
    for thread in plotting_thread:
        thread.start()
    '''
    *keeping this seems to shut down the script as soon as it starts*
    #try:
        #plot_data()
    #except KeyboardInterrupt:
        #print('Main thread interrupted.')
    #finally:
        #stop_event.set()  # Signal all threads to stop
    '''
    for thread in receiver_threads:
        thread.join()
    for thread in processor_threads:
        data_queues[thread.name.split('-')[1]].put(None)  # Signal processor threads to exit
        thread.join()
    for thread in plotting_thread:
        thread.join()
    print('Main thread done.')
