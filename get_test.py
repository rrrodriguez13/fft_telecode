import threading
import queue
import os
import matplotlib.pyplot as plt
import numpy as np
from functions import receive, writeto, initialize_plots, update_plot, correlate_and_plot

IP_ADDRESSES = ["10.10.10.40", "10.10.10.50"]
PORTS = [6371, 6372]
DATA_QUEUE_SIZE = 10
num_samples = 2048

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
                print(f"Received data size: {len(data)} bytes")
                data_queues[ip].put(data)
    except KeyboardInterrupt:
        print(f'Data receiver for {ip} interrupted.')
    finally:
        UDP.stop()
        data_queues[ip].put(None)
        print(f'Receiver for {ip} done.')

def data_processor(ip):
    folder = 'output'
    prefix = 'data'
    track_files = 0

    if not os.path.exists(folder):
        os.makedirs(folder)

    try:
        while True:
            data = data_queues[ip].get()
            if data is None:
                break

            spectrum = np.frombuffer(data, dtype=np.uint8)
            if spectrum.size == 2 * num_samples:
                spectrum.shape = (-1, 2)
            else:
                print(f"Unexpected data size for {ip}: {spectrum.size}")
                continue

            track_files += 1
            writeto(spectrum, prefix, folder, track_files)
            plot_queues[ip].put((spectrum, track_files))

            data_queues[ip].task_done()
    except Exception as e:
        print(f'Error in data processor for {ip}: {e}')
    finally:
        plot_queues[ip].put(None)
        print(f'Processor for {ip} done.')

def plot_data():
    fig, axs, lines = initialize_plots(IP_ADDRESSES)
    last_spectrum = {ip: None for ip in IP_ADDRESSES}

    try:
        while not stop_event.is_set():
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

            if len(last_spectrum) == 2 and all(last_spectrum.values()):
                ip1, ip2 = IP_ADDRESSES
                try:
                    correlate_and_plot(last_spectrum[ip1], last_spectrum[ip2], fig, axs)
                    plt.draw()
                    plt.pause(0.1)
                except Exception as e:
                    print(f'Error in correlation plotting: {e}')

    except KeyboardInterrupt:
        print('Plotting interrupted.')
    finally:
        plt.ioff()
        plt.show()

def start_data_processing():
    threads = []

    for ip, port in zip(IP_ADDRESSES, PORTS):
        thread = threading.Thread(target=data_receiver, args=(ip, port))
        thread.start()
        threads.append(thread)

    for ip in IP_ADDRESSES:
        thread = threading.Thread(target=data_processor, args=(ip,))
        thread.start()
        threads.append(thread)

    plot_thread = threading.Thread(target=plot_data)
    plot_thread.start()
    threads.append(plot_thread)

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    start_data_processing()
