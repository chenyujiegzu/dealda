import numpy as np
import mmap
import os
import multiprocessing as mp
import matplotlib.pyplot as plt
import argparse

def memory_map_read(filename, access=mmap.ACCESS_READ):
    size = os.path.getsize(filename)
    fd = os.open(filename, os.O_RDWR)
    return mmap.mmap(fd, size, access=access)

def memory_map_write(filename, access=mmap.ACCESS_WRITE):
    size = os.path.getsize(filename)
    fd = os.open(filename, os.O_RDWR)
    return mmap.mmap(fd, size, access=access)

def process_block(start, end, in1, in2, out, chunk_size):
    for i in range(start, end):
        out[2*i*chunk_size:(2*i+1)*chunk_size] = in1[i*chunk_size:(i+1)*chunk_size]
        out[(2*i+1)*chunk_size:(2*i+2)*chunk_size] = in2[i*chunk_size:(i+1)*chunk_size]

def parallel_memory_map_merge(file1, file2, outfile, num_workers=4):
    in1 = memory_map_read(file1)
    in2 = memory_map_read(file2)

    size = len(in1) * 2
    chunk_size = 4096
    blocksize = size // (chunk_size * 2)

    with open(outfile, 'wb') as f:
        f.seek(size - 1)
        f.write(b'\x00')

    out = memory_map_write(outfile)

    pool = mp.Pool(num_workers)
    block_ranges = [(i * (blocksize // num_workers), (i + 1) * (blocksize // num_workers)) for i in range(num_workers)]
    
    for start, end in block_ranges:
        pool.apply_async(process_block, args=(start, end, in1, in2, out, chunk_size))

    pool.close()
    pool.join()

    in1.close()
    in2.close()
    out.close()

def process_baseband_data(file):
    with open(file, 'r+b') as f:
        fmap = memory_map_read(file)

    onek = 1024
    nchan = 4 * onek
    nsample = 1000

    delta_t = 1.0 / 1.6 * 1.0e-9  # 1/1.6 ns
    bw = 1.0 / (2 * np.pi * delta_t)
    bw = 4 * bw

    ch_bw = bw / nchan
    freq = np.arange(nchan) * ch_bw / 1.0e6

    avspec = np.zeros(nchan)

    for ispec in range(nsample):
        tseries = np.ndarray(2 * nchan, np.int8, fmap[ispec * 2 * nchan:(ispec + 1) * 2 * nchan])
        subtseries = tseries
        tempspec = np.fft.fft(subtseries)
        avspec += np.abs(tempspec[0:nchan]) * 1.0 / nsample

    plt.plot(freq[0:nchan], avspec)
    plt.yscale('log')
    plt.xlabel('MHz')
    plt.show()

def main():
    args = parser.parse_args()

# Merge the baseband data files
parallel_memory_map_merge(file1, file2, outfile)

# Process the merged baseband data
process_baseband_data(outfile)

if __name__ == "__main__":
    main()
