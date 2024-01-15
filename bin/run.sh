#!/bin/bash

# Generate timestamp
timestamp=$(date +"%Y%m%d%H%M%S")

# Download data from sensor
curl -o "/home/pi/snow-data/snow_${timestamp}.json" "http://10.114.98.101"

# Load data into archive
python3 /home/pi/scripts/archive_snow_data.py

# Plot data
python3 /home/pi/scripts/plot_snow_data.py
