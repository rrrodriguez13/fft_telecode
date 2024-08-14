import argparse
import os
import asyncio
import ugradio
from functions_test import send
import numpy as np
import socket

# Argument parsing for observation configuration
parser = argparse.ArgumentParser()
parser.add_argument('--prefix', '-p', default='data')
parser.add_argument('--len_obs', '-l', default='120')
parser.add_argument('--folder', '-f', default='output')
args = parser.parse_args()

prefix = args.prefix
len_obs = int(args.len_obs)
folder = args.folder

LAPTOP_IP = "10.10.10.30"
PORT = 6373
num_samples = 2048
ACK_PORT = 6374  # Port for acknowledgment messages
MAX_RETRIES = 3  # Max retries for sending data

if not os.path.exists(folder):
    os.makedirs(folder)

# Set up SDR
sdr = ugradio.sdr.SDR(sample_rate=2.2e6, center_freq=145.2e6, direct=False, gain=20)

# Set up network connection
UDP = send(LAPTOP_IP, PORT)

# Increase socket buffer size
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2**21)  # Increase buffer size

# Acknowledgment socket setup
ack_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ack_sock.bind(("", ACK_PORT))
ack_sock.settimeout(1.0)  # Timeout for waiting for ACK

async def data_producer(nsamples, data_queue, stop_event):
    try:
        while not stop_event.is_set():
            # Capture data using the SDR in a separate thread
            data = await asyncio.to_thread(sdr.capture_data, nsamples)
            await data_queue.put(data)
    except Exception as e:
        print(f"Error in data_producer: {e}")

async def data_sender(data_queue, stop_event):
    try:
        cnt = 0
        while not stop_event.is_set() or not data_queue.empty():
            data = await data_queue.get()
            if data is None:
                break
            # Add sequence number to the data
            sequence_number = cnt.to_bytes(4, 'big')
            packet = sequence_number + data

            # Send data with retry mechanism
            for _ in range(MAX_RETRIES):
                UDP.send_data(packet)
                try:
                    ack, _ = ack_sock.recvfrom(1024)
                    if ack == sequence_number:
                        print(f"Received ACK for packet {cnt}")
                        break
                except socket.timeout:
                    print(f"ACK not received for packet {cnt}, retrying...")
            else:
                print(f"Failed to receive ACK after {MAX_RETRIES} retries for packet {cnt}")
                
            cnt += 1
            data_queue.task_done()
    except Exception as e:
        print(f"Error in data_sender: {e}")
    finally:
        UDP.stop()
        print("Data transfer stopped.")

async def main():
    stop_event = asyncio.Event()
    data_queue = asyncio.Queue(maxsize=10)
    
    producer_task = asyncio.create_task(data_producer(num_samples, data_queue, stop_event))
    sender_task = asyncio.create_task(data_sender(data_queue, stop_event))
    
    # Run the producer for the observation duration
    await asyncio.sleep(len_obs)
    stop_event.set()  # Signal to stop producing and sending data
    
    # Wait for the producer to finish
    await producer_task
    await data_queue.put(None)  # Signal the sender to exit
    await sender_task

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        print(f"RuntimeError: {e}")
