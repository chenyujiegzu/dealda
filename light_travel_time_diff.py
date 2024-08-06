import numpy as np
from datetime import datetime
from transform_epoch import lon_lat_alt_to_ITRS
from transform_effect import apply_transformations

def calculate_light_travel_time(stations, ra, dec, epoch, iers_data, lst):
    """
    Calculate the light travel time difference for multiple stations observing the same source.
    
    :param stations: List of dictionaries containing station information (name, lon, lat, alt).
    :param ra: Right Ascension of the source in degrees.
    :param dec: Declination of the source in degrees.
    :param epoch: Observation epoch in datetime format.
    :return: Dictionary with station pairs and their light travel time differences in seconds.
    """
    # Convert the source's RA and Dec to a unit vector in the ICRS
    ra_rad = np.deg2rad(float(ra))
    dec_rad = np.deg2rad(float(dec))
    source_vector = np.array([
        np.cos(dec_rad) * np.cos(ra_rad),
        np.cos(dec_rad) * np.sin(ra_rad),
        np.sin(dec_rad)
    ])
    print(f"Source unit vector in ICRS: {source_vector}")
    
    observation_time = epoch
    time_diffs = {}

    # Store already computed locations and distances to avoid redundant calculations
    locations = {}
    
    for i, station1 in enumerate(stations):
        if station1['name'] not in locations:
            loc1 = lon_lat_alt_to_ITRS(station1['lon'], station1['lat'], station1['alt'])
            loc1 = apply_transformations(loc1, lst, epoch, iers_data)
            locations[station1['name']] = loc1
            print(f"Station {station1['name']} vector (ITRS): {loc1}")
        
        for j, station2 in enumerate(stations):
            if i < j:
                if station2['name'] not in locations:
                    loc2 = lon_lat_alt_to_ITRS(station2['lon'], station2['lat'], station2['alt'])
                    loc2 = apply_transformations(loc2, lst, epoch, iers_data)
                    locations[station2['name']] = loc2
                    print(f"Station {station2['name']} vector (ITRS): {loc2}")
                
                loc1 = locations[station1['name']]
                loc2 = locations[station2['name']]
               
                # Calculate the projection length of the station vectors onto the source vector
                proj1_length = np.dot(loc1, source_vector)
                proj2_length = np.dot(loc2, source_vector)
               
                print(f"Projection length of station {station1['name']} vector onto source unit vector: {proj1_length}")
                print(f"Projection length of station {station2['name']} vector onto source unit vector: {proj2_length}")
 
                # Calculate the distance difference (light travel time difference)
                distance_diff = np.abs(proj2_length - proj1_length)
                # Calculate the light travel time difference in seconds (considering speed of light)
                light_travel_time_diff = distance_diff
                
                station_pair_key = f"{station1['name']}-{station2['name']}"
                time_diffs[station_pair_key] = light_travel_time_diff
                
    return time_diffs, locations, source_vector

