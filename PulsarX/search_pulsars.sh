#!/bin/bash
# @Yujie Chen, gs.yujiechen23@gzu.edu.cn, 2025/12/15
# PulsarX + presto search pulsars with parallel

# Data path
data_dir="/home/data/NGC6517"
fits_pattern="NGC6517_tracking-M01_{0001..0800}.fits"

# PulsarX dedispersion
dms="180"
ddm="0.01"
ndm="1000"
dedisp_thread="4"
zmax_value="20"
numharm_value="32"
wmax_value="8"

# fold paramters
fold_thread="4"
n_value="64"
npart_value="128"
thread="24"

# template and sift path
template="/home/software/PulsarX/include/template/fast_fold.template"
sift_script="/home/software/PulsarX/python/pulsarx/ACCEL_sift_pulsarx.py"

# output commands files
dedisp_commands="dedisperse.txt"
realfft_commands="realfft.txt"
accel_commands="accelsearch.txt"
fold_commands="psrfold.txt"

# logfiles
> "$dedisp_commands"
> "$realfft_commands"
> "$accel_commands"
> "$fold_commands"

> dedisperse.log
> realfft.log
> accelsearch.log
> sift.log
> psrfold.log

##############################
# Step 1: dedisperse (PulsarX)
##############################

echo "Generating dedisperse_all_fil commands..."

echo dedisperse_all_fil --dms "${dms}" --ddm "${ddm}" --ndm "${ndm}" -t "${dedisp_thread}" -z kadaneF 8 4 zdot --format presto --psrfits -f "${data_dir}/${fits_pattern}" >> "$dedisp_commands"

echo "Running dedisperse_all_fil..."
cat "$dedisp_commands" | tee -a dedisperse.log

wait
echo "Dedispersion finished."

########################
# Step 2: realfft (presto)
########################

echo "Generating realfft commands..."

ls *.dat | while read datfile; do
    echo realfft "$datfile" >> "$realfft_commands"
done

echo "Running realfft in parallel..."
cat "$realfft_commands" | parallel -j "${thread}" | tee -a realfft.log

wait
echo "realfft finished."

########################
# Step 3: accelsearch (presto)
########################

echo "Generating accelsearch commands..."

ls *.fft | while read fftfile; do
    echo accelsearch -zmax "${zmax_value}" -numharm "${numharm_value}" -wmax "${wmax_value}" "$fftfile" >> "$accel_commands"
done

echo "Running accelsearch in parallel..."
cat "$accel_commands" | parallel -j "${thread}" | tee -a accelsearch.log

wait
echo "accelsearch finished."

########################
# Step 4: ACCEL sift (PulsarX)
########################

echo "Running PulsarX ACCEL sift..."
python "${sift_script}" | tee -a sift.log

wait
echo "Candidate sifting finished."

########################
# Step 5: psrfold_fil2 (PulsarX)
########################

echo "Generating psrfold_fil2 commands..."

echo psrfold_fil2 -t "${fold_thread}" --template "${template}" -n "${n_value}" -b "${npart_value}" --clfd 2 --zapthre 3.0 -z kadaneF 8 4 zdot --candfile cands.txt --presto --psrfits "${data_dir}/${fits_pattern}" >> "$fold_commands"

echo "Running psrfold_fil2..."
cat "$fold_commands" | tee -a psrfold.log

wait
echo "psrfold finished."

echo "PulsarX + Presto completed."
