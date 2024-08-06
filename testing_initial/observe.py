import argparse
import os
import time
import ugradio
import functions
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

LAPTOP_IP = "192.168.0.234"
PORT = 6371
num_samples = 2048

if not os.path.exists(folder):
    os.makedirs(folder)

# sets up SDR
sdr = ugradio.sdr.SDR(sample_rate=3.2e6, center_freq=125.2e6, direct=False)

# sets up network connection
UDP = send(LAPTOP_IP, PORT)

try:
    while True:
        d = sdr.capture_data(num_samples)
        UDP.send_data(d)
        #files = d.run_vis(sdr, prefix, folder)
        #time.sleep(1)
        print("Sent Data! \n")
except KeyboardInterrupt:
    UDP.stop()
    print("Data transfer stopped ...")
finally:
    print("Done.")

