import numpy as np
import matplotlib.pyplot as plt

# loading the *.npy file
avspec = np.load('combined_spectrum.npy')

# print and checking
print(f"Shape of the spectrum: {avspec.shape}")
print(f"Spectrum data (first 10 values): {avspec[:10]}")

# plot
plt.plot(avspec)
plt.yscale('log')
plt.xlabel('Frequency Channel')
plt.ylabel('Amplitude')
plt.title('Combined Spectrum')
plt.show()

