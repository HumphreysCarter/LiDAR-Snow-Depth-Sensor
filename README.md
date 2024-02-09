# LiDAR Snow Depth Measurements

![Example data plot!](docs/example_plot.png)

## Hardware
- [Garmin LIDAR-Lite v4 LED - Distance Measurement Sensor](https://www.sparkfun.com/products/18009)
- [SparkFun IoT RedBoard ESP32 Development Board](https://www.sparkfun.com/products/19177)

## Setup

### Red Board
The software to run the LiDAR from the RedBoard is contained within the `src/lidar/lidar.ino` file. This file should be uploaded to the board using the Arduino IDE, refer to the [SparkFun hookup guide](https://learn.sparkfun.com/tutorials/garmin-lidar-lite-v4-qwiic-hookup-guide/arduino-library) for installing the software and uploading to the board.

Before uploading, configure the `lidar.ino` file by setting the following variables:

Required Variables
+ `API_SERVER` - Location for the RedBoard to send data to via POST.
+ `WIFI_SSID` and `WIFI_PASSWORD` - SSID and password for the Wi-Fi network the RedBoard should connect to.

Optional Variables
+ `LIDAR_CONFIG` = 0; // LiDAR setting 
+ `LIDAR_CALIBRATION` = 0.0; // Error of the LiDAR sensor
+ `NUM_MEASUREMENTS` = 60;  // Number of measurements to take for average
+ `MEASUREMENT_INTERVAL` = 1000;  // Interval between Lidar measurements in milliseconds (adjust as needed)

### Data Server
The data server will be the device that receives the POST request from the RedBoard from the `src/server.py` script. If using WeeWx, this should be the device with your WeeWx installation. The script will listen on port 7070 by default for data from the sensor, then write reach POST to a csv database.

#### Server Dependencies
+ Python 3.9 or higher
+ Pandas

#### Server Usage
The server script supports the following command line arguments:
- `--path DIRECTORY`: Specifies the data directory for the API and archive data. This directory will be created if it does not exist.
- `--port [PORT]`: Optional. Specifies the port number to run the server on. If not provided, the default port `7070` will be used.

Example Usage: `python src/server.py --path /path/to/data/ [--port 7070]`


### WeeWx Configuration

1. Add the five new elements to the WeeWx database.
    ```
    ./weewx/bin/wee_database --add-column=lidar_distance --type=REAL
    ./weewx/bin/wee_database --add-column=lidar_snowdepth --type=REAL
    ./weewx/bin/wee_database --add-column=lidar_snowfall --type=REAL
    ./weewx/bin/wee_database --add-column=lidar_boardtemp --type=REAL
    ./weewx/bin/wee_database --add-column=lidar_signal --type=REAL
    ```

2. Define the units for the elements by adding the code below to the WeeWx extension file at `weewx/bin/user/extensions.py`.
    ```
    import weewx.units
    weewx.units.obs_group_dict["lidar_snowdepth"] = "group_rain"
    weewx.units.obs_group_dict["lidar_snowfall"] = "group_rain"
    weewx.units.obs_group_dict["lidar_distance"] = "group_rain"
    weewx.units.obs_group_dict["lidar_boardtemp"] = "group_temperature"
    ```

3. Copy the LiDAR StdService to the weewx user scripts directory.
    ```
    cp src/weewx/lidar_snow.py weewx/bin/user/.
    ```
   
4. Add the service to your WeeWx config file under `[Engine]` > `[[Services]]` > `data_services`. 
    ```
    data_services = user.lidar_snow.AddLidarSnowData
    ```
   
5. Add the following code to the end of your WeeWx config file and enter values for each.
    ```
    ##############################################################################
    
    #   This section configures the LiDAR snow depth ingest.
    
    [SnowDepthLiDAR]

        api_directory = !** Enter the path to the API directory **!
        stale_minutes = 2
        sensor_id = !** Enter the MAC address (without the :) of the sensor **!
        sensor_datum = !** Enter the height of the sensor above ground in cm **!
    ```
   
6. Copy the cheetah report templates into the Seasons skin.

    ```
    cp src/weewx/lidarsnow.html.tmpl weewx/skins/Seasons/.
    cp src/weewx/lidarsnow.inc weewx/skins/Seasons/.
    ```
   
7. Add `#include "lidarsnow.inc"` line to the widget_group div within the `weewx/skins/Seasons/index.html.tmpl` file.
   ```
      <div id="widget_group">
        #include "current.inc"
        #include "lidarsnow.inc"
        #include "radar.inc"
        #include "satellite.inc"
        #include "sunmoon.inc"
        #include "hilo.inc"
        #include "sensors.inc"
        #include "about.inc"
        #include "map.inc"
      </div>
   ```
   
8. Add the following to the day, week, month, and year plots within the skin configuration file at the `weewx/skins/Seasons/skin.conf`.
   ```
    [[day_images]]
   
        [[[day_lidarsnowfall]]]
            yscale = 0.0, None, 0.5
            plot_type = bar
            [[[[lidar_snowfall]]]]
   
        [[[day_lidarsnowdepth]]]
            yscale = 0.0, None, 0.5
            plot_type = bar
            [[[[lidar_snowdepth]]]]
   
        [[[day_lidardistance]]]
            yscale = None, None, 1.0
            plot_type = bar
            [[[[lidar_distance]]]]
   ```
   ```
   [[week_images]]
   
      [[[week_lidarsnowfall]]]
         yscale = 0.0, None, 0.5
         plot_type = bar
         [[[[lidar_snowfall]]]]
      
      [[[week_lidarsnowdepth]]]
         yscale = 0.0, None, 0.5
         plot_type = bar
         [[[[lidar_snowdepth]]]]
      
      [[[week_lidardistance]]]
         yscale = None, None, 1.0
         plot_type = bar
         [[[[lidar_distance]]]]
   ```
   ```
   [[month_images]]
   
      [[[month_lidarsnowfall]]]
         yscale = 0.0, None, 0.5
         plot_type = bar
         [[[[lidar_snowfall]]]]
      
      [[[month_lidarsnowdepth]]]
         yscale = 0.0, None, 0.5
         plot_type = bar
         [[[[lidar_snowdepth]]]]
      
      [[[month_lidardistance]]]
         yscale = None, None, 1.0
         plot_type = bar
         [[[[lidar_distance]]]]
   ```
   ```
   [[year_images]]
   
      [[[year_lidarsnowfall]]]
         yscale = 0.0, None, 0.5
         plot_type = bar
         [[[[lidar_snowfall]]]]
      
      [[[year_lidarsnowdepth]]]
         yscale = 0.0, None, 0.5
         plot_type = bar
         [[[[lidar_snowdepth]]]]
      
      [[[year_lidardistance]]]
         yscale = None, None, 1.0
         plot_type = bar
         [[[[lidar_distance]]]]
   ```
   
9. Restart WeeWx `sudo service weewx restart` and data should begin to populate.