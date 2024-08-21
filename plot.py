import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import sys
import os

def load_data(file_path):
    with fits.open(file_path) as hdul:
        data = hdul['SUBINT'].data['DATA']
    print("Original data shape:", data.shape)
    
    data = np.squeeze(data)  # Remove single-dimensional entries from the shape
    
    if data.ndim == 3:
        freq_phase = np.mean(data, axis=0)  # Average over the polarization dimension
    elif data.ndim == 2:
        freq_phase = data
    else:
        raise ValueError(f"Unexpected data shape after squeeze: {data.shape}")

    print("Reshaped data shape:", freq_phase.shape)
    
    # Compute mean and standard deviation for normalization
    data_mean = np.mean(freq_phase)
    data_std = np.std(freq_phase)
    
    # Normalize the data using z-score normalization
    freq_phase = (freq_phase - data_mean) / data_std
    normalized_min, normalized_max = np.min(freq_phase), np.max(freq_phase)
    print(f"Normalized Data Range: Min = {normalized_min} , Max = {normalized_max} , Mean = {np.mean(freq_phase)}")
    
    return freq_phase

def plot_data(freq_phase, output_file):
    fig = plt.figure(figsize=(12, 12))
    grid = plt.GridSpec(5, 5, hspace=0.0, wspace=0.0)
    
    main_ax = fig.add_subplot(grid[1:, :-1])
    num_phases = freq_phase.shape[1]  # Phase corresponds to the second dimension
    num_channels = freq_phase.shape[0]  # Frequency corresponds to the first dimension
    
    phase = np.linspace(0, 1, num_phases)
    
    # Main plot
    cax = main_ax.imshow(freq_phase, aspect='auto', origin='lower', cmap='inferno',
                         extent=[0, 1, 0, num_channels])
    main_ax.set_xlabel('Pulse Phase')
    main_ax.set_ylabel('Frequency (Channel)')
    
    # Colorbar
    cbar_ax = fig.add_axes([0.08, 0.2, 0.05, 0.455555])
    cbar = plt.colorbar(cax, cax=cbar_ax)
    cbar.set_label('Intensity')
    cbar.ax.yaxis.set_label_position('left')
    cbar.ax.yaxis.set_ticks_position('left')
    
    # Top plot (Flux Density)
    top_ax = fig.add_subplot(grid[0, :-1])
    flux_phase = np.mean(freq_phase, axis=0)  # Average over frequency dimension
    top_ax.plot(phase, flux_phase)
    top_ax.set_ylabel('Flux Density')
    top_ax.set_xlabel('Pulse Phase')
    top_ax.set_ylim([-0.5, 5])  # Set the y-axis limit for the top plot
    top_ax.set_xlim([0, 1])
    top_ax.xaxis.set_visible(False)
    
    # Right plot (Frequency Strength)
    right_ax = fig.add_subplot(grid[1:, -1])
    freq_strength = np.mean(freq_phase, axis=1)  # Average over phase dimension
    right_ax.plot(freq_strength, np.arange(num_channels))
    right_ax.set_xlabel('Power')
    right_ax.set_ylabel('Frequency (Channel)')
    right_ax.set_xlim([-1, 1])
    top_ax.yaxis.set_visible(False)
    right_ax.set_xticks([-0.5, 0, 0.5, 1])
    right_ax.set_xticklabels(['-0.5', '0', '0.5', '1']) 
    
    plt.subplots_adjust(left=0.2, right=0.8, top=0.8, bottom=0.2)
    plt.show()
    fig.savefig(output_file)
    print("Figure saved as ", output_file)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)
    
    file_path = sys.argv[1]
    freq_phase = load_data(file_path)
    output_file = os.path.splitext(file_path)[0] + ".png"
    plot_data(freq_phase, output_file)

