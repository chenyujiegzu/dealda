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

def convert_to_degrees(ra, dec):
    def sexagesimal_to_decimal(sexagesimal, is_ra):
        parts = sexagesimal.split(':')
        if len(parts) == 3:
            hours_or_degrees = float(parts[0])
            minutes = float(parts[1])
            seconds = float(parts[2])
            if is_ra:
                return 15 * (hours_or_degrees + minutes / 60 + seconds / 3600)
            else:
                sign = 1 if hours_or_degrees >= 0 else -1
                return sign * (abs(hours_or_degrees) + minutes / 60 + seconds / 3600)
        else:
            raise ValueError("Invalid sexagesimal format")

    ra_deg = sexagesimal_to_decimal(ra, is_ra=True)
    dec_deg = sexagesimal_to_decimal(dec, is_ra=False)
    
    return ra_deg, dec_deg


