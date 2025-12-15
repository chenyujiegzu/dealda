# !/bin/bash

# Specify the directory containing the FITS files
data_dir="/home/data/C1"
name="c1"
thread="1"
parfile="J2338+4818_tdb.par"
nchan="1024:D"
npol="4"
nbin="128"
nsub="20"
parallel="12"

# Initialize files to store commands
dspsr_commands="dspsr.txt"

# Clear previous command files
> "$dspsr_commands"
> dspsr.log

# Initialize an array to store dates
dates=()

# Loop through all date directories
for date in $(ls $data_dir | grep '^[0-9]\{8\}$'); do
    
    # Run the rfifind command
    echo dspsr -cont -t "${thread}" -E "${parfile}" -F "${nchan}" -b "${nbin}" -K -L "${nsub}" -A -d "${npol}" -O "${name}_${date}" "$data_dir/$date/*.fits" >> "$dspsr_commands"

    # Store the date for later use in prepdata command
    dates+=("$date")
done

# Wait for all background processes to complete 
wait                                                                                                                                                                                          echo "The dspsr.txt have generated." 

# cat the -K with 20231006
#echo "Removing -K option and change npol to 2 for the dspsr command for date 20231006..."
#sed -i '/20231006/s/ -K//g' dspsr.txt
#sed -i '/20231006/s/ -d [0-9]\+/ -d 2/' dspsr.txt

# Run rfifind commands in parallel
echo "Running dspsr commands in parallel..."
cat "$dspsr_commands" | parallel -j "${parallel}" | tee -a dspsr.log

# Wait for all background processes to complete
wait

echo "All dspsr commands have completed."

