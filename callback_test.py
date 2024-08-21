#import ugradio
import numpy as np
import sdr_stream

cnt = 0

def file_writer(dev_id, shape, data):
    global cnt
    filename = f'sdr_data{cnt:03d}.npz'
    print(f'Saving data to {filename}')
    np.savez(filename, data=data)
    cnt += 1
    
sdr = sdr_stream.SDR(sample_rate=2.2e6, center_freq=145.2e6, direct=False, gain=10)
sdr_stream.capture_data(sdr, nblocks=128, callback=file_writer)
