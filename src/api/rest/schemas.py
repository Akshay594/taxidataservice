# src/api/rest/schemas.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Optional

class TaxiTrip(BaseModel):
    """Taxi trip response schema."""
    id: int
    vendor_id: str
    pickup_datetime: datetime
    dropoff_datetime: datetime
    passenger_count: int
    pickup_longitude: float
    pickup_latitude: float
    dropoff_longitude: float
    dropoff_latitude: float
    trip_duration: int
    distance: float
    speed: float
    estimated_fare: float
    is_weekend: bool
    is_rush_hour: bool

    class Config:
        from_attributes = True

class DailyStats(BaseModel):
    """Daily statistics response schema."""
    total_trips: int
    avg_duration: float = Field(..., description="Average trip duration in seconds")
    avg_distance: float = Field(..., description="Average trip distance in miles")
    avg_fare: float = Field(..., description="Average trip fare in USD")

class HourlyStats(BaseModel):
    """Hourly statistics response schema."""
    hourly_counts: Dict[int, int] = Field(
        ..., 
        description="Trip counts by hour (0-23)"
    )