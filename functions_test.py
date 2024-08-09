import numpy as np
import socket
import matplotlib.pyplot as plt
import scipy.signal
import os

num_samples = 2048
sample_rate = 3.2e6
center_freq = 145.2e6
freqs = np.fft.fftshift(np.fft.fftfreq(num_samples, 1/sample_rate) + center_freq)

class send:
    def __init__(self, host, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.connect((host, port))

    def send_data(self, data):
        data = np.array(data, dtype=np.uint8).tobytes()
        self.s.sendall(data)

    def close(self):
        self.s.close()

class receive:
    def __init__(self, host, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(('', port))

    def set_up(self):
        try:
            data, _ = self.s.recvfrom(2 * num_samples)
            return data
        except socket.timeout:
            return None

    def close(self):
        self.s.close()

def writeto(data, prefix, folder, track_files):
    filepath = os.path.join(folder, f'{prefix}_{track_files}.npz')
    np.savez(filepath, data=data)

def perform_power(signal):
    return np.abs(signal) ** 2

def shift(signal):
    return np.fft.fftshift(signal)

def correlate_signals(signal1, signal2):
    return scipy.signal.correlate(signal1, signal2, mode='full')

def initialize_plots(ip_addresses):
    plt.style.use('bmh')
    plt.ion()
    num_plots = len(ip_addresses) + 1
    fig, axs = plt.subplots(num_plots, 1, figsize=(12, 6 * num_plots), sharex=True)
    if num_plots == 1:
        axs = [axs]

    lines = []
    for ax, ip in zip(axs[:-1], ip_addresses):
        line, = ax.semilogy(freqs / 1e6, np.ones_like(freqs), label=f'Signal Data {ip}')
        lines.append(line)
        ax.set_title(f'Signal Data from {ip}')
        ax.set_xlabel('Frequency [MHz]')
        ax.set_ylabel('Power [arbitrary]')
        ax.grid()
        ax.legend()
        ax.set_ylim(1e4, 1e11)

    axs[-1].set_title('Correlated Signal Plot')
    axs[-1].set_xlabel('Frequency [MHz]')
    axs[-1].set_ylabel('Time [s]')
    
    plt.tight_layout()
    return fig, axs, lines

def update_plot(data, fig, line):
    d = data[..., 0] + 1j * data[..., 1]
    pwr = shift(perform_power(np.fft.fft(d)))
    line.set_ydata(pwr)
    fig.canvas.draw()
    fig.canvas.flush_events()

def correlate_and_plot(signal1, signal2, fig, axs):
    correlation = correlate_signals(signal1, signal2)
    num_bins = len(freqs)
    time_axis = np.arange(len(correlation))
    freq_axis = np.linspace(-num_bins/2, num_bins/2, num_bins) / 1e6

    corr_reshaped = np.reshape(correlation, (num_bins, -1))
    ax_corr = axs[-1]
    ax_corr.clear()
    cax = ax_corr.imshow(corr_reshaped, aspect='auto', cmap='inferno', origin='lower',
                         extent=[freq_axis.min(), freq_axis.max(), time_axis.min(), time_axis.max()])
    fig.colorbar(cax, ax=ax_corr, orientation='vertical', label='Correlation')
    plt.draw()
    plt.pause(0.1)
