from functions import receive, MAX_UDP_PACKET_SIZE, set_up_plot, plotter
import numpy as np

LAPTOP_IP = "192.168.0.234"
RPI_IP = "192.168.0.235"
PORT = 6371

def receiver_main():
    UDP = receive(LAPTOP_IP, PORT)
    UDP.eth0()
    print('Everything Initialized...')

    fig, line = set_up_plot()

    try:
        while True:
            data = UDP.set_up()
            if data:
                spectrum = np.frombuffer(data, dtype=np.float64)
                plotter(spectrum, fig, line)

    except KeyboardInterrupt:
        UDP.stop()
        print('UDP Stopped...')
    finally:
        print('Done.')

if __name__ == "__main__":
    # receiving script (not sending)
    receiver_main()

