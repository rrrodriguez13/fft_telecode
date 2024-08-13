import argparse
import os
import asyncio
import ugradio
from functions import send

# Arguments for when observing
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

async def data_sender(queue):
    cnt = 0
    try:
        while True:
            d = await queue.get()
            if d is None:
                break
            UDP.send_data(d)
            cnt += 1
            print(f"Sent Data! cnt={cnt}")
    finally:
        UDP.stop()
        print("Data transfer stopped ...")

async def main():
    queue = asyncio.Queue()

    sender_task = asyncio.create_task(data_sender(queue))

    try:
        while True:
            d = sdr.capture_data(num_samples)
            await queue.put(d)
    except KeyboardInterrupt:
        await queue.put(None)  # Signal sender task to exit
        await sender_task  # Wait for the sender to finish

    print("Main process done.")

if __name__ == "__main__":
    asyncio.run(main())
