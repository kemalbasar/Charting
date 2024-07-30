import numpy as np
from matplotlib import pyplot as plt

# Define the parameters for the pulse graph
period = 1.15  # seconds
period2 = 1  # seconds
num_peaks = 20  # number of peaks
num_peaks2 = 22  # number of peaks
time = np.linspace(0, period * num_peaks, num_peaks * 1000)  # time array
time2 = np.linspace(0, period2 * num_peaks2, num_peaks2 * 1000)  # time array
# Generate the pulse signal
pulse_signal = (np.sin(2 * np.pi * time / period) > 0).astype(float)
pulse_signal2 = (np.sin(2 * np.pi * time2 / period2) > 0).astype(float)

# Plot the pulse graph
plt.figure(figsize=(10, 6))
plt.plot(time, pulse_signal)
plt.plot(time2, pulse_signal2)
plt.title('Pulse Signal with 1.15 Seconds Period and 20 Peaks')
plt.xlabel('Time (seconds)')
plt.ylabel('Amplitude')
plt.grid(True)
plt.show()