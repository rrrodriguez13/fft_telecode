import numpy as np
import socket
import matplotlib.pyplot as plt
import os

num_samples = 2048
sample_rate = 3.2e6
center_freq = 125.2e6
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
        print('eth0 starting...')
        print(f'Yelling on port {self.HOST}')
        
    
    def send_data(self, data):
        data = np.array(data, dtype=np.uint8).tobytes()  # Ensures data is bytes
        chunks = [data[i:i + num_samples] for i in range(0, len(data), num_samples)]
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
        self.s.bind((self.HOST, self.PORT))
        #self.s.listen()
        #self.conn, addr = self.s.accept()
        print(f'Listening on port {self.PORT} ...')
    
    def set_up(self):
        try:
            print('Waiting to receive data ...')
            data, addr = self.s.recvfrom(num_samples)
            #print(f'Received data: {len(data)} bytes from {addr}')
            print('Received data!\n')
        except socket.timeout:
            print('No data received, waiting for next packet ...')
            print("\n")
    
    def stop(self):
        self.s.close()


def run_vis(sdr, prefix, folder):
    data = []
    track_files = 0  # number of files saved
    fig, line = set_up_plot()
    try:
        while True:
            d = sdr.capture_data() # reads data, can change nsamples and nblocks if necessary
            data.append(d) # appends data to d
            
            if len(data) > 10:
                track_files += 1
                writeto(data, prefix, folder, track_files)
                plotter(data[-1], fig, line, folder, prefix, track_files) # Pass the last batch of data to the plotter
                print(f'file number {track_files} has been written successfully!')
                data = []
    except KeyboardInterrupt:
        print("Stopping!")
        sdr.close()
        return

# writes new npz file every 100 data points pulled with prefix argument
def writeto(data, prefix, folder, track_files):
    filepath = os.path.join(folder, f'{prefix}_{track_files}.npz')
    np.savez(filepath, data=data)

# power spectra (absolute value squared)
def perform_power(signal):
    return np.abs(signal)**2
    
# fft shifts data
def shift(signal):
    return np.fft.fftshift(signal)
    
def set_up_plot():
	plt.style.use('bmh')
	plt.ion()
	fig = plt.figure(figsize=(12, 6))
	line, = plt.semilogy(freqs/1e6, np.ones_like(freqs), linewidth=0.8, label='Signal Data')
	plt.xlabel('Frequency [MHz]', fontsize=16) # x-axis label
	plt.ylabel('Power [arbitrary]', fontsize=16) # y-axis label
	plt.xticks(fontsize=14)
	plt.yticks(fontsize=14)
	plt.gca().ticklabel_format(axis='x', style='plain') # removes the 1e6 on the x-axis
	plt.tight_layout()
	plt.grid(color='dimgray')
	plt.legend(loc='best')
	plt.ylim(1e2, 1e9)
	return fig, line 

def plotter(data, fig, line, folder, prefix, track_files):
    d = data[..., 0] + 1j * data[..., 1]
    pwr = shift(np.mean(perform_power(np.fft.fft(d)), axis=0))
    
    title = f'{prefix}_{track_files}'

    # plots the data
    line.set_ydata(pwr)
    #plt.semilogy(freqs/1e6, pwr, linewidth=0.8, label='Signal Data') # plots power spectra
    plt.title(f'{title} Power Spectrum', fontsize=18, fontweight='bold') # sets title of subplot to filename
    fig.canvas.draw()
    fig.canvas.flush_events()
    #plt.savefig(os.path.join(folder, f'{title}.png')) # saves plot



