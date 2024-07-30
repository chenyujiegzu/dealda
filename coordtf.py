import argparse
import numpy as np
from datetime import datetime
from args_parser import parse_args
from transform_effect import apply_transformations
from utils import download_iers_file, parse_iers_data
from transform_epoch import datetime_to_mjd, lst_from_utc, lon_lat_alt_to_ITRS, convert_to_degrees

def main():
    args = parser.parse_args()

    # Parse the epoch time
    epoch = datetime.strptime(args.epoch, "%Y-%m-%dT%H:%M:%S")
    
    # Download and parse IERS data
    iers_data_text = download_iers_file(args.iers_url)
    iers_data = parse_iers_data(iers_data_text)
    
    # Convert latitude, longitude, and altitude to ITRS coordinates
    # This is a placeholder for the actual coordinate transformation
    ITRS = np.array([args.lon, args.lat, args.alt])
    
    # Apply transformations
    transformed_coords = apply_transformations(ITRS, args.lst, epoch, iers_data)
    
    print(f"Transformed coordinates: {transformed_coords}")

if __name__ == "__main__":
    main()
