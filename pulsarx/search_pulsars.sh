#!/bin/bash
# @Yujie Chen, gs.yujiechen23@gzu.edu.cn, 2025/12/15
# PulsarX + presto search pulsars with parallel

# Data path
data_dir="/home/data/NGC6517"
fits_pattern="NGC6517_tracking-M01_{0001..0800}.fits"

# PulsarX dedispersion
td="1"
fd="2"
zapthre="3"
dms="182"
ddm="0.1"
ndm="2"
dedisp_thread="4"
zmax="20"
numharm="32"
wmax="20"  # wmax: an integer multiple of 20, such as 20, 40, 60.
Z_RFI="kadaneF 8 4 zdot"
dedisp_format="presto"  # pulsarx, sigproc, presto
Jname="J1801-0857"
srcname="J1801-0857"
RA="18:01:50.52"
DEC="-08:57:31.60"
fold_thread="4"
clfd="2"
nsubband="64"
nbin="128"
thread="4"

# template and sift path
template="/home/software/PulsarX/include/template/fast_fold.template"
sift_script="/mnt/f/data/pulsarX/ACCEL_sift_pulsarx.py"
ACCEL_value=$(( ((zmax + 19) / 20) * 20 ))
JERK_value=$(( ((wmax + 19) / 20) * 20 ))
cand="*ACCEL_${zmax}_JERK_${JERK_value}"
candfile="./cands.txt"

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

echo dedisperse_all_fil --cont --td "${td}" --fd "${fd}" --zapthre "${zapthre}" --dms "${dms}" --ddm "${ddm}" --ndm "${ndm}" -t "${dedisp_thread}" -z "${Z_RFI}" --rootname "${Jname}" --format "${dedisp_format}" --psrfits -f "${data_dir}/${fits_pattern}" >> "$dedisp_commands"

echo "Running dedisperse_all_fil..."
cat "$dedisp_commands" | parallel -j "${thread}" | tee -a dedisperse.log

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
    echo accelsearch -zmax "${zmax}" -numharm "${numharm}" -wmax "${wmax}" "$fftfile" >> "$accel_commands"
done

echo "Running accelsearch in parallel..."
cat "$accel_commands" | parallel -j "${thread}" | tee -a accelsearch.log

wait
echo "accelsearch finished."

########################
# Step 4: ACCEL sift (PulsarX)
########################

echo "Running PulsarX ACCEL sift..."
python "${sift_script}" --cand "${cand}" | tee -a sift.log

wait
echo "Candidate sifting finished."

########################
# Step 5: psrfold_fil2 (PulsarX)
########################

echo "Generating psrfold_fil2 commands..."

echo psrfold_fil2 -t "${fold_thread}" --srcname "${srcname}" --ra "${RA}" --dec "${DEC}" --template "${template}" --nsubband "${nsubband}" --nbin "${nbin}" --clfd "${clfd}" --zapthre "${zapthre}" -z "${Z_RFI}" --candfile "${candfile}" --presto --psrfits "${data_dir}/${fits_pattern}" >> "$fold_commands"

echo "Running psrfold_fil2..."
cat "$fold_commands" | parallel -j "${thread}" | tee -a psrfold.log

wait
echo "psrfold finished."

echo "All commands completed."
