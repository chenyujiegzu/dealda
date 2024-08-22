# !/bin/bash

usage() {
    echo "usage: $0 [-h] [-source <source_name>]"
    echo
    echo "parameters:"
    echo "  -source           specify the source name and create the source name directory in the target directory."
    echo
    echo "example:"
    echo "  sh $0 -source source_name(1004/baseband_19beam)"
    exit 0
}

# check whether the parameter is passed
if [ $# -eq 0 ]; then
    usage
fi

# give the data directory
data_dir='/data187'

# give the target directory
target_dir='/home/cyj'

# see the current directory
current_dir=$(pwd)

# the giant.psh path
giant_file='/home/cyj/giant.psh'

# the source hdr path
hdr_file='/home/cyj/header.hdr'

# dspsr parameters
dspsr_params="-t 4 -cpu 4 -s -J giant.psh -F 4096:D -K -e fits -a psrfits"

# shift the path
if [ "$current_dir" != "$target_dir" ]; then
    cd "$target_dir" || {
        echo "$target_dir : error ! no such directory!"
        exit 1
    }
else
    echo "nothing to do, continue"
    
    # source the .bashrc in target_dir
    if [ -f ./.bashrc ]; then
        source ./.bashrc
        echo ".bashrc loaded from $target_dir"
    else
        echo "no .bashrc file found in $target_dir"
    fi
else
    echo "already in the target directory: $current_dir"
fi

# parse the source name
while [[ $# -gt 0 ]]
do
    key="$1"
    case $key in
        -source)
        source_name="$2"
        shift # past argument
        shift # past value
        ;;
        *)
        echo "unknown parameter : $1"
        usage
        ;;
    esac
done

# check whether the former name folder is specified.
if [ -z "$source_name" ]; then
    echo "error: please use the "-source" to specify the source."
    exit 1
fi

# mkdir the source name folder
mkdir -p "$source_name"
cd "$source_name" || {
    echo "unable to enter the directory : $source_name"
    exit 1
}

# list all date directories and sort by date
date_dirs=$(ls "$data_dir/$source_name" | sort)

# enter the date directory one by one and create symbolic links
for date_dir in $date_dirs; do
    mkdir -p "$date_dir"
    echo "enter the date directory: $date_dir"
    cd "$date_dir" || {
        echo "unable enter the date directory: $date_dir"
        exit 1
    }
    
    # create symbolic links
    ln -s "$data_dir/$source_name/$date_dir/"*.zst .

    echo "date directory created: $data_dir/$source_name/$date_dir/*.zst"

    # define the combine output name
    output_pol0="${source_name}_${date_dir}_combine_pol0"
    output_pol1="${source_name}_${date_dir}_combine_pol1"

    # parallel execution of the combine commands
    cat *pol0* > "${output_pol0}.dat" &
    cat *pol1* > "${output_pol1}.dat" &   
 
    # waiting for the background task to complete
    wait

    echo "the $output_pol0 and $output_pol1 has been completed "
    
    # generate ephemeris file
    psrcat -e "$source_name" > "${source_name}_${date_dir}.par"
    echo "ephemeris file has been generated: ${source_name}_${date_dir}.par" 
    
    # cp the source name's hdr to local dir
    cp "$hdr_file" "${output_pol0}.hdr"
    cp "$hdr_file" "${output_pol1}.hdr" 

    # cp the giant.psh to local dir
    cp "$giant_file" .

    # use the dspsr to fold the combine data
    dspsr_pol0="dspsr $dspsr_params -E ${source_name}_${date_dir}.par ${output_pol0}.dat"
    dspsr_pol1="dspsr $dspsr_params -E ${source_name}_${date_dir}.par ${output_pol1}.dat"
    
    echo "use dspsr to deal with the ${output_pol0}.dat..."
    $dspsr_pol0 &
    echo "use dspsr to deal with the ${output_pol0}.dat..." 
    $dspsr_pol1 &

    # back to the previous directory
    cd ..
done

# wainting all dspsr command finished
wait

echo "operation completed"
