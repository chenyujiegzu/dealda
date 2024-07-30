import numpy as np
from datetime import datetime
import requests


def download_iers_file(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def parse_iers_data(iers_data_text):
    iers_data = []
    data_section_started = False
    lines = iers_data_text.splitlines()
    for line in lines:
        if 'MJD' in line:
            data_section_started = True
            continue
        if data_section_started:
            parts = line.split()
            
            if len(parts) >= 6 and parts[0].isdigit():
                year = int(parts[0])
                month = int(parts[1])
                day = int(parts[2])
                x_p = float(parts[4])
                y_p = float(parts[5])
                date = datetime(year, month, day)
                iers_data.append((date, x_p, y_p))
    return iers_data

def get_polar_motion_angles(epoch, iers_data):
    if not iers_data:
        raise ValueError("IERS data is empty")
        
    # Find closest dates before and after the epoch
    before_epoch = [data for data in iers_data if data[0] <= epoch]
    after_epoch = [data for data in iers_data if data[0] > epoch]

    if not before_epoch or not after_epoch:
        raise ValueError("Insufficient IERS data to perform interpolation")

    closest_before = max(before_epoch, key=lambda x: x[0])
    closest_after = min(after_epoch, key=lambda x: x[0])

    print(f"Epoch: {epoch}, closest date is: {closest_before} and {closest_after}")
    
    # Linear interpolation
    delta_t_before = (epoch - closest_before[0]).total_seconds()
    delta_t_after = (closest_after[0] - epoch).total_seconds()
    total_delta_t = (closest_after[0] - closest_before[0]).total_seconds()

    if total_delta_t == 0:
        raise ValueError("Dates are the same, unable to interpolate")

    x_p = closest_before[1] + (delta_t_before / total_delta_t) * (closest_after[1] - closest_before[1])
    y_p = closest_before[2] + (delta_t_before / total_delta_t) * (closest_after[2] - closest_before[2])

    print(f"Linear interpolation to obtain the polar motion parameters: x_p: {x_p}, y_p: {y_p}")
    
    # Convert to radians
    x_p = np.deg2rad(x_p / 3600.0)
    y_p = np.deg2rad(y_p / 3600.0)
    
    return x_p, y_p

