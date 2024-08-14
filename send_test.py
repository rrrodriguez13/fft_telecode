import argparse
import os
import asyncio
import ugradio
from functions_test import send

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
sdr = ugradio.sdr.SDR(sample_rate=2.2e6, center_freq=145.2e6, direct=False, gain=20)

# sets up network connection
UDP = send(LAPTOP_IP, PORT)

# async send data function
async def data_sender(queue, stop_event):
    try:
        cnt = 0
        while not stop_event.is_set() or not queue.empty():
            d = await queue.get()
            if d is None:
                break
            UDP.send_data(d)
            cnt += 1
            print(f"Sent Data! cnt={cnt}")
    except Exception as e:
        print(f"Error in data_sender: {e}")
    finally:
        UDP.stop()
        print("Data transfer stopped.")

# async capture data function
async def data_producer(queue, stop_event):
    try:
        while not stop_event.is_set():
            d = sdr.capture_data(num_samples)
            await queue.put(d)
    except KeyboardInterrupt:
        stop_event.set()
    finally:
        await queue.put(None)  # signal sender to exit

async def main():
    data_queue = asyncio.Queue()
    stop_event = asyncio.Event()

    # creates producer and sender tasks
    producer_task = asyncio.create_task(data_producer(data_queue, stop_event))
    sender_tasks = [asyncio.create_task(data_sender(data_queue, stop_event)) for _ in range(3)]

    try:
        await producer_task  # waits for the producer to finish
        await asyncio.gather(*sender_tasks)  # waits for all sender tasks to finish
    except KeyboardInterrupt:
        stop_event.set()
        await producer_task
        await asyncio.gather(*sender_tasks)
    finally:
        print("Main function done.")

# runs the asyncio event loop
asyncio.run(main())
