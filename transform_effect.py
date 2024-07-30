import numpy as np
from datetime import datetime
from utils import get_polar_motion_angles

# functions for computing angles
def compute_precession_angles(epoch):
    # Calculate number of Julian centuries since J2000.0
    T = (epoch - datetime(2000, 1, 1, 12)).total_seconds() / 86400.0 / 36525.0
    
    # IAU 2000 precession angles in arcseconds
    zeta = (2306.2181 + 0.30188 * T + 0.017998 * T**2) * T
    z = (2306.2181 + 1.09468 * T + 0.018203 * T**2) * T
    theta = (2004.3109 - 0.42665 * T - 0.041833 * T**2) * T
    
    # Convert angles from arcseconds to radians
    zeta = np.deg2rad(zeta / 3600.0)
    z = np.deg2rad(z / 3600.0)
    theta = np.deg2rad(theta / 3600.0)
    
    return zeta, z, theta

def compute_nutation_angles(epoch):
    # Number of Julian centuries since J2000.0
    T = (epoch - datetime(2000, 1, 1, 12)).total_seconds() / 86400.0 / 36525.0
    
    # Mean elongation of the moon from the sun (in radians)
    D = np.deg2rad((297.85036 + 445267.111480 * T - 0.0019142 * T**2 + T**3 / 189474) % 360)
    
    # Mean anomaly of the sun (in radians)
    M = np.deg2rad((357.52772 + 35999.050340 * T - 0.0001603 * T**2 - T**3 / 300000) % 360)
    
    # Mean anomaly of the moon (in radians)
    M_prime = np.deg2rad((134.96298 + 477198.867398 * T + 0.0086972 * T**2 + T**3 / 56250) % 360)
    
    # Moon's argument of latitude (in radians)
    F = np.deg2rad((93.27191 + 483202.017538 * T - 0.0036825 * T**2 + T**3 / 327270) % 360)
    
    # Longitude of ascending node of the moon's mean orbit (in radians)
    Omega = np.deg2rad((125.04452 - 1934.136261 * T + 0.0020708 * T**2 + T**3 / 450000) % 360)
    
    # Nutation in longitude and obliquity (in arcseconds)
    delta_psi = -17.20 * np.sin(Omega) - 1.32 * np.sin(2 * D) - 0.23 * np.sin(2 * F) + 0.21 * np.sin(2 * Omega)
    delta_epsilon = 9.20 * np.cos(Omega) + 0.57 * np.cos(2 * D) + 0.10 * np.cos(2 * F) - 0.09 * np.cos(2 * Omega)
    
    # Convert from arcseconds to radians
    delta_psi = np.deg2rad(delta_psi / 3600.0)  # change of nutation in longitude
    delta_epsilon = np.deg2rad(delta_epsilon / 3600.0)  #change of nutation on gradient
    
    return delta_psi, delta_epsilon

def compute_rotation_matrix(angle, axis):
    if axis == 'x':
        return np.array([
            [1, 0, 0],
            [0, np.cos(angle), -1 * np.sin(angle)],
            [0, np.sin(angle), np.cos(angle)]
        ])
    elif axis == 'y':
        return np.array([
            [np.cos(angle), 0, np.sin(angle)],
            [0, 1, 0],
            [-1 * np.sin(angle), 0, np.cos(angle)]
        ])
    elif axis == 'z':
        return np.array([
            [np.cos(angle), -1 * np.sin(angle), 0],
            [np.sin(angle), np.cos(angle), 0],
            [0, 0, 1]
        ])

def apply_transformations(ITRS, lst, epoch, iers_data):
    # Self-rotation (Earth rotation)
    earth_rotation_angle = np.deg2rad(lst * 15)
    R_earth_rotation = compute_rotation_matrix(earth_rotation_angle, 'z')
    print(f"Earth rotation matrix:\n{R_earth_rotation}")
    
    # Polar motion
    x_p, y_p = get_polar_motion_angles(epoch, iers_data)
    R_polar_motion = np.dot(compute_rotation_matrix(x_p, 'x'),
                            compute_rotation_matrix(y_p, 'y'))
    print(f"Polar motion matrix:\n{R_polar_motion}")
    
    # Nutation
    delta_psi, delta_epsilon = compute_nutation_angles(epoch)
    R_nutation = np.dot(compute_rotation_matrix(delta_psi, 'z'),
                        compute_rotation_matrix(delta_epsilon, 'x'))
    print(f"Nutation matrix:\n{R_nutation}")
    
    # Precession
    zeta, z, theta = compute_precession_angles(epoch)
    R_precession = np.dot(compute_rotation_matrix(zeta, 'z'),
                          np.dot(compute_rotation_matrix(theta, 'y'),
                                 compute_rotation_matrix(z, 'z')))
    print(f"Precession matrix:\n{R_precession}")
    
    # Combined transformation
    R_total = np.dot(R_precession, np.dot(R_nutation, np.dot(R_polar_motion, R_earth_rotation)))
    print(f"Total transformation matrix:\n{R_total}")
    
    # Apply the combined transformation to the ITRS coordinates
    transformed_coords = np.dot(R_total, ITRS)
    return transformed_coords

