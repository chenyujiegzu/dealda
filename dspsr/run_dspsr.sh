# !/bin/bash

#@Yujie Chen, gs.yujiechen23@gzu.edu.cn, 2025/12/15

# Specify the directory containing the FITS files
data_dir="/home/data/C1"
dates=("20241222" "20250220")
fits_pattern="NGC6517_tracking-M01_*.fits"

PSRname="c1"
thread="1"
parfile="J2338+4818_tdb.par"
nchan="1024:D"
npol="4"
nbin="128"
nsub="20"
parallel="2"

# Initialize files to store commands
dspsr_commands="dspsr.txt"

# Clear previous command files
> "$dspsr_commands"
> dspsr.log

# Loop through all date directories
for day in "${dates[@]}"; do
    echo dspsr -cont -t "${thread}" -E "${parfile}" -F "${nchan}" -b "${nbin}" -K -L "${nsub}" -A -d "${npol}" -O "${PSRname}_${date}" "${data_dir}/${day}/${fits_pattern}" >> "$dspsr_commands"
done

# Wait for all background processes to complete 
wait                                                                                                                                                                                          echo "The dspsr.txt have generated." 

# Run rfifind commands in parallel
echo "Running dspsr commands in parallel..."
cat "$dspsr_commands" | parallel -j "${parallel}" | tee -a dspsr.log

# Wait for all background processes to complete
wait

echo "All dspsr commands have completed."

