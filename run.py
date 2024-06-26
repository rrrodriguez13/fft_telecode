import time
from udp_script import send, receive, MAX_UDP_PACKET_SIZE

def capture_data(size):
    # send a bunch of zeros for now, replace with actual data later
    return [0] * size

def sender_main():
    UDP = send('192.168.0.123', 2001)
    UDP.eth0()
    print('Everything initialized...')
    try:
        print('Starting loop...')
        while True:
            data = capture_data(3*MAX_UDP_PACKET_SIZE)
            UDP.send_data(data)
            time.sleep(1)
            print("sent data")
    except KeyboardInterrupt:
        UDP.stop()
        print('UDP Stopped...')
    finally:
        print('done')

def receiver_main():
    UDP = receive('192.168.0.234', 2001)
    UDP.eth0()
    print('Everything Initialized...')
    try:
        while True:
            UDP.set_up()
    except KeyboardInterrupt:
        UDP.stop()
        print('UDP Stopped...')
    finally:
        print('done')

if __name__ == "__main__":
    # Uncomment the appropriate function depending on whether you want to send or receive data
    #sender_main()
    receiver_main()
