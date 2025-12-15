# !/bin/bash

# Specify the directory containing the FITS files
data_dir="/home/data/C1"
date=""
name="C1"
time_value="2"
dm_value="35.3"
zmax_value="20"
numharm_value="32"
thread="12"
parfile="J2338+4818_best.par"
n_value="64"
npart_value="128"

# Initialize files to store commands
rfifind_commands="rfifind.txt"
prepdata_commands="prepdata.txt"
prepfold_commands="prepfold.txt"

# Clear previous command files
> "$rfifind_commands"
> "$prepdata_commands"
> "$prepfold_commands"
> rfifind.log
> prepdata.log
> realfft.log
> accelsearch.log
> prepfold.log


# Initialize an array to store dates
dates=()

# Loop through all date directories
if [[ -z "$date" ]]; then
    for date in $(ls $data_dir | grep '^[0-9]\{8\}$'); do
        # Run the rfifind command
        echo rfifind -time "$time_value" -o "${name}_${date}_time${time_value}" "$data_dir/$date/*.fits" >> "$rfifind_commands"
        dates+=("$date")  # Store the date for later use in prepdata command
    done
else
    # Check if the specified date exists
    if [[ -d "$data_dir/$date" ]]; then
        date="$date"
        echo rfifind -time "$time_value" -o "${name}_${date}_time${time_value}" "$data_dir/$date/*.fits" >> "$rfifind_commands"
        dates+=("$date")
    else
        echo "Date $date not found. Continuing with all dates."
        for date in $(ls $data_dir | grep '^[0-9]\{8\}$'); do
            echo rfifind -time "$time_value" -o "${name}_${date}_time${time_value}" "$data_dir/$date/*.fits" >> "$rfifind_commands"
            dates+=("$date")
        done
    fi
fi

# Run rfifind commands in parallel
echo "Running rfifind commands in parallel..."
cat "$rfifind_commands" | parallel -j "${thread}" | tee -a rfifind.log

# Wait for all background processes to complete
wait

echo "All rfifind commands have completed."


# Run prepdata for each date
for date in "${dates[@]}"; do
    echo prepdata -dm "${dm_value}" -nobary -mask "${name}_${date}_time${time_value}_rfifind.mask" -o "${name}_${date}_time${time_value}_dm${dm_value}" "$data_dir/$date/*.fits" >> "$prepdata_commands"
done

# Run prepdata commands in parallel
echo "Running prepdata commands in parallel..."
cat "$prepdata_commands" | parallel -j "${thread}" | tee -a prepdata.log

# Wait for all background processes to complete
wait

echo "All prepdata commands have completed."

# Run realfft for each .dat file
ls *.dat | xargs -n 1 realfft | tee -a realfft.log

echo "All realfft commands have completed."

wait

# Run accelsearch for each .fft file
ls *.fft | xargs -n 1 accelsearch -zmax "${zmax_value}" -numharm "${numharm_value}" | tee -a accelsearch.log

echo "All accelsearch commands have completed."

# Run prepfold
for date in $(ls $data_dir | grep '^[0-9]\{8\}$'); do

    # Run the prepfold command
    echo prepfold -topo -nosearch -mask "${name}_${date}_time${time_value}_rfifind.mask" -par "${parfile}" -noxwin -n "${n_value}" -npart "${npart_value}" -o "${name}_${date}_time${time_value}_dm${dm_value}" "$data_dir/$date/*.fits" >> "$prepfold_commands"
done

# Run prepfold commands in parallel
echo "Running prepfold commands in parallel..."
cat "$prepfold_commands" | parallel -j "${thread}" | tee -a prepfold.log

# Wait for all background processes to complete
wait

echo "All prepfold commands have completed."
