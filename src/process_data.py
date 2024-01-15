import os
import json
import pandas as pd

def process_json_file(json_file_path):
    """
    Extracts data from the archived json files.
    """
    # Read JSON file
    with open(json_file_path, 'r') as file:
        json_data = json.load(file)

    # Process JSON
    print(f'Getting data at {json_data["utc_time"]}')
    data_list = [{'average_distance_cm': json_data['average_distance_cm'], 'utc_time': json_data['utc_time']}]

    # Remove JSON file once read
    os.remove(json_file_path)

    return data_list

def append_data_to_csv(existing_df, json_directory):
    """
    Processes archived JSON data and adds it to the csv archive
    """
    for filename in os.listdir(json_directory):
        if filename.endswith('.json'):
            json_file_path = os.path.join(json_directory, filename)
            processed_data = process_json_file(json_file_path)

            # Append new data to the existing dataframe
            new_data_df = pd.DataFrame(processed_data)
            existing_df = pd.concat([existing_df, new_data_df], ignore_index=True)

    return existing_df

if __name__ == "__main__":
    json_directory = '/home/pi/snow-data/'
    csv_filename = '/var/www/html/snow-data/output.csv'

    try:
        # Load existing data or create a new dataframe if the file doesn't exist
        try:
            existing_df = pd.read_csv(csv_filename)
        except FileNotFoundError:
            existing_df = pd.DataFrame()

        # Append data from JSON files to the existing dataframe
        combined_df = append_data_to_csv(existing_df, json_directory)

        # Export the  dataframe to CSV
        combined_df.to_csv(csv_filename, index=False)
        print('CSV export successful.')

    except Exception as e:
        print(f'Error: {e}')