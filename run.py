import time
from udp_script import send, receive

def sender_main():
    UDP = send('10.32.92.216', 2001, '10.32.92.215', 2002, 900e6)
    UDP.eth0()
    UDP.eth1()
    print('Everything initialized...')
    try:
        print('Starting loop...')
        while True:
            UDP.udp0()
            time.sleep(1)
    except KeyboardInterrupt:
        UDP.stop()
        print('UDP Stopped...')
    finally:
        print('done')

def receiver_main():
    UDP = receive('10.32.92.216', 2001)
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
    # sender_main()
    receiver_main()
