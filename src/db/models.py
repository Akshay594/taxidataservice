from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TaxiTrip(Base):
    __tablename__ = "taxi_trips"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(String)
    pickup_datetime = Column(DateTime)
    dropoff_datetime = Column(DateTime)
    passenger_count = Column(Integer)
    pickup_longitude = Column(Float)
    pickup_latitude = Column(Float)
    dropoff_longitude = Column(Float)
    dropoff_latitude = Column(Float)
    trip_duration = Column(Integer)  # in seconds
    
    # Derived features
    distance = Column(Float)
    speed = Column(Float)
    pickup_hour = Column(Integer)
    pickup_day = Column(String)
    pickup_month = Column(Integer)
    is_weekend = Column(Boolean)
    is_rush_hour = Column(Boolean)
    estimated_fare = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    class Config:
        orm_mode = True