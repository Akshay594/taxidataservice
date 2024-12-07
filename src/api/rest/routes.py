# src/api/rest/routes.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List, Optional
from ...db.database import db
from ...db.repository import TaxiTripRepository
from . import schemas
from ...utils.helpers import calculate_distance

router = APIRouter(prefix="/api/v1")

# Dependency
def get_db():
    db_session = next(db.get_session())
    try:
        yield db_session
    finally:
        db_session.close()

@router.get("/trips/", response_model=List[schemas.TripResponse])
async def get_trips(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db_session: Session = Depends(get_db)
):
    """Get trips within a date range with pagination."""
    repo = TaxiTripRepository(db_session)
    trips = repo.get_trips_by_date_range(start_date, end_date, offset, limit)
    return trips

@router.get("/trips/{trip_id}", response_model=schemas.TripResponse)
async def get_trip(
    trip_id: int,
    db_session: Session = Depends(get_db)
):
    """Get a specific trip by ID."""
    repo = TaxiTripRepository(db_session)
    trip = repo.get_trip_by_id(trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

@router.get("/trips/nearby/", response_model=List[schemas.TripResponse])
async def get_nearby_trips(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius: float = Query(0.01, gt=0),
    limit: int = Query(100, ge=1, le=1000),
    db_session: Session = Depends(get_db)
):
    """Get trips near a specific location."""
    repo = TaxiTripRepository(db_session)
    trips = repo.get_trips_by_location(latitude, longitude, radius, limit)
    return trips

@router.get("/stats/daily/", response_model=schemas.DailyStats)
async def get_daily_statistics(
    date: date,
    db_session: Session = Depends(get_db)
):
    """Get aggregated statistics for a specific date."""
    repo = TaxiTripRepository(db_session)
    stats = repo.get_daily_stats(date)
    return stats

@router.get("/stats/hourly/", response_model=schemas.HourlyStats)
async def get_hourly_statistics(
    date: date,
    db_session: Session = Depends(get_db)
):
    """Get hourly trip counts for a specific date."""
    repo = TaxiTripRepository(db_session)
    stats = repo.get_hourly_trip_counts(date)
    return {"hourly_counts": stats}