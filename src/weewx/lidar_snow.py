import json
import weewx
import weewx.units
from weewx.engine import StdService
from datetime import datetime


class AddLidarSnowData(StdService):

    def __init__(self, engine, config_dict):

        # Initialize my superclass first:
        super(AddLidarSnowData, self).__init__(engine, config_dict)

        # Bind to any new archive record events:
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)

        # Get unit system in use
        unit_system = config_dict['StdConvert']['target_unit']  # Options are 'US', 'METRICWX', or 'METRIC'
        if unit_system == 'US':
            self.units_snow = weewx.units.USUnits['group_rain']
            self.units_temp = weewx.units.USUnits['group_temperature']
        elif unit_system == 'METRIC':
            self.units_snow = weewx.units.MetricUnits['group_rain']
            self.units_temp = weewx.units.MetricUnits['group_temperature']
        elif unit_system == 'METRICWX':
            self.units_snow = weewx.units.MetricWXUnits['group_rain']
            self.units_temp = weewx.units.MetricWXUnits['group_temperature']

        # Get data from config
        self.api_directory = '/home/pi/lidar-snow/data/api/'
        self.stale_minutes = 2
        self.sensor_id = 'b0b21c043834'
        self.sensor_datum = 103

    def get_sensor_data(self, serial_number):
        with open(f'{self.api_directory}/LiDAR_SnowDepth_{serial_number}.json', 'r') as f:
            data = json.load(f)

        # Only return data if data no more than 1 minute old
        data_date = datetime.strptime(data['datetime'], '%Y-%m-%dT%H:%M:%S.%f')
        if (datetime.utcnow() - data_date).total_seconds() <= self.stale_minutes * 60:
            return data

        return None

    def get_value(self, data, key):
        try:
            return data[key]
        except KeyError as e:
            return None

    def new_archive_record(self, event):
        # Get data from sensor
        if self.sensor_id is not None:
            data = self.get_sensor_data(self.sensor_id)

            if data is not None:
                # Get distance from LiDAR sensor
                lidar_distance = self.get_value(data, 'average_distance')

                if lidar_distance is not None:
                    # Calculate snow depth from distance and datum
                    lidar_snowdepth = self.sensor_datum-lidar_distance

                    # Convert units as needed, sensor data is in cm.
                    if self.units_snow != 'cm':
                        conversion = weewx.units.conversionDict['cm'][self.units_snow]
                        lidar_distance = conversion(lidar_distance)
                        lidar_snowdepth = conversion(lidar_snowdepth)

                    # Add data to record
                    event.record['lidar_distance'] = lidar_distance
                    event.record['lidar_snowdepth'] = lidar_snowdepth

                else:
                    event.record['lidar_distance'] = None
                    event.record['lidar_snowdepth'] = None

                # Add sensor board temperature
                lidar_boardtemp = self.get_value(data, 'board_temp')

                if lidar_boardtemp is not None:
                    # Convert from degC if needed
                    if self.units_temp != 'degree_C':
                        conversion = weewx.units.conversionDict['degree_C'][self.units_temp]
                        lidar_boardtemp = conversion(lidar_boardtemp)

                    event.record['lidar_boardtemp'] = lidar_boardtemp
                else:
                    event.record['lidar_boardtemp'] = None

                # Add sensor WiFi signal
                event.record['lidar_signal'] = self.get_value(data, 'wifi')
