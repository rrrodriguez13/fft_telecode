import argparse
import os
import threading
import queue
import ugradio
from functions import send

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prefix', '-p', default='data')
    parser.add_argument('--len_obs', '-l', default='60', type=int)
    parser.add_argument('--folder', '-f', default='output')
    return parser.parse_args()

def main():
    args = parse_args()
    folder = args.folder

    if not os.path.exists(folder):
        os.makedirs(folder)

    sdr = ugradio.sdr.SDR(sample_rate=3.2e6, center_freq=145.2e6, direct=False)
    udp = send("10.10.10.30", 6372)

    data_queue = queue.Queue()
    stop_event = threading.Event()

    def data_sender():
        while not stop_event.is_set() or not data_queue.empty():
            data = data_queue.get()
            if data is None:
                break
            udp.send_data(data)

    sender_thread = threading.Thread(target=data_sender)
    sender_thread.start()

    try:
        while not stop_event.is_set():
            data = sdr.capture_data(2048)
            data_queue.put(data)
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        data_queue.put(None)
        sender_thread.join()

if __name__ == "__main__":
    main()
