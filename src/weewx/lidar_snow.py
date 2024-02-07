import json
import weewx
from weewx.engine import StdService
from datetime import datetime

class AddLidarSnowData(StdService):

    def __init__(self, engine, config_dict):

        # Initialize my superclass first:
        super(AddLidarSnowData, self).__init__(engine, config_dict)

        # Bind to any new archive record events:
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)

        # Get data from config
        self.api_directory = '/home/pi/lidar-snow/data/api/'
        self.stale_minutes = 2
        self.sensor_id = 'b0b21c043834'

    def get_sensor_data(self, serial_number):
        with open(f'{self.api_directory}/LiDAR_SnowDepth_{serial_number}.json', 'r') as f:
            data = json.load(f)

        # Only return data if data no more than 1 minute old
        data_date = datetime.strptime(data['datetime'], '%Y-%m-%dT%H:%M:%S.%f')
        if (datetime.utcnow()-data_date).total_seconds() <= self.stale_minutes * 60:
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
                event.record['lidar_distance'] = self.get_value(data, 'average_distance')
                event.record['lidar_boardtemp'] = self.get_value(data, 'board_temp')
                event.record['lidar_signal'] = self.get_value(data, 'wifi')