import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import os

num_samples = 2048
sample_rate = 2.2e6
center_freq = 145.2e6
freqs = np.fft.fftshift(np.fft.fftfreq(num_samples, 1/sample_rate) + center_freq)


def writeto(data, prefix, folder, track_files):
    filepath = os.path.join(folder, f'{prefix}_{track_files:05d}.npz')
    np.savez(filepath, data=data) # saves data to output folder

def perform_power(signal):
    return np.abs(signal)**2
    
def shift(signal):
    return np.fft.fftshift(signal)

def correlate_signals(signal1, signal2):
    correlation = signal.correlate(signal1/np.std(signal1), signal2/np.std(signal2), mode='full') / min(len(signal1), len(signal2))
    return correlation

