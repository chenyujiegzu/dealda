import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Calculate light path delay for multiple stations.")
    parser.add_argument('--lat', type=float, required=True, help='Latitude of the station in degrees.')
    parser.add_argument('--lon', type=float, required=True, help='Longitude of the station in degrees.')
    parser.add_argument('--alt', type=float, default=0, help='Altitude of the station in meters.')
    parser.add_argument('--epoch', type=str, required=True, help='Epoch time in YYYY-MM-DDTHH:MM:SS format.')
    parser.add_argument('--lst', type=float, required=True, help='Local Sidereal Time in degrees.')
    parser.add_argument('--iers-url', type=str, required=True, help='URL of the IERS Bulletin A file.')
    
    args = parser.parse_args()
    return args
