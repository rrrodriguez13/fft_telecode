import threading
import queue
import numpy as np
import os
import matplotlib.pyplot as plt
from functions import receive, writeto, set_up_plot, plotter

# Networking
LAPTOP_IP = "192.168.0.234"
PORT = 6371

data_queue = queue.Queue(maxsize=10)
plot_queue = queue.Queue(maxsize=10)
stop_event = threading.Event()

def data_receiver():
    UDP = receive(LAPTOP_IP, PORT)
    UDP.eth0()
    print('Everything Initialized ...')

    try:
        while not stop_event.is_set():
            data = UDP.set_up()
            if data:
                data_queue.put(data)
    except KeyboardInterrupt:
        print('Data receiver interrupted.')
    finally:
        UDP.stop()
        data_queue.put(None)  # Signal to stop processing
        print('Receiver done.')

def data_processor():
    folder = 'output'
    prefix = 'data'
    track_files = 0  # counter for the number of files saved

    if not os.path.exists(folder):
        os.makedirs(folder)

    try:
        while True:
            data = data_queue.get()
            if data is None:
                break

            spectrum = np.frombuffer(data, dtype=np.uint8)
            spectrum.shape = (-1, 2)
            print("Data shape:", spectrum.shape)
            
            # save the data to a file
            track_files += 1
            #writeto(spectrum, prefix, folder, track_files)

            # put the data in the plot queue
            plot_queue.put((spectrum, track_files))

            data_queue.task_done()
    except KeyboardInterrupt:
        print('Data processor interrupted.')
    finally:
        plot_queue.put(None)  # Signal to stop plotting
        print('Processor done.')

def plot_data():
    fig, line = set_up_plot()

    try:
        while True:
            all_spectra = np.empty((100, 2048, 2))
            for i in range(100):
            
                item = plot_queue.get()
                spectrum, track_files = item
                all_spectra[i] = spectrum
            avg_spectra = np.mean(all_spectra, axis=0)
            plotter(avg_spectra, fig, line, 'output', 'data', track_files/100)

            plot_queue.task_done()
    except KeyboardInterrupt:
        print('Plotting interrupted.')
    finally:
        plt.ioff()
        plt.show()
        print('Plotting done.')

if __name__ == "__main__":
    receiver_thread = threading.Thread(target=data_receiver)
    processor_thread = threading.Thread(target=data_processor)

    receiver_thread.start()
    processor_thread.start()

    try:
        plot_data()
    except KeyboardInterrupt:
        print('Main thread interrupted.')
    finally:
        # Signal all threads to stop
        stop_event.set()
        receiver_thread.join()
        data_queue.put(None)  # Signal processor thread to exit
        processor_thread.join()
        print('Main thread done.')
