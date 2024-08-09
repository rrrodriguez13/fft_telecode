import numpy as np
import socket
import matplotlib.pyplot as plt
import scipy as sci
import scipy.signal
import os

num_samples = 2048
sample_rate = 3.2e6
center_freq = 145.2e6
freqs = np.fft.fftshift(np.fft.fftfreq(num_samples, 1/sample_rate) + center_freq)

class send:
    def __init__(self, HOST, PORT):
        self.HOST = HOST
        self.PORT = PORT
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def stop(self):
        self.s.close()
    
    def eth0(self):
        self.s.connect((self.HOST, self.PORT))
        print(f'Starting sender on {self.HOST}:{self.PORT}')
        
    def send_data(self, data):
        data = np.array(data, dtype=np.uint8).ravel().tobytes()
        self.s.sendto(data, (self.HOST, self.PORT))
        print(f'Sent data of size {len(data)} bytes')

class receive:
    def __init__(self, HOST, PORT):
        self.HOST = HOST
        self.PORT = PORT
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.settimeout(5)
        
    def eth0(self):
        self.s.bind(('', self.PORT))
        print(f'Listening on port {self.PORT} ...')
    
    def set_up(self):
        try:
            data, addr = self.s.recvfrom(2*num_samples)
            print(f'Received data of size {len(data)} bytes from {addr}')
            return data
        except socket.timeout:
            print('No data received, waiting for next packet ...')
        
    def stop(self):
        self.s.close()

def initialize_plots(ip_addresses):
    plt.style.use('bmh')
    plt.ion()
    num_plots = len(ip_addresses) + 1
    fig, axs = plt.subplots(num_plots, 1, figsize=(12, 6 * num_plots), sharex=True)
    if num_plots == 1:
        axs = [axs]

    lines = []
    for ax, ip in zip(axs[:-1], ip_addresses):
        line, = ax.semilogy(freqs / 1e6, np.ones_like(freqs), linewidth=0.8, label=f'Signal Data {ip}')
        lines.append(line)
        ax.set_title(f'Signal Data from {ip}')
        ax.set_xlabel('Frequency [MHz]')
        ax.set_ylabel('Power [arbitrary]')
        ax.grid(color='dimgray')
        ax.legend(loc='best')
        ax.set_ylim(1e4, 1e11)
    
    ax_corr = axs[-1]
    ax_corr.set_title('Correlated Signal Plot')
    ax_corr.set_xlabel('Frequency [MHz]')
    ax_corr.set_ylabel('Time [s]')
    
    plt.tight_layout()
    return fig, axs, lines

def update_plot(data, fig, line):
    d = data[..., 0] + 1j * data[..., 1]
    pwr = np.abs(np.fft.fftshift(np.fft.fft(d))) ** 2

    line.set_ydata(pwr)
    fig.canvas.draw()
    fig.canvas.flush_events()

def correlate_and_plot(signal1, signal2, fig, axs):
    correlation = sci.signal.correlate(signal1, signal2, mode='full')
    num_points = len(correlation)
    num_bins = len(freqs)
    time_axis = np.arange(num_points)
    freq_axis = np.linspace(-num_bins/2, num_bins/2, num_bins) / 1e6

    corr_reshaped = np.reshape(correlation, (num_bins, num_points // num_bins))
    ax_corr = axs[-1]
    ax_corr.clear()
    cax = ax_corr.imshow(corr_reshaped, aspect='auto', cmap='inferno', origin='lower',
                         extent=[freq_axis.min(), freq_axis.max(), time_axis.min(), time_axis.max()])
    ax_corr.set_title('Correlated Signal Plot')
    ax_corr.set_xlabel('Frequency [MHz]')
    ax_corr.set_ylabel('Time [s]')
    fig.colorbar(cax, ax=ax_corr, orientation='vertical', label='Correlation')
    plt.draw()
    plt.pause(0.1)

