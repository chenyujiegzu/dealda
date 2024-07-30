from datetime import datetime
import numpy as np

def datetime_to_mjd(epoch):
    JD = (epoch - datetime(2000, 1, 1, 12)).total_seconds() / 86400.0 + 2451545.0
    MJD = JD - 2400000.5
    return MJD

def lst_from_utc(epoch, lon):
    """
    Calculate Local Sidereal Time (LST) from UTC datetime and observer's longitude.
    """
    JD = (epoch - datetime(2000, 1, 1, 12)).days + 2451545.0
    T = (JD - 2451545.0) / 36525.0

    GMST = 280.46061837 + 360.98564736629 * (JD - 2451545.0) + 0.000387933 * T**2 - T**3 / 38710000.0
    GMST = GMST % 360.0
    LST = GMST + lon
    LST = LST % 360.0

    return LST / 15.0  # Convert degrees to hours

def lon_lat_alt_to_ITRS(lon, lat, alt):
    # Use the World Geodetic System 84 (WGS84).
    a = 6378137.0  # Semi-major axis in meters
    f = 1 / 298.257223563  # Flattening
    e2 = f * (2 - f)  # Square of eccentricity
    
    lon_rad = np.deg2rad(lon)
    lat_rad = np.deg2rad(lat)

    # Radius of curvature in the dimension
    N = a / np.sqrt(1 - e2 * np.sin(lat_rad)**2)

    # Calculate the position of observation station in ITRS/WGS84
    x = (N + alt) * np.cos(lat_rad) * np.cos(lon_rad)
    y = (N + alt) * np.cos(lat_rad) * np.sin(lon_rad)
    z = (N * (1 - e2) + alt) * np.sin(lat_rad)
 
    # Take the obtained xyz as an array.
    return np.array([x, y, z])

def convert_to_degrees(ra, dec, ra_format, dec_format):
    if (ra_format == 'sexagesimal'):
        ra_deg = 15 * (ra[0] + ra[1] / 60.0 + ra[2] / 3600.0)
    else:
        ra_deg = ra[0]
    
    if dec_format == 'sexagesimal':
        sign = 1 if dec[0] >= 0 else -1
        dec_deg = sign * (abs(dec[0]) + dec[1] / 60.0 + dec[2] / 3600.0)
    else:
        dec_deg = dec[0]
    
    return ra_deg, dec_deg
