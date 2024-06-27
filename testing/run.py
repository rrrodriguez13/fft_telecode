import time
from udp_script import send, receive, MAX_UDP_PACKET_SIZE

LAPTOP_IP = "192.168.0.234"
RPI_IP = "192.168.0.235"
PORT = 6371

def capture_data(size):
    # send a bunch of zeros for now, replace with actual data later
    return [0] * size

# going on the pi
def sender_main():
    UDP = send(LAPTOP_IP, PORT)
    #UDP.eth0()
    print('Everything initialized...')
    try:
        print('Starting loop...')
        while True:
            data = capture_data(3*MAX_UDP_PACKET_SIZE)
            UDP.send_data(data)
            time.sleep(1)
            print("Sent data!")
    except KeyboardInterrupt:
        UDP.stop()
        print('UDP Stopped...')
    finally:
        print('Done.')

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
    # Uncomment the appropriate function depending on whether you want to send or receive data
    #sender_main()
    receiver_main()
