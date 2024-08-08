import sys
import argparse

def parse_station(station_str):
    """
    Custom function to parse station information.
    Format: name:lon lat alt
    Example: FAST:106.8561 25.6500 1065
    """
    print(f"Parsing station: {station_str}")  # Debugging output
    try:
        name, rest = station_str.split(':', 1)
        lon_lat_alt = rest.split()
        
        # Ensure the correct number of elements
        if len(lon_lat_alt) != 3:
            raise argparse.ArgumentTypeError(f"Invalid station format (expected 3 elements but got {len(lon_lat_alt)}): {station_str}")
        
        lon = float(lon_lat_alt[0])
        lat = float(lon_lat_alt[1])
        alt = float(lon_lat_alt[2])
        return {'name': name, 'lon': lon, 'lat': lat, 'alt': alt}
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"Invalid station format: {station_str}") from e

def parse_args_coordtf():
    parser = argparse.ArgumentParser(description="Coordinate transformation script.")
    parser.add_argument('--ra', required=True, help="Right Ascension of the source.")
    parser.add_argument('--dec', required=True, help="Declination of the source.")
    parser.add_argument('--lon', type=float, required=True, help="Longitude of the observation station.")
    parser.add_argument('--lat', type=float, required=True, help="Latitude of the observation station.")
    parser.add_argument('--alt', type=float, required=True, help="Altitude of the observation station.")
    parser.add_argument('--epoch', required=True, help="Observation epoch in YYYY-MM-DDTHH:MM:SS.SSS format.")
    parser.add_argument('--format', required=True, choices=['degrees', 'sexagesimal'], help="Input format of RA and Dec.") 
    return parser.parse_args()

def parse_args_lighttf():
    parser = argparse.ArgumentParser(description="Light travel time difference calculation script.")
    parser.add_argument('--ra', required=True, help="Right Ascension of the source.")
    parser.add_argument('--dec', required=True, help="Declination of the source.")
    parser.add_argument('--epoch', required=True, help="Observation epoch in YYYY-MM-DDTHH:MM:SS.SSS format.")
    parser.add_argument('--format', required=True, choices=['degrees', 'sexagesimal'], help="Input format of RA and Dec.") 
    parser.add_argument('--stations', required=True, nargs='+', type=parse_station,
                        help="Observation stations in the format name:lon lat alt (e.g., FAST:106.8561 25.6500 1065).")
    return parser.parse_args()

def parse_args_deal_baseband():
    parser = argparse.ArgumentParser(description="Read and combine baseband data files.")
    parser.add_argument('file1', type=str, help="Path to the first baseband data file.")
    parser.add_argument('file2', type=str, help="Path to the second baseband data file.")
    parser.add_argument('-o', type=str, required=True, help="Path to the output merged data file.")
    parser.add_argument('-t', type=int, default=4, help="Numbers of parallel processing (default: 4).")
    return parser.parse_args()

def parse_args():
    script_name = sys.argv[0]
    if 'coordtf.py' in script_name:
        return parse_args_coordtf()
    elif 'lighttf.py' in script_name:
        return parse_args_lighttf()
    elif 'deal_baseband.py' in script_name:
        return parse_args_deal_baseband()
    else:
        raise RuntimeError("Unknown script. Please run coordtf.py, lighttf.py, or deal_baseband.py.")
