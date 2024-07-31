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
    source = np.array([ra, dec])
    observation_time = epoch
    time_diffs = {}
    distance_diffs = {}

    # Store already computed locations and distances to avoid redundant calculations
    locations = {}
    distances = {}
    
    for i, station1 in enumerate(stations):
        if station1['name'] not in locations:
            loc1 = lon_lat_alt_to_ITRS(station1['lon'], station1['lat'], station1['alt'])
            loc1 = apply_transformations(loc1, lst, epoch, iers_data)
            distance1 = np.linalg.norm(loc1)
            locations[station1['name']] = loc1
            distances[station1['name']] = distance1
            print(f"Station {station1['name']} location (ITRS): {loc1}, distance from Earth's center: {distance1:.12f} meters")
        
        for j, station2 in enumerate(stations):
            if i < j:
                if station2['name'] not in locations:
                    loc2 = lon_lat_alt_to_ITRS(station2['lon'], station2['lat'], station2['alt'])
                    loc2 = apply_transformations(loc2, lst, epoch, iers_data)
                    distance2 = np.linalg.norm(loc2)
                    locations[station2['name']] = loc2
                    distances[station2['name']] = distance2
                    print(f"Station {station2['name']} location (ITRS): {loc2}, distance from Earth's center: {distance2:.12f} meters")
                
                loc1 = locations[station1['name']]
                loc2 = locations[station2['name']]
                distance1 = distances[station1['name']]
                distance2 = distances[station2['name']]
               
                # Calculate the distance difference
                distance_diff = distance2 - distance1
                # Calculate the light travel time difference in seconds
                light_travel_time_diff = distance_diff / 299792458.0
                station_pair_key = f"{station1['name']}-{station2['name']}"
                
                time_diffs[station_pair_key] = light_travel_time_diff
                distance_diffs[station_pair_key] = distance_diff
                
    return time_diffs, distance_diffs
