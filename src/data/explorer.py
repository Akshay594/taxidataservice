# src/data/explorer.py

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Dict, Any, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

class TaxiDataExplorer:
    """
    Explores and analyzes the NYC Taxi Trip dataset to understand its characteristics.
    """
    def __init__(self, data_path: str):
        self.logger = self._setup_logging()
        self.data_path = Path(data_path)
        self.df = None
        
    def _setup_logging(self) -> logging.Logger:
        """Configure logging for the explorer."""
        logger = logging.getLogger('TaxiDataExplorer')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def load_sample_data(self, sample_size: int = 100000) -> pd.DataFrame:
        """
        Load a sample of the data for initial exploration.
        """
        try:
            self.df = pd.read_csv(self.data_path, nrows=sample_size)
            self.logger.info(f"Loaded sample of {len(self.df)} rows")
            return self.df
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            raise

    def get_basic_info(self) -> Dict[str, Any]:
        """
        Get basic information about the dataset.
        """
        if self.df is None:
            raise ValueError("Data not loaded. Call load_sample_data() first.")
            
        info = {
            "total_rows": len(self.df),
            "columns": list(self.df.columns),
            "dtypes": self.df.dtypes.to_dict(),
            "missing_values": self.df.isnull().sum().to_dict(),
            "memory_usage": self.df.memory_usage(deep=True).sum() / 1024**2  # in MB
        }
        
        self.logger.info("Basic information gathered")
        return info

    def analyze_numeric_columns(self) -> Dict[str, Dict[str, float]]:
        """
        Analyze numeric columns for statistical properties.
        """
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        stats = {}
        
        for col in numeric_cols:
            stats[col] = {
                "mean": self.df[col].mean(),
                "median": self.df[col].median(),
                "std": self.df[col].std(),
                "min": self.df[col].min(),
                "max": self.df[col].max(),
                "skew": self.df[col].skew(),
                "kurtosis": self.df[col].kurtosis()
            }
        
        return stats

    def analyze_datetime_columns(self) -> Dict[str, Dict[str, Any]]:
        """
        Analyze datetime columns for temporal patterns.
        """
        datetime_stats = {}
        
        # Convert pickup and dropoff columns to datetime
        self.df['pickup_datetime'] = pd.to_datetime(self.df['pickup_datetime'])
        self.df['dropoff_datetime'] = pd.to_datetime(self.df['dropoff_datetime'])
        
        for col in ['pickup_datetime', 'dropoff_datetime']:
            datetime_stats[col] = {
                "min_date": self.df[col].min(),
                "max_date": self.df[col].max(),
                "date_range_days": (self.df[col].max() - self.df[col].min()).days,
                "common_hours": self.df[col].dt.hour.value_counts().to_dict(),
                "common_days": self.df[col].dt.day_name().value_counts().to_dict()
            }
        
        return datetime_stats

    def analyze_trip_characteristics(self) -> Dict[str, Any]:
        """
        Analyze specific characteristics of taxi trips.
        """
        trip_stats = {
            "avg_trip_duration": self.df['trip_duration'].mean() / 60,  # in minutes
            "passenger_distribution": self.df['passenger_count'].value_counts().to_dict(),
            "long_trips": len(self.df[self.df['trip_duration'] > 3600]),  # > 1 hour
            "short_trips": len(self.df[self.df['trip_duration'] < 300]),  # < 5 minutes
        }
        
        return trip_stats

    def identify_outliers(self) -> Dict[str, Dict[str, int]]:
        """
        Identify outliers in numeric columns using IQR method.
        """
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        outlier_stats = {}
        
        for col in numeric_cols:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            outliers = len(self.df[
                (self.df[col] < (Q1 - 1.5 * IQR)) |
                (self.df[col] > (Q3 + 1.5 * IQR))
            ])
            
            outlier_stats[col] = {
                "total_outliers": outliers,
                "outlier_percentage": (outliers / len(self.df)) * 100
            }
        
        return outlier_stats

    def generate_exploration_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive report of the data exploration.
        """
        self.logger.info("Generating exploration report...")
        
        report = {
            "basic_info": self.get_basic_info(),
            "numeric_analysis": self.analyze_numeric_columns(),
            "datetime_analysis": self.analyze_datetime_columns(),
            "trip_characteristics": self.analyze_trip_characteristics(),
            "outlier_analysis": self.identify_outliers(),
            "report_generated_at": datetime.now().isoformat()
        }
        
        self.logger.info("Report generation completed")
        return report

def main():
    """
    Main function to run the exploration.
    """
    explorer = TaxiDataExplorer("data/train.csv")
    explorer.load_sample_data()
    report = explorer.generate_exploration_report()
    
    # Save report to file
    import json
    with open("docs/data_exploration_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)

if __name__ == "__main__":
    main()