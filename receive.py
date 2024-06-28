import functions
from functions import receive, run_vis, sdr, prefix, folder


LAPTOP_IP = "192.168.0.234"
RPI_IP = "192.168.0.235"
PORT = 6371

def capture_data(size):
    # send a bunch of zeros for now, replace with actual data later
    return [0] * size

def receiver_main():
    UDP = receive(LAPTOP_IP, PORT)
    UDP.eth0()
    print('Everything Initialized...')
    try:
        while True:
            UDP.set_up()
    except KeyboardInterrupt:
        UDP.stop()
        print('UDP Stopped...')
    finally:
        print('Done.')

if __name__ == "__main__":
    # receiving script (not sending)
    receiver_main()

functions.run_vis(sdr, prefix, folder)