# src/api/rest/routes.py

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from ...db.database import db
from ...db.repository import TaxiTripRepository
from . import schemas
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/v1/taxi", tags=["taxi"])

# Dependency to get database session
def get_db():
    db_session = next(db.get_session())
    try:
        yield db_session
    finally:
        db_session.close()

@router.get("/trips/", response_model=List[schemas.TaxiTrip])
async def get_trips(
    start_date: Optional[datetime] = Query(None, description="Start date for trip range"),
    end_date: Optional[datetime] = Query(None, description="End date for trip range"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db)
):
    """Get taxi trips within a date range with pagination."""
    repo = TaxiTripRepository(db)
    trips = repo.get_trips_by_date_range(start_date, end_date, offset, limit)
    return trips

@router.get("/trips/{trip_id}", response_model=schemas.TaxiTrip)
async def get_trip(trip_id: int, db: Session = Depends(get_db)):
    """Get a specific taxi trip by ID."""
    repo = TaxiTripRepository(db)
    trip = repo.get_trip_by_id(trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

@router.get("/trips/location/", response_model=List[schemas.TaxiTrip])
async def get_trips_by_location(
    latitude: float = Query(..., description="Pickup latitude"),
    longitude: float = Query(..., description="Pickup longitude"),
    radius: float = Query(0.01, description="Search radius in degrees"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get taxi trips near a specific location."""
    repo = TaxiTripRepository(db)
    trips = repo.get_trips_by_location(latitude, longitude, radius, limit)
    return trips

@router.get("/stats/daily/", response_model=schemas.DailyStats)
async def get_daily_stats(
    date: date = Query(..., description="Date for statistics"),
    db: Session = Depends(get_db)
):
    """Get aggregated statistics for a specific date."""
    repo = TaxiTripRepository(db)
    stats = repo.get_daily_stats(date)
    return stats

@router.get("/stats/hourly/", response_model=schemas.HourlyStats)
async def get_hourly_stats(
    date: date = Query(..., description="Date for hourly statistics"),
    db: Session = Depends(get_db)
):
    """Get hourly trip counts for a specific date."""
    repo = TaxiTripRepository(db)
    stats = repo.get_hourly_trip_counts(date)
    return {"hourly_counts": stats}