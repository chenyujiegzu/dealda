import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Coordinate transformation script.")
    parser.add_argument('--ra', required=True, help="Right Ascension of the source.")
    parser.add_argument('--dec', required=True, help="Declination of the source.")
    parser.add_argument('--lon', type=float, required=True, help="Longitude of the observation station.")
    parser.add_argument('--lat', type=float, required=True, help="Latitude of the observation station.")
    parser.add_argument('--alt', type=float, required=True, help="Altitude of the observation station.")
    parser.add_argument('--epoch', required=True, help="Observation epoch in YYYY-MM-DDTHH:MM:SS.SSS format.")
    parser.add_argument('--format', required=True, choices=['degrees', 'sexagesimal'], help="Input format of RA and Dec.") 
    return parser.parse_args()
    

