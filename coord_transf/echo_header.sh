#!/bin/bash

# define parameters
parameters=(
    "DUMMY"
    "HDR_VERSION 1.0"
    "BW 500"
    "FREQ 1250"
    "TELESCOPE FAST"
    "RECEIVER 19BEAM"
    "INSTRUMENT ROACH2"
    "SOURCE M14A"
    "MODE PSR"
    "NBIT 8"
    "NCHAN 1"
    "NDIM 1"
    "NPOL 1"
    "NDAT 128849018880"
    "OBS_OFFSET 0"
    "UTC_START 2019-07-01-11:20:00"
    "TSAMP 0.001"
    "RESOLUTION 4"
)

# define the output file name
output_file=${1:-"baseband_header"}.hdr

# clear or create the output file
> "$output_file"

# Loop through the array and output each parameter to the file
for param in "${parameters[@]}"; do
    echo $param >> "$output_file"
done
