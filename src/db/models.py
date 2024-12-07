# src/db/models.py

from sqlalchemy import (
    Column, Integer, Float, String, DateTime, Boolean,
    Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.sql import func
from .database import Base

class TaxiTrip(Base):
    """Taxi trip data model with optimized indexing and constraints."""
    
    __tablename__ = "taxi_trips"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Raw data fields
    vendor_id = Column(String(10), nullable=False)
    pickup_datetime = Column(DateTime(timezone=True), nullable=False)
    dropoff_datetime = Column(DateTime(timezone=True), nullable=False)
    passenger_count = Column(Integer, nullable=False)
    pickup_longitude = Column(Float, nullable=False)
    pickup_latitude = Column(Float, nullable=False)
    dropoff_longitude = Column(Float, nullable=False)
    dropoff_latitude = Column(Float, nullable=False)
    trip_duration = Column(Integer, nullable=False)  # in seconds
    
    # Derived features
    distance = Column(Float, nullable=False)
    speed = Column(Float, nullable=False)
    pickup_hour = Column(Integer, nullable=False)
    pickup_day = Column(String(10), nullable=False)
    pickup_month = Column(Integer, nullable=False)
    is_weekend = Column(Boolean, nullable=False)
    is_rush_hour = Column(Boolean, nullable=False)
    estimated_fare = Column(Float, nullable=False)
    
    # Metadata
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Constraints
    __table_args__ = (
        # Check constraints
        CheckConstraint('passenger_count BETWEEN 1 AND 6', name='valid_passenger_count'),
        CheckConstraint('trip_duration > 0', name='positive_duration'),
        CheckConstraint('distance > 0', name='positive_distance'),
        CheckConstraint('speed >= 0', name='non_negative_speed'),
        CheckConstraint('pickup_hour BETWEEN 0 AND 23', name='valid_hour'),
        CheckConstraint('pickup_month BETWEEN 1 AND 12', name='valid_month'),
        CheckConstraint('estimated_fare >= 0', name='non_negative_fare'),
        
        # Indexes for common queries
        Index('ix_taxi_trips_pickup_datetime', 'pickup_datetime'),
        Index('ix_taxi_trips_dropoff_datetime', 'dropoff_datetime'),
        Index('ix_taxi_trips_pickup_location', 'pickup_latitude', 'pickup_longitude'),
        Index('ix_taxi_trips_dropoff_location', 'dropoff_latitude', 'dropoff_longitude'),
        Index('ix_taxi_trips_trip_stats', 'trip_duration', 'distance', 'speed'),
        Index('ix_taxi_trips_temporal', 'pickup_hour', 'pickup_day', 'pickup_month'),
    )