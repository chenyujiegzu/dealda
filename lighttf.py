from datetime import datetime
from args_parser import parse_args
from light_travel_time_diff import calculate_light_travel_time
from utils import download_iers_file, parse_iers_data
from transform_epoch import datetime_to_mjd, lst_from_utc, lon_lat_alt_to_ITRS

def main():
    # Parse command line arguments
    args = parse_args()
    
    # Parse and convert station data from args.stations
    stations = []
    for station in args.stations:
        name = station['name']
        lon = station['lon']
        lat = station['lat']
        alt = station['alt']
        
        # Calculate the initial ITRS coordinates of the observation station
        initial_ITRS = lon_lat_alt_to_ITRS(lon, lat, alt)
        print(f"Station {name} initial ITRS coordinates: {initial_ITRS}")
        
        stations.append({
            'name': name,
            'lon': lon,
            'lat': lat,
            'alt': alt,
            'ITRS': initial_ITRS
        })

    # Calculate the LST based on the observer's longitude and the provided epoch
    # Using the longitude of the first station for LST calculation
    epoch = datetime.strptime(args.epoch, '%Y-%m-%dT%H:%M:%S.%f')
    lst = lst_from_utc(epoch, stations[0]['lon'])

    # Download IERS data from the specified URL
    iers_url = "https://datacenter.iers.org/data/6/bulletina-xxxvii-023.txt"  # Update this with the actual URL
    iers_data_text = download_iers_file(iers_url)
    if not iers_data_text:
        raise ValueError("Failed to download IERS data")

    iers_data = parse_iers_data(iers_data_text)
    if not iers_data:
        raise ValueError("Failed to parse IERS data")

    # Calculate light travel time differences using the parsed arguments
    time_diffs, distance_diffs = calculate_light_travel_time(
        stations=stations, 
        ra=args.ra, 
        dec=args.dec, 
        epoch=epoch,
        iers_data=iers_data,  # Pass IERS data for transformation
        lst=lst
    )
    
    # Print the detailed time differences
    for station_pair, time_diff in time_diffs.items():
        station1, station2 = station_pair.split('-')
        distance_diff = distance_diffs[station_pair]
        print(f"Between stations {station1} and {station2}:")
        print(f"  Light travel time difference: {time_diff:.12f} seconds")
        print(f"  Distance difference in ICRS: {distance_diff:.12f} meters")

if __name__ == "__main__":
    main()
