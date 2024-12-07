# src/api/graphql/schema.py

import strawberry
from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session
from ...db.repository import TaxiTripRepository
from fastapi import Depends
from ...db.database import get_db

@strawberry.type
class TaxiTrip:
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

@strawberry.type
class DailyStats:
    total_trips: int
    avg_duration: float
    avg_distance: float
    avg_fare: float

@strawberry.type
class Query:
    @strawberry.field
    def trip(self, trip_id: int, db: Session = Depends(get_db)) -> Optional[TaxiTrip]:
        repo = TaxiTripRepository(db)
        return repo.get_trip_by_id(trip_id)

    @strawberry.field
    def trips(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        offset: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
    ) -> List[TaxiTrip]:
        repo = TaxiTripRepository(db)
        return repo.get_trips_by_date_range(start_date, end_date, offset, limit)

    @strawberry.field
    def trips_near_location(
        self,
        latitude: float,
        longitude: float,
        radius: float = 0.01,
        limit: int = 100,
        db: Session = Depends(get_db)
    ) -> List[TaxiTrip]:
        repo = TaxiTripRepository(db)
        return repo.get_trips_by_location(latitude, longitude, radius, limit)

    @strawberry.field
    def daily_stats(
        self,
        stats_date: date,
        db: Session = Depends(get_db)
    ) -> DailyStats:
        repo = TaxiTripRepository(db)
        return repo.get_daily_stats(stats_date)

schema = strawberry.Schema(query=Query)