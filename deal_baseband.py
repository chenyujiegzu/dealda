import os
import mmap
import time
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from args_parser import parse_args_deal_baseband

def memory_map_read(filename, access=mmap.ACCESS_READ):
    size = os.path.getsize(filename)
    with open(filename, 'r') as f:
        fd = os.open(filename, os.O_RDONLY)
        return mmap.mmap(fd, size, access=access)

def memory_map_write(filename, access=mmap.ACCESS_WRITE):
    size = os.path.getsize(filename)
    with open(filename, 'r+b') as f:
        fd = os.open(filename, os.O_RDWR)
        return mmap.mmap(fd, size, access=access)

def process_chunk(in1, in2, out, chunk_size, start, end):
    out[start:end] = in1[start:end]
    out[start + len(in1):end + len(in2)] = in2[start:end]

def combine_baseband(file1, file2, outfile, num_threads):
    in1 = memory_map_read(file1)
    in2 = memory_map_read(file2)
    
    size = len(in1) * 2
    chunk_size = 64 * 1024  # Adjust as necessary
    block_size = int(size / chunk_size / 2)
    
    # Create output file with correct size
    with open(outfile, 'wb') as f:
        f.seek(size - 1)
        f.write(b'\x00')
    
    out = memory_map_write(outfile)
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for i in tqdm(range(block_size), desc="Processing", unit="blocks"):
            start = i * chunk_size
            end = start + chunk_size
            futures.append(executor.submit(process_chunk, in1, in2, out, chunk_size, start, end))
        
        for future in futures:
            future.result()
    
    in1.close()
    in2.close()
    out.close()

def main():
    args = parse_args_deal_baseband()
    
    start_time = time.time()
    combine_baseband(args.file1, args.file2, args.o, args.t)
    end_time = time.time()
    
    elapsed_time = end_time - start_time
    print(f"Total time taken: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()


