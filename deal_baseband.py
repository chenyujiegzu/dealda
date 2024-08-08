import multiprocessing as mp
import numpy as np
import mmap
import os
from args_parser import parse_args_deal_baseband
import matplotlib.pyplot as plt

def memory_map_read(filename, access=mmap.ACCESS_READ):
    size = os.path.getsize(filename)
    fd = os.open(filename, os.O_RDONLY)
    return mmap.mmap(fd, size, access=access)

def memory_map_write(filename, access=mmap.ACCESS_WRITE):
    size = os.path.getsize(filename)
    fd = os.open(filename, os.O_RDWR)
    return mmap.mmap(fd, size, access=access)

def process_block(start, end, in1, in2, out, chunk_size):
    for i in range(start, end):
        out[2*i*chunk_size:(2*i+1)*chunk_size] = in1[i*chunk_size:(i+1)*chunk_size]
        out[(2*i+1)*chunk_size:(2*i+2)*chunk_size] = in2[i*chunk_size:(i+1)*chunk_size]

def parallel_memory_map_combine(file1, file2, outfile, parallels=4):
    in1 = memory_map_read(file1)
    in2 = memory_map_read(file2)

    size = len(in1) * 2
    chunk_size = 4096
    blocksize = size // (chunk_size * 2)

    with open(outfile, 'wb') as f:
        f.seek(size - 1)
        f.write(b'\x00')

    out = memory_map_write(outfile)

    pool = mp.Pool(parallels)
    block_ranges = [(i * (blocksize // parallels), (i + 1) * (blocksize // parallels)) for i in range(parallels)]
    
    for start, end in block_ranges:
        pool.apply_async(process_block, args=(start, end, in1, in2, out, chunk_size))

    pool.close()
    pool.join()

    in1.close()
    in2.close()
    out.close()

def process_combined_data(outfile, result_file, plot_file):
    with open(outfile, 'rb') as f:
        fmap = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

    onek = 1024
    nchan = 4 * onek
    nsample = 1000

    delta_t = 1.0 / 1.6 * 1.0e-9
    bw = 1.0 / (2 * np.pi * delta_t)
    bw = 4 * bw

    ch_bw = bw / nchan
    freq = np.arange(nchan) * ch_bw / 1.0e6

    avspec = np.zeros(nchan)

    for ispec in range(nsample):
        tseries = np.ndarray(2 * nchan, np.int8, fmap[ispec * 2 * nchan:(ispec + 1) * 2 * nchan])
        subtseries = tseries
        tempspec = np.fft.fft(subtseries)

        avspec = avspec + np.abs(tempspec[0:nchan]) * 1.0 / nsample

    # Save the frequency spectrum to a text file
    np.savetxt(result_file, np.column_stack((freq, avspec)), header="Frequency (MHz)  Amplitude", comments='')

    # Plot and save the spectrum as an image file
    plt.figure()
    plt.plot(freq[0:nchan], avspec)
    plt.yscale('log')
    plt.xlabel('MHz')
    plt.ylabel('Amplitude')
    plt.title('Frequency Spectrum')
    plt.savefig(plot_file)
    plt.close()

def main():
    args = parse_args_deal_baseband()

    # Combine the baseband data files
    parallel_memory_map_merge(args.file1, args.file2, args.o, parallels=args.t)

    # Process the combined baseband data
    process_combined_data(args.o, 'frequency_spectrum.txt', 'spectrum_plot.png')

if __name__ == "__main__":
    main()

