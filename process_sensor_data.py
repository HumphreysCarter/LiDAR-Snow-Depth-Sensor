# Carter Humphreys, 11/02/2020
# github.com/HumphreysCarter

import math
import numpy as np
import pandas as pd
from metpy.units import units

def get_air_temperature(wu_station, api_key):
    """
    Get current air temperature using Weather Underground API
    """
    # Generate data URL
    dataURL = f'https://api.weather.com/v2/pws/observations/current?stationId={wu_station}&format=json&units=m&apiKey={api_key}'
    
    # Get data from API
    data = pd.read_json(dataURL)
    
    # Extract air temeprature
    air_temp = data.values[0][0]['metric']['temp']
    
    # Attach units to value
    air_temp = air_temp * units.degC
    
    return air_temp

def calc_speed_of_sound(T):
    """
    Calculates speed of sound based on air temperature
    """
    # Constants
    k = 1.4
    R = 286.9
    T = T.to('kelvin').magnitude
    
    # Speed of sound equation    
    c = math.pow(1.4*(R*T), 0.5) * units('m/s')
    
    return c

def calc_snow_depth(sensor_height, wave_speed, speed_of_sound):
    """
    Calculates the snow depth from the total trip time of the sound wave
    """
    # Convert units for calculation
    sensor_height = sensor_height.to('m')
    wave_speed = wave_speed.to('s')
    speed_of_sound = speed_of_sound.to('m/s')
    
    # Divide total wave speed by 2 to get inital trip speed
    wave_speed = wave_speed / 2
    
    # Get distance from sensor to surface
    d = wave_speed * speed_of_sound
    
    # Subtract depth from sensor height to get snow depth
    snow_depth = sensor_height - d
    
    return snow_depth
    
def process_sensor_data(records, sensor_height, air_temp, unit='cm', precision=1, truncate_neg_zero=True, no_negative=False):
    """
    Gets snow depth from sensor records
    """
    # Calculate speed of sound from air temperature
    speed_of_sound = calc_speed_of_sound(air_temp)
    
    # Calcualte snow depth from each record
    snow_depth_obs = []
    for wave_speed in records.WaveSpeed_μs:
        # Attach units to wave speed
        wave_speed = wave_speed * units.microseconds

        # Calculate snow depth
        snow_depth = calc_snow_depth(sensor_height, wave_speed, speed_of_sound)
        snow_depth_obs.append(snow_depth)

    # Calculate average depth from observations
    snow_depth = sum(snow_depth_obs)/len(snow_depth_obs)

    # Round to nearest tenth of a centimeter
    snow_depth = round(snow_depth.to(unit), precision)
    
    # Check if number is negative
    if no_negative and snow_depth.magnitude < 0:
        return (records.DateTime_UTC[0], np.nan)
    
    # Change values between -1 and 0 to 0
    if truncate_neg_zero and snow_depth.magnitude <= 0 and snow_depth.magnitude > -1:
        return (records.DateTime_UTC[0], round(0.0  * units(unit), precision))
    
    return (records.DateTime_UTC[0], snow_depth)

# Load configuration
f = open('/home/pi/workspace/Ultrasonic-Snow-Depth-Sensor/config.json', 'r')
config = json.loads(f.read())

# Specify sensor height
sensor_height = config['SensorHeight'] * units(config['HeightUnit'])

# Get air temeprature from Weather Underground
air_temp = get_air_temperature(config['station'], config['APIkey'])

# Read in sensor data
records = pd.read_csv(f'{config["DataPath"]}/obs/HC-SR04_Ultrasonic_Sensor_WaveSpeed_Readings.csv')

# Process sensor observations
time, snow_depth = process_sensor_data(records, sensor_height, air_temp)

# Export to file
with open(f'{config["DataPath"]}/snow_depth.csv', 'a') as f:
    f.write(f'\n{time},{snow_depth.magnitude},{snow_depth.units}')