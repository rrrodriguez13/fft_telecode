import threading
import queue
import os
import matplotlib.pyplot as plt
import numpy as np
from functions2 import receive, writeto, initialize_plots, update_plot, correlate_and_plot

# Configuration
IP_ADDRESSES = ["10.10.10.60", "10.10.10.50"]
PORTS = [6374, 6372]  # Different ports for each IP
DATA_QUEUE_SIZE = 10

data_queues = {ip: queue.Queue(maxsize=DATA_QUEUE_SIZE) for ip in IP_ADDRESSES}
plot_queues = {ip: queue.Queue(maxsize=DATA_QUEUE_SIZE) for ip in IP_ADDRESSES}
stop_event = threading.Event()

def data_receiver(ip, port):
    UDP = receive(ip, port)
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
    folder = 'output'
    prefix = 'data'
    track_files = 0  # counter for the number of files saved

    if not os.path.exists(folder):
        os.makedirs(folder)

    try:
        while True:
            data = data_queues[ip].get()
            if data is None:
                break

            spectrum = np.frombuffer(data, dtype=np.uint8)
            spectrum.shape = (-1, 2)
            print(f"Data shape for {ip}: {spectrum.shape}")

            # Save the data to a file
            track_files += 1
            writeto(spectrum, prefix, folder, track_files)

            # Put the data in the plot queue
            plot_queues[ip].put((spectrum, track_files))

            data_queues[ip].task_done()
    except Exception as e:
        print(f'Error in data processor for {ip}: {e}')
    finally:
        plot_queues[ip].put(None)  # Signal to stop plotting
        print(f'Processor for {ip} done.')

def plot_data():
    fig, axs, lines = initialize_plots(IP_ADDRESSES)
    last_spectrum = {ip: None for ip in IP_ADDRESSES}

    try:
        while not stop_event.is_set():
            # Process data from each IP address
            for ip in IP_ADDRESSES:
                if not plot_queues[ip].empty():
                    item = plot_queues[ip].get()
                    if item is None:
                        continue

                    spectrum, track_files = item
                    try:
                        update_plot(spectrum, fig, lines[IP_ADDRESSES.index(ip)])
                        last_spectrum[ip] = spectrum
                    except Exception as e:
                        print(f'Error updating plot for {ip}: {e}')

            # Check if we have data from at least two IPs for correlation
            if len(last_spectrum) == 2 and all(last_spectrum.values()):
                ip1, ip2 = IP_ADDRESSES
                try:
                    correlate_and_plot(last_spectrum[ip1], last_spectrum[ip2], fig, axs)
                    plt.draw()  # Ensure the plot is updated
                    plt.pause(0.1)  # Adjust or comment out if needed
                except Exception as e:
                    print(f'Error in correlation plotting: {e}')

    except KeyboardInterrupt:
        print('Plotting interrupted.')
    finally:
        plt.ioff()
        plt.show()
        print('Plotting done.')

if __name__ == "__main__":
    receiver_threads = [threading.Thread(target=data_receiver, args=(ip, port)) for ip, port in zip(IP_ADDRESSES, PORTS)]
    processor_threads = [threading.Thread(target=data_processor, args=(ip,)) for ip in IP_ADDRESSES]

    for thread in receiver_threads:
        thread.start()
    for thread in processor_threads:
        thread.start()

    try:
        plot_data()
    except KeyboardInterrupt:
        print('Main thread interrupted.')
    finally:
        stop_event.set()  # Signal all threads to stop
        for thread in receiver_threads:
            thread.join()
        for thread in processor_threads:
            data_queues[thread.name.split('-')[1]].put(None)  # Signal processor threads to exit
            thread.join()
        print('Main thread done.')
