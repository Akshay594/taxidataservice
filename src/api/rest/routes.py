# src/api/rest/routes.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from src.db.database import db
from src.db.operations import TaxiTripOperations, QueryOptimizer
from .schemas import (
    TripResponse, 
    TripCreate,
    TripUpdate,
    TripStats,
    LocationStats,
    DateRangeParams
)

router = APIRouter(prefix="/api/v1")

# Dependency to get database session
def get_db():
    with db.get_session() as session:
        yield session

@router.get("/trips/", response_model=List[TripResponse])
async def get_trips(
    start_date: date = Query(None, description="Start date for trip filter"),
    end_date: date = Query(None, description="End date for trip filter"),
    pickup_location: Optional[str] = Query(None, description="Pickup location area"),
    limit: int = Query(100, le=1000),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    """
    Retrieve taxi trips based on date range and location filters.
    """
    try:
        trips = QueryOptimizer.get_trips_by_timeframe(
            db,
            start_date,
            end_date,
            limit=limit
        )
        return trips
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trips/{trip_id}", response_model=TripResponse)
async def get_trip(
    trip_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific trip by ID.
    """
    trip = TaxiTripOperations.get_trip_by_id(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

@router.get("/stats/daily/", response_model=TripStats)
async def get_daily_stats(
    date: date = Query(..., description="Date for statistics"),
    db: Session = Depends(get_db)
):
    """
    Get aggregated statistics for a specific date.
    """
    stats = QueryOptimizer.get_daily_statistics(db, date)
    if not stats:
        raise HTTPException(status_code=404, detail="No data found for this date")
    return stats

@router.get("/stats/location/", response_model=LocationStats)
async def get_location_stats(
    latitude: float = Query(..., description="Location latitude"),
    longitude: float = Query(..., description="Location longitude"),
    radius: float = Query(1.0, description="Radius in kilometers"),
    db: Session = Depends(get_db)
):
    """
    Get statistics for trips around a specific location.
    """
    # Implementation of location-based statistics
    pass

@router.post("/trips/", response_model=TripResponse)
async def create_trip(
    trip: TripCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new trip record.
    """
    return TaxiTripOperations.create_trip(db, trip.dict())

@router.put("/trips/{trip_id}", response_model=TripResponse)
async def update_trip(
    trip_id: int,
    trip: TripUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing trip record.
    """
    updated_trip = TaxiTripOperations.update_trip(db, trip_id, trip.dict())
    if not updated_trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return updated_trip