import functions
from functions import receive, writeto, set_up_plot, plotter
import numpy as np
import os
import threading
import queue

# networking
LAPTOP_IP = "192.168.0.234"
RPI_IP = "192.168.0.235"
PORT = 6371

def receiver_main():
    UDP = receive(LAPTOP_IP, PORT)
    UDP.eth0()
    print('Everything Initialized ...')

    # defines folder and prefix for saving files
    folder = 'output'
    prefix = 'data'
    track_files = 0  # counter for the number of files saved

    fig, line = set_up_plot()

    if not os.path.exists(folder):
        os.makedirs(folder)

    data_queue = queue.Queue()

    def producer():
        try:
            while True:
                data = UDP.set_up()
                if data:
                    data_queue.put(data)
        except KeyboardInterrupt:
            UDP.stop()
            print('UDP stopping...')
        finally:
            print('Producer done.')

    def consumer():
        try:
            nonlocal track_files
            while True:
                data = data_queue.get()
                if data is None:
                    break

                spectrum = np.frombuffer(data, dtype=np.uint8)
                spectrum.shape = (-1, 2)
                print("Data shape:", spectrum.shape)

                # save the data to a file
                track_files += 1
                writeto(spectrum, prefix, folder, track_files)

                # plots the data
                plotter(spectrum, fig, line, folder, prefix, track_files)
                data_queue.task_done()
        except KeyboardInterrupt:
            print('Consumer stopping...')
        finally:
            print('Consumer done.')

    # Start producer and consumer threads
    producer_thread = threading.Thread(target=producer)
    consumer_thread = threading.Thread(target=consumer)

    producer_thread.start()
    consumer_thread.start()

    producer_thread.join()
    data_queue.put(None)  # Signal consumer to exit
    consumer_thread.join()

    print('All done.')

if __name__ == "__main__":
    # receiving script (not sending)
    receiver_main()
