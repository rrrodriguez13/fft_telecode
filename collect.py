import argparse
import os
import ugradio
import functions

parser = argparse.ArgumentParser()
parser.add_argument('--prefix', '-p')
parser.add_argument('--len_obs', '-l')
parser.add_argument('--folder', '-f', default='output')

args = parser.parse_args()

prefix = args.prefix
len_obs = int(args.len_obs)
folder = args.folder

if not os.path.exists(folder):
    os.makedirs(folder)

sdr = ugradio.sdr.SDR(sample_rate=3.2e6, center_freq=125.2e6, direct=False)

functions.run_vis(sdr, prefix, folder)
