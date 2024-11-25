import numpy as np
import mmap
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
import argparse

# one telescope's spectrum
def compute_single_antennas_spectrum(filename, sample_rate, nchan):
    with open(filename, 'r+b') as f:
        fmap = mmap.mmap(f.fileno(), 0)
        tseries = np.frombuffer(fmap[:2 * nchan], dtype=np.int8).astype(np.float32)
        tseries -= np.mean(tseries)  # remove the DC

        # fft
        tempspec = np.fft.fft(tseries)
        fmap.close()
        
    spectrum = np.abs(tempspec[:nchan // 2]) ** 2
    return spectrum

def main():
    parser = argparse.ArgumentParser(description="Compute and plot spectrum for a single antenna.")
    parser.add_argument('--file', required=True, help="Path to the .dat file from the antenna.")
    args = parser.parse_args()

    # sample rate and channels
    sample_rate = 1000000000  # 1000MSps (1 GHz)
    nchan = 4096

    # file
    filename = args.file

    # spectrum
    spectrum = compute_single_antennas_spectrum(filename, sample_rate, nchan)

    freq_start = 1000  # 1 GHz
    freq_end = 1500    # 1.5 GHz
    freq = np.linspace(freq_start, freq_end, nchan // 2)

    # smoothing
    smooth_spec = gaussian_filter1d(spectrum, sigma=5)

    # ploting
    plt.figure(figsize=(10, 6))
    plt.plot(freq, smooth_spec, label='Smoothed Spectrum', color='blue')
    plt.axvline(x=1420, color='red', linestyle='--', label='21cm Line (1420 MHz)')
    plt.yscale('log')
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Amplitude (Normalized Power Spectrum)')
    plt.title('Smoothed Spectrum of Single Antenna')
    plt.legend()
    plt.grid()

    # saving the png file
    plt.savefig("smoothed_single_antenna_spectrum.png", dpi=1080)
    plt.show()

    np.save("single_antenna_spectrum.npy", spectrum)
    print("Saved single antenna spectrum to single_antenna_spectrum.npy and smoothed_single_antenna_spectrum.png.")

if __name__ == "__main__":
    main()

