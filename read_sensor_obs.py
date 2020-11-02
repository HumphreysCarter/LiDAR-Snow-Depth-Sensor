# Carter Humphreys, 11/02/2020
# github.com/HumphreysCarter

import serial
import pandas as pd
from datetime import datetime

# Start serial connection with sensor
sensor = serial.Serial('/dev/ttyACM0', 9600, 8, 'N', 1, timeout=1)

# Initialize empty dataframe
records=pd.DataFrame()

# Read in new data until 10 records are recorded
while len(records) < 10:
    
    # Read data from sensor
    record = sensor.readline()
    
    # De-code byte object as string
    record = record.decode("utf-8")
       
    # Check if valid record
    if '!***' in record and '***!' in record:
              
        # Remove start/end strings and charcaters
        record = record.replace('!*** ', '')
        record = record.replace(' ***!', '')
        record = record.replace('\r\n', '')
        
        # Convert to int
        record = int(record)
               
        # Save record
        records = records.append([{'DateTime_UTC':datetime.utcnow(), 'WaveSpeed_μs':record}], ignore_index=True)
        
# Close serial connection with sensor
sensor.close()

# Export sensor data to CSV
records.to_csv('snow_depth/obs/HC-SR04_Ultrasonic_Sensor_WaveSpeed_Readings.csv', index=False)