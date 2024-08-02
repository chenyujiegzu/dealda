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
            unit_vector1 = loc1 / np.linalg.norm(loc1)
            locations[station1['name']] = unit_vector1
            print(f"Station {station1['name']} unit vector (ITRS): {unit_vector1}")
        
        for j, station2 in enumerate(stations):
            if i < j:
                if station2['name'] not in locations:
                    loc2 = lon_lat_alt_to_ITRS(station2['lon'], station2['lat'], station2['alt'])
                    loc2 = apply_transformations(loc2, lst, epoch, iers_data)
                    unit_vector2 = loc2 / np.linalg.norm(loc2)
                    locations[station2['name']] = unit_vector2
                    print(f"Station {station2['name']} unit vector (ITRS): {unit_vector2}")
                
                unit_vector1 = locations[station1['name']]
                unit_vector2 = locations[station2['name']]
               
                # Calculate the projection of the station unit vectors onto the source vector
                proj1 = np.dot(unit_vector1, source_vector) * source_vector
                proj2 = np.dot(unit_vector2, source_vector) * source_vector
               
                proj1_norm = np.linalg.norm(proj1)
                proj2_norm = np.linalg.norm(proj2)
                
                print(f"Projection of station {station1['name']} unit vector onto source unit vector: {proj1_norm}")
                print(f"Projection of station {station2['name']} unit vector onto source unit vector: {proj2_norm}")
 
                # Calculate the distance difference
                distance_diff = np.linalg.norm(proj2) - np.linalg.norm(proj1)
                # Calculate the light travel time difference
                light_travel_time_diff = distance_diff
                
                station_pair_key = f"{station1['name']}-{station2['name']}"
                time_diffs[station_pair_key] = light_travel_time_diff
                
    return time_diffs, locations, source_vector

