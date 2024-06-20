import numpy
import ugradio

def test_sdr_device():
    device_index = 0
    sdr = None
    while sdr is None and device_index < 10:
        try:
            sdr = ugradio.sdr.SDR(sample_rate=3.2e6, center_freq=145.2e6, direct=False, device_index=device_index)
            print(f"Successfully opened SDR with device index {device_index}!")
        except Exception as e:
            print(f"Could not open SDR with device index {device_index}: {e}... ya done fucked up!")
            device_index += 1

    if sdr is None:
        raise RuntimeError("Could not open any SDR device")
    else:
        # Try reading some data
        try:
            data = sdr.capture_data()
            print("Reading data from SDR successfully!")
        except Exception as e:
            print(f"Error reading data from SDR: {e}... ya done fucked up!")

test_sdr_device()



