# src/api/rest/schemas.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class TripBase(BaseModel):
    vendor_id: str
    pickup_datetime: datetime
    dropoff_datetime: datetime
    passenger_count: int
    pickup_latitude: float
    pickup_longitude: float
    dropoff_latitude: float
    dropoff_longitude: float
    trip_duration: int

class TripCreate(TripBase):
    pass

class TripUpdate(BaseModel):
    passenger_count: Optional[int] = None
    trip_duration: Optional[int] = None

class TripResponse(TripBase):
    id: int
    distance: float
    average_speed: float
    is_rush_hour: bool
    time_category: str
    created_at: datetime
    
    class Config:
        orm_mode = True

class TripStats(BaseModel):
    date: datetime
    total_trips: int
    average_duration: float
    average_distance: float
    average_passengers: float
    peak_hour: int
    total_passengers: int

class LocationStats(BaseModel):
    location: str
    total_pickups: int
    total_dropoffs: int
    average_trip_duration: float
    popular_hours: List[int]
    average_fare: float

class DateRangeParams(BaseModel):
    start_date: datetime
    end_date: datetime