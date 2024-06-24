import socket
import numpy as np
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--host', '-H', default='localhost')
parser.add_argument('--port', '-P', type=int, default=65432)
args = parser.parse_args()

num_samples = 2048
sample_rate = 3.2e6
center_freq = 125.2e6
freqs = np.fft.fftshift(np.fft.fftfreq(num_samples, 1/sample_rate) + center_freq)

def receive_data(conn):
    data = b''
    while True:
        packet = conn.recv(4096)
        if not packet:
            break
        data += packet
    return np.frombuffer(data, dtype=np.float32).reshape(-1, 2)

def perform_power(signal):
    return np.abs(signal)**2

def shift(signal):
    return np.fft.fftshift(signal)

def correlate(data):
    d = data[..., 0] + 1j * data[..., 1]
    pwr = shift(np.mean(perform_power(np.fft.fft(d)), axis=0))
    return pwr

def set_up_plot():
    plt.style.use('bmh')
    plt.ion()
    fig = plt.figure(figsize=(12, 6))
    line, = plt.semilogy(freqs/1e6, np.ones_like(freqs), linewidth=0.8, label='Signal Data')
    plt.xlabel('Frequency [MHz]', fontsize=16)
    plt.ylabel('Power [arbitrary]', fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.gca().ticklabel_format(axis='x', style='plain')
    plt.tight_layout()
    plt.grid(color='dimgray')
    plt.legend(loc='best')
    plt.ylim(1e2, 1e9)
    return fig, line

def plotter(pwr, fig, line):
    line.set_ydata(pwr)
    fig.canvas.draw()
    fig.canvas.flush_events()

# Set up socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((args.host, args.port))
    print(f'Connected to server at {args.host}:{args.port}')
    data = receive_data(s)
    pwr = correlate(data)
    fig, line = set_up_plot()
    plotter(pwr, fig, line)
