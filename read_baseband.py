import numpy as np
import mmap
import matplotlib.pyplot as plt
import sys

# Set file path and parameters
file = 'test.dat'
onek = 1024
nchan = 4 * onek
nsample = 1000

# Open the file and map it into memory
with open(file, 'r+b') as f:
    fmap = mmap.mmap(f.fileno(), 0)

# Compute parameters
delta_t = 1.0 / 1.6 * 1.0e-9  # Time resolution (1/1.6 ns)
bw = 1.0 / (2 * np.pi * delta_t)
bw *= 4
ch_bw = bw / nchan
freq = np.arange(nchan) * ch_bw / 1.0e6

# Initialize the average spectrum array
avspec = np.zeros(nchan)

# Compute the average spectrum over all samples
for ispec in range(nsample):
    # Read data from memory map
    start_idx = ispec * 2 * nchan
    end_idx = start_idx + 2 * nchan
    tseries = np.frombuffer(fmap[start_idx:end_idx], dtype=np.int8)

    # Compute the FFT of the time series
    subtseries = tseries
    tempspec = np.fft.fft(subtseries)
    avspec += np.abs(tempspec[:nchan]) * 1.0 / nsample

# Close the memory map
fmap.close()

# Plot the average spectrum
plt.plot(freq, avspec)
plt.yscale('log')
plt.xlabel('Frequency (MHz)')
plt.ylabel('Amplitude')
plt.title('Average Spectrum')
plt.show()
