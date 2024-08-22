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



"""
def initialize_plots(ip_addresses):
    plt.style.use('bmh')
    plt.ion() # live plotter
    num_plots = len(ip_addresses) + 1  # correlation plot is added to IP plots
    fig, axs = plt.subplots(num_plots, 1, figsize=(12, 6 * num_plots), sharex=False)
    if num_plots == 1:
        axs = [axs]  # ensures axs is iterable if only one subplot

    lines = []
    for ax, ip in zip(axs[:-1], ip_addresses):  # subplots for IP addresses
        line, = ax.semilogy(freqs / 1e6, np.ones_like(freqs), linewidth=0.8, label='Signal')
        lines.append(line)
        ax.set_title(f'Signal Data from {ip}')
        ax.set_xlabel('Frequency [MHz]')
        ax.set_ylabel('Power [arbitrary]')
        ax.grid(color='dimgray')
        ax.legend(loc='best')
        ax.set_ylim(1e1, 1e11)
    
    plt.tight_layout()
    return fig, axs, lines

def update_plot(data, fig, line):
    #d = data[..., 0] + 1j * data[..., 1]
    d = data
    pwr = shift(perform_power(np.fft.fft(d)))

    # plots new data and flushes previous data
    line.set_ydata(pwr)
    fig.canvas.draw()
    fig.canvas.flush_events()

# clock formatting
def format_time(seconds_elapsed):
    # Extract components from total seconds
    hours, remainder = divmod(seconds_elapsed, 3600)
    minutes, remainder = divmod(remainder, 60)
    seconds, milliseconds = divmod(remainder, 1)
    milliseconds, microseconds = divmod(milliseconds * 1e3, 1)
    microseconds, nanoseconds = divmod(microseconds * 1e3, 1)

    # Format the time as HH:MM:SS.mmmuuuunnn
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}.{int(milliseconds):03}{int(microseconds):03}{int(nanoseconds):03}"
"""
