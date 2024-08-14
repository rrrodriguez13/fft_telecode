import asyncio
import os
import matplotlib.pyplot as plt
import numpy as np
from functions_test import receive, writeto, initialize_plots, update_plot, correlate_and_plot

# Configuration
IP_ADDRESSES = ["10.10.10.60", "10.10.10.50"]
PORTS = [6373, 6372]  # using different ports for easy identification
DATA_QUEUE_SIZE = 10

data_queues = {ip: asyncio.Queue(maxsize=DATA_QUEUE_SIZE) for ip in IP_ADDRESSES}
plot_queues = {ip: asyncio.Queue(maxsize=DATA_QUEUE_SIZE) for ip in IP_ADDRESSES}

async def data_receiver(ip, port):
    UDP = receive(ip, port)
    UDP.eth0()
    print(f'Listening on {ip}:{port} ...')
    try:
        while True:
            data = await UDP.set_up_async()
            if data:
                await data_queues[ip].put(data)
    except asyncio.CancelledError:
        print(f'Data receiver for {ip} cancelled.')
    finally:
        await UDP.stop_async()
        await data_queues[ip].put(None)  # Signal to stop processing
        print(f'Receiver for {ip} done.')

async def data_processor(ip):
    folder = 'output'
    prefix = 'data'
    track_files = 0  # counter for the number of files saved

    if not os.path.exists(folder):
        os.makedirs(folder)

    try:
        while True:
            data = await data_queues[ip].get()
            if data is None:
                break

            spectrum = np.frombuffer(data, dtype=np.int8)
            spectrum.shape = (-1, 2)
            print(f"Data shape for {ip}: {spectrum.shape}")

            # Save the data to a file
            track_files += 1
            writeto(spectrum, prefix, folder, track_files)

            # Put the data in the plot queue
            await plot_queues[ip].put((spectrum, track_files))
    except asyncio.CancelledError:
        print(f'Data processor for {ip} cancelled.')
    finally:
        await plot_queues[ip].put(None)  # Signal to stop plotting
        print(f'Processor for {ip} done.')

async def plot_data():
    fig, axs, lines = initialize_plots(IP_ADDRESSES)
    last_spectrum = {ip: None for ip in IP_ADDRESSES}
    counters = {ip: 0 for ip in IP_ADDRESSES}  # Initialize counters for each IP

    try:
        while True:
            # Process data from each IP address
            for ip in IP_ADDRESSES:
                if not plot_queues[ip].empty():
                    item = await plot_queues[ip].get()
                    if item is None:
                        continue

                    spectrum, track_files = item
                    try:
                        update_plot(spectrum, fig, lines[IP_ADDRESSES.index(ip)])
                        last_spectrum[ip] = spectrum

                        # Update the counter and plot title
                        counters[ip] += 1
                        axs[IP_ADDRESSES.index(ip)].set_title(f'Signal Data for {ip} [cnt: #{counters[ip]}]')

                    except Exception as e:
                        print(f'Error updating plot for {ip}: {e}')

            # Correlate signals if we have data from both IPs
            if len(IP_ADDRESSES) >= 2:
                ip1, ip2 = IP_ADDRESSES[:2]
                if last_spectrum[ip1] is not None and last_spectrum[ip2] is not None:
                    correlate_and_plot(last_spectrum[ip1], last_spectrum[ip2], fig, axs)

            await asyncio.sleep(0.01)  # Small pause to update the plots in real-time

    except asyncio.CancelledError:
        print('Plotting cancelled.')
    finally:
        print('Plotting done.')

async def main():
    receiver_tasks = [asyncio.create_task(data_receiver(ip, port)) for ip, port in zip(IP_ADDRESSES, PORTS)]
    processor_tasks = [asyncio.create_task(data_processor(ip)) for ip in IP_ADDRESSES]
    plot_task = asyncio.create_task(plot_data())

    await asyncio.gather(*receiver_tasks)
    await asyncio.gather(*processor_tasks)
    plot_task.cancel()  # This will cancel the plotting when all other tasks are done
    await plot_task

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Main thread interrupted.')
