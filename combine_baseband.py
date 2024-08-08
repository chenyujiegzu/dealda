import numpy as np
import mmap
import os
import multiprocessing as mp

def process_block(start, end, in1, in2, out, blocksize, chunk_size):
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

    # Split the work among multiple processes
    pool = mp.Pool(num_workers)
    block_ranges = [(i * (blocksize // num_workers), (i + 1) * (blocksize // num_workers)) for i in range(num_workers)]
    
    for start, end in block_ranges:
        pool.apply_async(process_block, args=(start, end, in1, in2, out, blocksize, chunk_size))

    pool.close()
    pool.join()

    in1.close()
    in2.close()
    out.close()

file1 = 'bb1/UDP_0001.dat'
file2 = 'bb2/UDP_0001.dat'
outfile = 'combine_bb1_bb2.dat'
parallel_memory_map_merge(file1, file2, outfile)
