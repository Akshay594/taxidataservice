# src/db/models.py

from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class TaxiTrip(Base):
    """
    Enhanced taxi trip model based on our data analysis.
    """
    __tablename__ = "taxi_trips"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(String)
    
    # Temporal data
    pickup_datetime = Column(DateTime, index=True)
    dropoff_datetime = Column(DateTime)
    pickup_hour = Column(Integer)
    pickup_day = Column(String)
    pickup_month = Column(Integer)
    is_rush_hour = Column(Boolean)
    is_weekend = Column(Boolean)
    time_category = Column(String)
    
    # Location data
    pickup_latitude = Column(Float)
    pickup_longitude = Column(Float)
    dropoff_latitude = Column(Float)
    dropoff_longitude = Column(Float)
    trip_distance = Column(Float)
    
    # Trip details
    passenger_count = Column(Integer)
    trip_duration = Column(Integer)  # in seconds
    average_speed = Column(Float)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TripAggregation(Base):
    """
    Pre-calculated aggregations for faster API responses.
    """
    __tablename__ = "trip_aggregations"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, index=True)
    hour = Column(Integer)
    total_trips = Column(Integer)
    average_duration = Column(Float)
    average_distance = Column(Float)
    average_passengers = Column(Float)
    total_passengers = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)