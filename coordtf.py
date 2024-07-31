import numpy as np
from datetime import datetime
from args_parser import parse_args
from transform_effect import apply_transformations
from utils import download_iers_file, parse_iers_data
from transform_epoch import datetime_to_mjd, lst_from_utc, lon_lat_alt_to_ITRS, convert_to_degrees

def main():
    args = parse_args()

    # Calculate the initial ITRS coordinates of the observation station
    initial_ITRS = lon_lat_alt_to_ITRS(args.lon, args.lat, args.alt)
    print("Initial ITRS coordinates:", initial_ITRS)
 
    # Calculate the LST based on the observer's longitude and the provided epoch
    epoch = datetime.strptime(args.epoch, '%Y-%m-%dT%H:%M:%S.%f')
    lst = lst_from_utc(epoch, args.lon)

    # Download IERS data from the specified URL
    iers_url = "https://datacenter.iers.org/data/6/bulletina-xxxvii-023.txt"  # Update this with the actual URL
    iers_data_text = download_iers_file(iers_url)
    if not iers_data_text:
        raise ValueError("Failed to download IERS data")

    print(f"Downloaded IERS data: {iers_data_text[:7000]}")
        
    iers_data = parse_iers_data(iers_data_text)
    if not iers_data:
        raise ValueError("Failed to parse IERS data")
        
    # Apply transformations to get the coordinates in ITRS
    transformed_coordinates = apply_transformations(initial_ITRS, lst, epoch, iers_data)
    print("Transformed coordinates in ICRS:", transformed_coordinates)
 
    # Normalize the transformed coordinates to get the unit vector
    unit_vector = transformed_coordinates / np.linalg.norm(transformed_coordinates)
    print("Transformed unit vector coordinates in ICRS:", unit_vector)

if __name__ == "__main__":
    main()
