import threading
import queue
import os
import matplotlib.pyplot as plt
import numpy as np
from functions import receive, writeto, initialize_plots, update_plot, correlate_and_plot

IP_ADDRESSES = ["10.10.10.60", "10.10.10.50"]
PORTS = [6374, 6372]

data_queues = {ip: queue.Queue(maxsize=10) for ip in IP_ADDRESSES}
plot_queues = {ip: queue.Queue(maxsize=10) for ip in IP_ADDRESSES}
stop_event = threading.Event()

def data_receiver(ip, port):
    udp = receive(ip, port)
    udp.eth0()
    while not stop_event.is_set():
        data = udp.set_up()
        if data:
            data_queues[ip].put(data)
    data_queues[ip].put(None)

def data_processor(ip):
    track_files = 0
    folder = 'output'
    prefix = 'data'
    if not os.path.exists(folder):
        os.makedirs(folder)

    while True:
        data = data_queues[ip].get()
        if data is None:
            break
        spectrum = np.frombuffer(data, dtype=np.uint8).reshape(-1, 2)
        track_files += 1
        writeto(spectrum, prefix, folder, track_files)
        plot_queues[ip].put((spectrum, track_files))

def plot_data():
    fig, axs, lines = initialize_plots(IP_ADDRESSES)
    last_spectrum = {ip: None for ip in IP_ADDRESSES}

    while not stop_event.is_set():
        for ip in IP_ADDRESSES:
            if not plot_queues[ip].empty():
                item = plot_queues[ip].get()
                if item is None:
                    continue
                spectrum, _ = item
                update_plot(spectrum, fig, lines[IP_ADDRESSES.index(ip)])
                last_spectrum[ip] = spectrum

        if len(last_spectrum) == 2 and all(last_spectrum.values()):
            try:
                correlate_and_plot(last_spectrum[IP_ADDRESSES[0]], last_spectrum[IP_ADDRESSES[1]], fig, axs)
                plt.draw()
                plt.pause(0.1)
            except Exception as e:
                print(f'Correlation error: {e}')

    plt.ioff()
    plt.show()

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
        pass
    finally:
        stop_event.set()
        for thread in receiver_threads:
            thread.join()
        for thread in processor_threads:
            data_queues[thread.name.split('-')[1]].put(None)
            thread.join()
