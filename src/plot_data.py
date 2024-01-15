import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def plot_data(df, numDays=7):
    """
    Plot data from the csv archive
    """
    df['utc_time'] = pd.to_datetime(df['utc_time'])  # Convert 'utc_time' to datetime for better plotting

    # Filter the dataframe to include only the last 5 days
    subset = df[df['utc_time'] >= (df['utc_time'].max() - timedelta(days=numDays))]

    plt.figure(figsize=(16, 8))
    plt.plot(subset['utc_time'], subset['average_distance_cm'], marker='+', linestyle='-', color='b')
    plt.title(f'Snow Depth LiDAR - Distance from Sensor (Last {numDays} Days)')
    plt.xlabel('Time (UTC)')
    plt.ylabel('Distance (cm)')

    # Create new datetime range for ticks in even 6-hour increments
    tick_start = subset['utc_time'].min().replace(hour=0, minute=0, second=0, microsecond=0)
    tick_end = subset['utc_time'].max().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    major_ticks = pd.date_range(tick_start, tick_end, freq='6H')

    # Set x-axis ticks to even 6-hour increments
    formatted_ticks = [tick.strftime('%Y-%m-%d %HZ') for tick in major_ticks]
    plt.xticks(major_ticks, formatted_ticks, rotation=90)

    # Set minor x-axis ticks at each data point
    plt.minorticks_on()
    plt.grid(which='minor', linestyle=':', linewidth=0.5, alpha=0.5)

    plt.grid(True, which='major', linestyle='--', linewidth=0.5, alpha=0.7)
    plt.gca().invert_yaxis()  # Invert the y-axis

    # Add current time annotation to the plot
    plt.annotate(f'Last Observation: {subset["utc_time"].max():%Y-%m-%d %H:%M:%S} UTC', xy=(0.99, 0.97), xycoords='axes fraction', fontsize=12, color='red', ha='right')

    # Set axis limits
    plt.xlim(datetime.utcnow()-timedelta(days=numDays), datetime.utcnow()+timedelta(hours=6))
    plt.ylim(100, subset['average_distance_cm'].min()-1)

    plt.tight_layout()

    # Replace 'plot.png' with the desired plot file name
    plt.savefig('/var/www/html/snow-data/plot.png')
    plt.show()

if __name__ == "__main__":
    try:
        # Load dataframe
        df = pd.read_csv('/var/www/html/snow-data/output.csv')

        # Sort the dataframe by time
        df['utc_time'] = pd.to_datetime(df['utc_time'])
        df = df.sort_values(by='utc_time')

        # Plot the data
        plot_data(df, numDays=7)
        print("Plot created successfully.")

    except FileNotFoundError as e:
        print(f"Error: {e}")
