import ugradio
import threading
import numpy as np
import matplotlib as plt
import os
import argparse
import time

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

sdr = ugradio.SDR(sample_rate=3.2e6, center_freq=145.2e6, direct=False)

count = 0
data = []
storage_count = []
time_track = []
running = True

def run_vis(sdr):
	global count
	global date
	global storage_count
	global time_track
	global running

	while running:
		#starting at zero
		if count == 0:
			d = sdr.read_data() # reads data
			data_name = list(d.keys())[0] 
			data.append(d[data_name]) # appends data to 1
			count = d['acc_cnt'] # reassigns count to output
			print(count)
			storage_count.append(d['time']) # appends the time to time_track
		else: # all other cases
			d = sdr.read_data(count)
			data_name = list(d.keys())[0]
			data.append(d[data_name])
			count = d['acc_cnt']
			print(count)
			storage_count.append(count)
			time_track.append(d['time'])

# writes new npz file every 10 vis pulled with prefix argument
def writeto(prefix, folder):
	global count
	global data
	global storage_count
	global time_track
	global running

	track_files = 0
	while running:
		if len(storage_count) > 10:
			counts, times, stored = storage_count[:10], time_track[:10], data[:10]
			del storage_count[:10]
			del time_track[:10]
			del data[:10]

			# saves data to npz file
			filepath = os.path.join(folder, f'{prefix}_{track_files}.npz')
			np.savez(filepath, counts=counts, times=times, stored=stored)
			print(f'file number {track_files} has been written successfully!')
			track_files += 1

def tracktime():
	global running
	global len_obs

	time.sleep(len_obs)
	running = False

# initializes threads, brings back and releases daemons
reading = threading.Thread(target=run_vis, args=(sdr,))
writing = threading.Thread(target=writeto, args=(prefix, folder))
tracking = threading.Thread(target=tracktime)
reading.daemon = True
writing.daemon = True
tracking.daemon = True
reading.start()
writing.start()
tracking.start()
