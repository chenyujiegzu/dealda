import numpy as np
import mmap
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
import argparse

# combine these signals and caulate
def combine_signals(filenames, sample_rate, nchan):
    n_antennas = len(filenames)
    avspec = np.zeros(nchan // 2)

    # initing the signals
    signals = np.zeros((n_antennas, nchan), dtype=np.float32)

    # deal with all signals
    for i, filename in enumerate(filenames):
        with open(filename, 'r+b') as f:
            fmap = mmap.mmap(f.fileno(), 0)
            tseries = np.frombuffer(fmap[:2 * nchan], dtype=np.int8).astype(np.float32)
            tseries -= np.mean(tseries)

            # fft
            tempspec = np.fft.fft(tseries)
            if tempspec.size >= nchan:
                signals[i, :] = np.abs(tempspec[:nchan]) ** 2 
            else:
                signals[i, :] = np.pad(np.abs(tempspec) ** 2, (0, nchan - tempspec.size), 'constant')

            fmap.close()

    # fringe search
    phase_differences = np.zeros((n_antennas, n_antennas))
    for i in range(n_antennas):
        for j in range(i + 1, n_antennas):
            cross_spectrum = np.fft.fft(signals[i]) * np.conj(np.fft.fft(signals[j]))
            phase_diff = np.angle(cross_spectrum)  # phase difference
            delay_samples = np.argmax(np.abs(np.fft.ifft(phase_diff)))
            delay_seconds = delay_samples / sample_rate
            phase_differences[i, j] = delay_seconds
            phase_differences[j, i] = -delay_seconds

            # print
            print(f" {i} and {j} phase difference: {np.mean(phase_diff):.4f} rad")
            print(f" {i} and {j} delay: {delay_seconds * 1e3:.4f} ms")

    # add the delay and combine signals
    corrected_signals = np.zeros_like(signals)
    for i in range(n_antennas):
        for j in range(n_antennas):
            if i != j:
                delay_samples = int(phase_differences[i, j] * sample_rate)
                corrected_signals[j, :] = np.roll(signals[j, :], delay_samples)

    combined_signal = np.sum(corrected_signals, axis=0)
    # hanning
    combined_signal *= np.hanning(len(combined_signal))

    # spectrum
    tempspec = np.fft.fft(combined_signal)
    avspec += (np.abs(tempspec[:nchan // 2]) ** 2) / len(filenames)

    return avspec, phase_differences

def remove_dc(avspec, freq, dc_freq=1000.0, bandwidth=0.3):
    """remove the DC（1 GHz）"""
    mask = np.logical_or(freq < (dc_freq - bandwidth), freq > (dc_freq + bandwidth))
    avspec[~mask] = 0 
    return avspec

def main():
    parser = argparse.ArgumentParser(description="Process .dat files and compute phase offset for array synthesis.")
    parser.add_argument('--file', nargs='+', required=True, help="Paths to the .dat files from antennas.")
    args = parser.parse_args()

    # sample rate and channels
    sample_rate = 1000000000  # 1000MSps (1 GHz)
    nchan = 4096

    # file
    filenames = args.file

    # combine signals
    avspec, phase_differences = combine_signals(filenames, sample_rate, nchan)

    freq_start = 1.0e3  # 1 GHz
    freq_end = 1.5e3    # 1.5 GHz
    freq = np.linspace(freq_start, freq_end, nchan // 2)

    # remove DC（1 GHz )
    avspec = remove_dc(avspec, freq)

    # smooth the ploting
    smooth_spec = gaussian_filter1d(avspec, sigma=5)

    # ploting
    plt.figure(figsize=(10, 6))
    plt.plot(freq, smooth_spec, label='Smoothed Combined Spectrum', color='blue')
    plt.axvline(x=1420, color='red', linestyle='--', label='21cm Line (1420 MHz)')
    plt.yscale('log')
    plt.xlabel('Frequency (MHz)')
    plt.ylabel('Amplitude (Normalized Power Spectrum)')
    plt.title('Smoothed Combined Amplitude Spectrum')
    plt.legend()
    plt.grid()

    # saving png file
    plt.savefig("smoothed_combined_spectrum.png", dpi=1080)
    plt.show()

    np.save("combined_spectrum.npy", avspec)
    np.save("phase_differences.npy", phase_differences)
    print("Saved combined spectrum to combined_spectrum.npy, smoothed_combined_spectrum.png, and phase_differences.npy.")

if __name__ == "__main__":
    main()

