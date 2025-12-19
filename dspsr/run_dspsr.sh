# !/bin/bash

#@Yujie Chen, gs.yujiechen23@gzu.edu.cn, 2025/12/15

# Specify the directory containing the FITS files
data_dir="/home/data/C1"
dates=("20241222" "20250220")
fits_pattern="NGC6517_tracking-M01_*.fits"
minX_MB="1024"
PSRname="c1"
thread="1"
parfile="J2338+4818_tdb.par"
nchan="1024:D"
npol="4"
nbin="128"
nsub="20"
parallel="2"
dspsr_commands="dspsr.txt"

> "$dspsr_commands"
> dspsr.log

# Loop through all date directories
for day in "${dates[@]}"; do
    echo dspsr -cont -U "${minX_MB}" -t "${thread}" -E "${parfile}" -F "${nchan}" -b "${nbin}" -K -L "${nsub}" -A -d "${npol}" -O "${PSRname}_${day}" "${data_dir}/${day}/${fits_pattern}" >> "$dspsr_commands"
done                                                                                                                                                                                       echo "The dspsr.txt have generated." 

# Run rfifind commands in parallel
echo "Running dspsr commands in parallel..."
cat "$dspsr_commands" | parallel -j "${parallel}" | tee -a dspsr.log

echo "All dspsr commands have completed."

