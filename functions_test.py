import numpy as np
import socket
import matplotlib.pyplot as plt
from scipy import signal
import os

num_samples = 2048
sample_rate = 2.2e6
center_freq = 145.2e6
freqs = np.fft.fftshift(np.fft.fftfreq(num_samples, 1/sample_rate) + center_freq)

# Networking classes
class send:
    def __init__(self, HOST, PORT):
        self.HOST = HOST
        self.PORT = PORT
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def stop(self):
        self.s.close()
    
    def eth0(self):
        self.s.connect((self.HOST, self.PORT))
        print('eth0 starting...')
        print(f'Yelling on port {self.HOST}')
        
    def send_data(self, data):
        data = np.array(data, dtype=np.int8)
        data = np.ravel(data).tobytes()  # Flatten data and ensure data is bytes
        chunks = [data]  # sends all data in chunks
        for i, chunk in enumerate(chunks):
            self.s.sendto(chunk, (self.HOST, self.PORT))
            print(f'Sent chunk {i+1}/{len(chunks)} of size {len(chunk)}')

class receive:
    def __init__(self, HOST, PORT):
        self.HOST = HOST
        self.PORT = PORT
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.settimeout(5)
        
    def eth0(self):
        # Bind to all interfaces
        self.s.bind(('', self.PORT))
        print(f'Listening on port {self.PORT} ...')
    
    def set_up(self):
        try:
            print('Searching for data ...')
            data, addr = self.s.recvfrom(2*num_samples)
            print('Received data!\n')
            return data
        except socket.timeout:
            print('No data received, waiting for next packet ...')
            print("\n")
        
    def stop(self):
        self.s.close()

def writeto(data, prefix, folder, track_files):
    filepath = os.path.join(folder, f'{prefix}_{track_files}.npz')
    np.savez(filepath, data=data) # uncomment to save files into output folder

def perform_power(signal):
    return np.abs(signal)**2
    
def shift(signal):
    return np.fft.fftshift(signal)

def correlate_signals(signal1, signal2):
    correlation = signal.correlate(signal1/np.std(signal1), signal2/np.std(signal2), mode='full') / min(len(signal1), len(signal2))
    return correlation
    
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
    d = data[..., 0] + 1j * data[..., 1]
    pwr = shift(perform_power(np.fft.fft(d)))

    # plots new data and flushes previous data
    line.set_ydata(pwr)
    fig.canvas.draw()
    fig.canvas.flush_events()

def correlate_and_plot(signal1, signal2, fig, axs):
    # Ensure signals are the same length
    if len(signal1) != len(signal2):
        min_len = min(len(signal1), len(signal2))
        signal1 = signal1[:min_len]
        signal2 = signal2[:min_len]
    
    # Compute correlation
    correlation = correlate_signals(signal1, signal2)

    # Generate time lags for the x-axis
    lags = np.arange(-len(signal1) + 1, len(signal1))
    
    # Access the correlation subplot
    ax_corr = axs[-1]
    
    # Clear the correlation plot before plotting
    ax_corr.clear()
    
    # Plot the correlation
    ax_corr.plot(lags, correlation, linewidth=0.8, label='Correlated Signal', color='green')
    ax_corr.set_title('Correlation of Signals')
    ax_corr.set_xlabel('Time Lag')
    ax_corr.set_ylabel('Amplitude [arbitrary]')
    ax_corr.grid(True)
    
    # Optionally set y-axis limits if needed
    # ax_corr.set_ylim(-50, 300)
    
    # Refresh the plot
    fig.canvas.draw()
    fig.canvas.flush_events()



