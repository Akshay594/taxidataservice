# src/data/processor.py

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Tuple
from .validator import TaxiDataValidator
import logging
from math import radians, sin, cos, sqrt, atan2

class TaxiTripDataProcessor:
    """
    Processes taxi trip data with enhanced features based on data analysis.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.validator = TaxiDataValidator()
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        logger = logging.getLogger('TaxiTripDataProcessor')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula."""
        R = 6371  # Earth's radius in kilometers

        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = R * c

        return distance * 0.621371  # Convert to miles

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create new features based on our data analysis insights.
        """
        df = df.copy()
        
        # Convert timestamps
        df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'])
        df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'])
        
        # Time-based features
        df['pickup_hour'] = df['pickup_datetime'].dt.hour
        df['pickup_day'] = df['pickup_datetime'].dt.day_name()
        df['pickup_month'] = df['pickup_datetime'].dt.month
        df['pickup_dayofweek'] = df['pickup_datetime'].dt.dayofweek
        
        # Rush hour feature (based on our analysis)
        rush_hours_morning = (df['pickup_hour'].isin([7, 8, 9]))
        rush_hours_evening = (df['pickup_hour'].isin([17, 18, 19]))
        df['is_rush_hour'] = rush_hours_morning | rush_hours_evening
        
        # Weekend feature
        df['is_weekend'] = df['pickup_dayofweek'].isin([5, 6])
        
        # Calculate trip distance
        df['trip_distance'] = df.apply(
            lambda row: self.calculate_distance(
                row['pickup_latitude'], row['pickup_longitude'],
                row['dropoff_latitude'], row['dropoff_longitude']
            ),
            axis=1
        )
        
        # Calculate speed (mph)
        df['average_speed'] = df['trip_distance'] / (df['trip_duration'] / 3600)
        
        # Time of day categories
        df['time_category'] = pd.cut(
            df['pickup_hour'],
            bins=[-1, 6, 12, 18, 23],
            labels=['Night', 'Morning', 'Afternoon', 'Evening']
        )
        
        return df

    def process_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Process the data with validation and feature engineering.
        """
        self.logger.info("Starting data processing")
        
        # Validate data
        df_clean, validation_stats = self.validator.validate_dataframe(df)
        self.logger.info(f"Validation removed {validation_stats['total_removed']} records")
        
        # Engineer features
        df_processed = self.engineer_features(df_clean)
        self.logger.info("Feature engineering completed")
        
        processing_stats = {
            **validation_stats,
            "features_added": [
                "pickup_hour", "pickup_day", "pickup_month",
                "is_rush_hour", "is_weekend", "trip_distance",
                "average_speed", "time_category"
            ]
        }
        
        return df_processed, processing_stats