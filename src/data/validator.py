# src/data/validator.py

from datetime import datetime
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np

class TaxiDataValidator:
    """
    Validates taxi trip data based on business rules and data analysis findings.
    """
    def __init__(self):
        # NYC geographical boundaries
        self.NYC_LAT_BOUNDS = (40.4, 41.0)  # NYC latitude range
        self.NYC_LON_BOUNDS = (-74.3, -73.7)  # NYC longitude range
        
        # Time and passenger constraints
        self.MAX_TRIP_DURATION = 24 * 60 * 60  # 24 hours in seconds
        self.MIN_TRIP_DURATION = 60  # 1 minute in seconds
        self.VALID_PASSENGER_RANGE = (1, 6)
        
        # Speed constraints
        self.MAX_SPEED_MPH = 100.0  # Maximum reasonable speed in NYC
    
    def validate_coordinates(self, lat: float, lon: float) -> bool:
        """Validate if coordinates are within NYC boundaries."""
        return (self.NYC_LAT_BOUNDS[0] <= lat <= self.NYC_LAT_BOUNDS[1] and
                self.NYC_LON_BOUNDS[0] <= lon <= self.NYC_LON_BOUNDS[1])
    
    def validate_trip_duration(self, duration: int) -> bool:
        """Validate if trip duration is within reasonable bounds."""
        return self.MIN_TRIP_DURATION <= duration <= self.MAX_TRIP_DURATION
    
    def validate_passenger_count(self, count: int) -> bool:
        """Validate if passenger count is within valid range."""
        return self.VALID_PASSENGER_RANGE[0] <= count <= self.VALID_PASSENGER_RANGE[1]
    
    def validate_timestamps(self, pickup: datetime, dropoff: datetime) -> bool:
        """Validate if timestamps are logical."""
        return pickup < dropoff and pickup.year == 2016
    
    def get_validation_rules(self) -> Dict[str, Any]:
        """Return all validation rules for documentation."""
        return {
            "coordinates": {
                "latitude_range": self.NYC_LAT_BOUNDS,
                "longitude_range": self.NYC_LON_BOUNDS
            },
            "trip_duration": {
                "min_seconds": self.MIN_TRIP_DURATION,
                "max_seconds": self.MAX_TRIP_DURATION
            },
            "passengers": {
                "min_count": self.VALID_PASSENGER_RANGE[0],
                "max_count": self.VALID_PASSENGER_RANGE[1]
            },
            "speed_limit_mph": self.MAX_SPEED_MPH
        }

    def validate_dataframe(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
        """
        Validate entire DataFrame and return cleaned data with validation stats.
        """
        original_count = len(df)
        validation_stats = {"original_count": original_count}
        
        # Create copy to avoid modifying original
        df_clean = df.copy()
        
        # Validate passenger counts
        passenger_mask = df_clean['passenger_count'].apply(self.validate_passenger_count)
        validation_stats['invalid_passengers'] = (~passenger_mask).sum()
        
        # Validate trip durations
        duration_mask = df_clean['trip_duration'].apply(self.validate_trip_duration)
        validation_stats['invalid_duration'] = (~duration_mask).sum()
        
        # Validate coordinates
        pickup_coord_mask = df_clean.apply(
            lambda x: self.validate_coordinates(x['pickup_latitude'], x['pickup_longitude']),
            axis=1
        )
        dropoff_coord_mask = df_clean.apply(
            lambda x: self.validate_coordinates(x['dropoff_latitude'], x['dropoff_longitude']),
            axis=1
        )
        validation_stats['invalid_coordinates'] = (
            ~(pickup_coord_mask & dropoff_coord_mask)
        ).sum()
        
        # Combine all validations
        valid_mask = (
            passenger_mask &
            duration_mask &
            pickup_coord_mask &
            dropoff_coord_mask
        )
        
        # Apply filtering
        df_clean = df_clean[valid_mask]
        validation_stats['final_count'] = len(df_clean)
        validation_stats['total_removed'] = original_count - len(df_clean)
        
        return df_clean, validation_stats