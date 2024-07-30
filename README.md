<h1 style="text-align: center;">COORDTF</h1>  

Coordinate Transformation Script   
This project provides a Python script to convert station ITRF (International Terrestrial Reference Frame) coordinates to ICRF (International Celestial Reference Frame) coordinates. The transformation process considers various Earth motions, including Earth rotation, polar motion, nutation, and precession, to obtain precise ICRF coordinates.

## Table of Contents  
1. [Project Structure](#project-structure)  
2. [Installation](#installation)  
3. [Usage](#usage)  
4. [Example](#example)  
5. [Details of the Transformation Process](#details-of-the-transformation-process)  

## Project Structure  
The project is modularized into the following files:  
args_parser.py: Handles command-line argument parsing.  
coordtf.py: Main script that orchestrates the coordinate transformation.  
transform_effect.py: Contains functions related to specific transformation effects like Earth rotation, polar motion, nutation, and precession.  
transform_epoch.py: Contains functions to compute angles and parameters for nutation and precession based on the epoch.  
utils.py: Utility functions such as downloading and parsing IERS data, converting coordinates, etc.  

## Installation  
git clone https://github.com/cyj-hue/coordtf.git   
cd /path/coordrf   
pip install numpy  

## Usage  
To run the script, use the following command:  
python coordtf.py --ra <RA> --dec <Dec> --lon <Longitude> --lat <Latitude> --alt <Altitude> --epoch <Epoch> --format <Format>  

## Parameters:  
--ra: Right Ascension of the source.  
--dec: Declination of the source.  
--lon: Longitude of the observation station.  
--lat: Latitude of the observation station.  
--alt: Altitude of the observation station.  
--epoch: Observation epoch in YYYY-MM-DDTHH:MM:SS.SSS format.  
--format: Input format of RA and Dec (degrees or sexagesimal).  

## Example:  
python coordtf.py --ra "14:15:39.7" --dec "-60:50:02" --lon 21.443 --lat 37.983 --alt 100 --epoch "2024-07-30T12:00:00.000" --format sexagesimal  

## Details of the Transformation Process  
1.Earth Rotation:  
The Earth rotation angle is computed based on the Local Sidereal Time (LST), and the Earth rotation matrix is applied to convert ITRF coordinates to geocentric coordinates.  

2.Polar Motion:  
Polar motion parameters (x_p and y_p) are obtained from IERS data. Linear interpolation is used to obtain accurate polar motion parameters.  

3.Nutation:  
Nutation angles (delta_psi and delta_epsilon) are calculated, and the nutation matrix is applied to correct short-term changes in the Earth's rotation axis.  

4.Precession:  
Precession angles (zeta, z, and theta) are calculated, and the precession matrix is applied to correct long-term changes in the Earth's rotation axis.  
5.Combining All Transformation Matrices:  
All the above rotation matrices are multiplied to obtain the total transformation matrix R_total, which is then applied to the initial ITRF coordinates to obtain the final ICRF coordinates.  
