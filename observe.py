import argparse
import ugradio
from functions import send

# Arguments for when observing
parser = argparse.ArgumentParser()

parser.add_argument('--prefix', '-p', default='data')
parser.add_argument('--len_obs', '-l', default='60')
parser.add_argument('--folder', '-f', default='output')
parser.add_argument('--laptop_ip', '-I', default='192.168.0.234')
parser.add_argument('--samp_rate', '-S', default='3.2e6')
parser.add_argument('--cent_freq', '-F', default='125.2e6')
parser.add_argument('--port', '-P', default='6371')

args = parser.parse_args()

prefix = args.prefix
len_obs = int(args.len_obs)
folder = args.folder
LAPTOP_IP = args.laptop_ip
sample_rate = int(args.samp_rate)
center_freq = int(args.cent_freq)
PORT = args.port

# sets up SDR
sdr = ugradio.sdr.SDR(sample_rate, center_freq, direct=False)

# sets up network connection
UDP = send(LAPTOP_IP, PORT)

while True:
    d = sdr.capture_data()
    UDP.send_data(d)