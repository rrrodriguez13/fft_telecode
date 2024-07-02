from functions import receive, writeto, set_up_plot, plotter
import numpy as np
import os

# networking
LAPTOP_IP = "192.168.0.234"
RPI_IP = "192.168.0.235"
PORT = 6371

#fig, line = set_up_plot()

def receiver_main():
    UDP = receive(LAPTOP_IP, PORT)
    UDP.eth0()
    print('Everything Initialized ...')

    # defines folder and prefix for saving files
    folder = 'output'
    prefix = 'data'
    track_files = 0 # counter for the number of files saved

    fig, line = set_up_plot()


    if not os.path.exists(folder):
        os.makedirs(folder)

    try:
        while True:
            data = UDP.set_up()
            if data:
                
                spectrum = np.frombuffer(data, dtype=np.uint8)
                spectrum.shape = (-1, 2)
                print("Data shape:", spectrum.shape)
                
                # save the data to a file
                track_files += 1
                #writeto(spectrum, prefix, folder, track_files)

                # plots the data
                plotter(spectrum, fig, line, folder, prefix, track_files) # Pass the last batch of data to the plotter
            
    except KeyboardInterrupt:
        UDP.stop()
        print('UDP stopping...')
    finally:
        print('Done.')
        return

if __name__ == "__main__":
    # receiving script (not sending)
    receiver_main()