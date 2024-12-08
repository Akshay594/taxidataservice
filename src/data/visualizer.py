# src/data/visualizer.py

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from src.data.explorer import TaxiDataExplorer  # Fixed import statement

class TaxiDataVisualizer:
    """
    Creates visualizations for the NYC Taxi Trip dataset.
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.output_dir = Path("docs/figures")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def plot_trip_duration_distribution(self):
        """Plot the distribution of trip durations."""
        plt.figure(figsize=(10, 6))
        sns.histplot(self.df['trip_duration'] / 60, bins=50)  # Convert to minutes
        plt.title('Distribution of Trip Durations')
        plt.xlabel('Duration (minutes)')
        plt.ylabel('Count')
        plt.savefig(self.output_dir / 'trip_duration_dist.png')
        plt.close()

    def plot_passenger_count_distribution(self):
        """Plot the distribution of passenger counts."""
        plt.figure(figsize=(8, 6))
        sns.countplot(data=self.df, x='passenger_count')
        plt.title('Distribution of Passenger Counts')
        plt.xlabel('Number of Passengers')
        plt.ylabel('Count')
        plt.savefig(self.output_dir / 'passenger_count_dist.png')
        plt.close()

    def plot_hourly_patterns(self):
        """Plot pickup patterns by hour."""
        plt.figure(figsize=(12, 6))
        self.df['hour'] = pd.to_datetime(self.df['pickup_datetime']).dt.hour
        sns.countplot(data=self.df, x='hour')
        plt.title('Pickup Patterns by Hour')
        plt.xlabel('Hour of Day')
        plt.ylabel('Number of Trips')
        plt.savefig(self.output_dir / 'hourly_patterns.png')
        plt.close()

    def generate_all_plots(self):
        """Generate all visualizations."""
        self.plot_trip_duration_distribution()
        self.plot_passenger_count_distribution()
        self.plot_hourly_patterns()

def main():
    # Load data
    explorer = TaxiDataExplorer("data/train.csv")
    df = explorer.load_sample_data()
    
    # Generate visualizations
    visualizer = TaxiDataVisualizer(df)
    visualizer.generate_all_plots()

if __name__ == "__main__":
    main()