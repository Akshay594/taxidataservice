# src/db/operations.py

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import pandas as pd
from sqlalchemy import text, func, and_
from sqlalchemy.orm import Session
from .models import TaxiTrip, TripAggregation
import logging
from geopy.distance import geodesic

logger = logging.getLogger(__name__)

class TaxiTripOperations:
    """
    Handles CRUD operations and bulk data management for taxi trips.
    """

    @staticmethod
    def bulk_insert_trips(session: Session, trips_data: List[Dict[str, Any]]) -> int:
        """
        Efficiently insert multiple trip records.
        
        Args:
            session: Database session
            trips_data: List of trip dictionaries
            
        Returns:
            Number of records inserted
        """
        try:
            session.bulk_insert_mappings(TaxiTrip, trips_data)
            return len(trips_data)
        except Exception as e:
            logger.error(f"Bulk insert failed: {str(e)}")
            session.rollback()
            raise

    @staticmethod
    def create_trip(session: Session, trip_data: Dict[str, Any]) -> TaxiTrip:
        """
        Create a single trip record.
        """
        try:
            trip = TaxiTrip(**trip_data)
            session.add(trip)
            session.flush()
            return trip
        except Exception as e:
            logger.error(f"Create trip failed: {str(e)}")
            session.rollback()
            raise

    @staticmethod
    def update_trip(session: Session, trip_id: int, trip_data: Dict[str, Any]) -> Optional[TaxiTrip]:
        """
        Update an existing trip record.
        """
        try:
            trip = session.query(TaxiTrip).filter(TaxiTrip.id == trip_id).first()
            if trip:
                for key, value in trip_data.items():
                    setattr(trip, key, value)
                session.flush()
            return trip
        except Exception as e:
            logger.error(f"Update trip failed: {str(e)}")
            session.rollback()
            raise

    @staticmethod
    def delete_trip(session: Session, trip_id: int) -> bool:
        """
        Delete a trip record.
        """
        try:
            trip = session.query(TaxiTrip).filter(TaxiTrip.id == trip_id).first()
            if trip:
                session.delete(trip)
                session.flush()
                return True
            return False
        except Exception as e:
            logger.error(f"Delete trip failed: {str(e)}")
            session.rollback()
            raise

    @staticmethod
    def get_trip_by_id(session: Session, trip_id: int) -> Optional[TaxiTrip]:
        """
        Retrieve a single trip by ID.
        """
        try:
            return session.query(TaxiTrip).filter(TaxiTrip.id == trip_id).first()
        except Exception as e:
            logger.error(f"Get trip failed: {str(e)}")
            raise

class QueryOptimizer:
    """
    Optimizes and handles complex queries for trip data analysis.
    """

    @staticmethod
    def get_trips_by_timeframe(
        session: Session,
        start_time: datetime,
        end_time: datetime,
        limit: int = 1000
    ) -> List[TaxiTrip]:
        """
        Get trips within a specific timeframe.
        """
        try:
            return session.query(TaxiTrip)\
                .filter(
                    and_(
                        TaxiTrip.pickup_datetime >= start_time,
                        TaxiTrip.pickup_datetime <= end_time
                    )
                )\
                .limit(limit)\
                .all()
        except Exception as e:
            logger.error(f"Timeframe query failed: {str(e)}")
            raise

    @staticmethod
    def get_trips_by_location(
        session: Session,
        latitude: float,
        longitude: float,
        radius_km: float = 1.0,
        limit: int = 100
    ) -> List[TaxiTrip]:
        """
        Get trips starting or ending near a location.
        """
        try:
            # Convert radius to approximate degrees
            radius_deg = radius_km / 111.32  # rough approximation

            return session.query(TaxiTrip)\
                .filter(
                    or_(
                        and_(
                            TaxiTrip.pickup_latitude.between(latitude - radius_deg, latitude + radius_deg),
                            TaxiTrip.pickup_longitude.between(longitude - radius_deg, longitude + radius_deg)
                        ),
                        and_(
                            TaxiTrip.dropoff_latitude.between(latitude - radius_deg, latitude + radius_deg),
                            TaxiTrip.dropoff_longitude.between(longitude - radius_deg, longitude + radius_deg)
                        )
                    )
                )\
                .limit(limit)\
                .all()
        except Exception as e:
            logger.error(f"Location query failed: {str(e)}")
            raise

    @staticmethod
    def get_daily_statistics(session: Session, date: datetime) -> Dict[str, Any]:
        """
        Get aggregated statistics for a specific date.
        """
        try:
            stats = session.query(
                func.count(TaxiTrip.id).label('total_trips'),
                func.avg(TaxiTrip.trip_duration).label('avg_duration'),
                func.avg(TaxiTrip.distance).label('avg_distance'),
                func.avg(TaxiTrip.passenger_count).label('avg_passengers'),
                func.sum(TaxiTrip.passenger_count).label('total_passengers')
            ).filter(
                func.date(TaxiTrip.pickup_datetime) == date.date()
            ).first()

            # Get peak hours
            peak_hours = session.query(
                func.extract('hour', TaxiTrip.pickup_datetime).label('hour'),
                func.count(TaxiTrip.id).label('count')
            ).filter(
                func.date(TaxiTrip.pickup_datetime) == date.date()
            ).group_by('hour')\
            .order_by(text('count DESC'))\
            .first()

            return {
                'date': date,
                'total_trips': stats.total_trips,
                'average_duration': float(stats.avg_duration) if stats.avg_duration else 0,
                'average_distance': float(stats.avg_distance) if stats.avg_distance else 0,
                'average_passengers': float(stats.avg_passengers) if stats.avg_passengers else 0,
                'total_passengers': stats.total_passengers,
                'peak_hour': peak_hours.hour if peak_hours else None
            }
        except Exception as e:
            logger.error(f"Daily statistics query failed: {str(e)}")
            raise

    @staticmethod
    async def analyze_trip_patterns(
        session: Session,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Analyze trip patterns for a date range.
        """
        try:
            # Get hourly distribution
            hourly_dist = session.query(
                func.extract('hour', TaxiTrip.pickup_datetime).label('hour'),
                func.count(TaxiTrip.id).label('count')
            ).filter(
                and_(
                    TaxiTrip.pickup_datetime >= start_date,
                    TaxiTrip.pickup_datetime <= end_date
                )
            ).group_by('hour')\
            .order_by('hour')\
            .all()

            # Get passenger distribution
            passenger_dist = session.query(
                TaxiTrip.passenger_count,
                func.count(TaxiTrip.id).label('count')
            ).filter(
                and_(
                    TaxiTrip.pickup_datetime >= start_date,
                    TaxiTrip.pickup_datetime <= end_date
                )
            ).group_by(TaxiTrip.passenger_count)\
            .order_by(TaxiTrip.passenger_count)\
            .all()

            return {
                'hourly_distribution': {h.hour: h.count for h in hourly_dist},
                'passenger_distribution': {p.passenger_count: p.count for p in passenger_dist},
                'date_range': {
                    'start': start_date,
                    'end': end_date
                }
            }
        except Exception as e:
            logger.error(f"Pattern analysis failed: {str(e)}")
            raise

    @staticmethod
    def update_aggregation_table(session: Session, date: datetime) -> None:
        """
        Update the trip aggregation table for a specific date.
        """
        try:
            # Delete existing aggregation for the date
            session.query(TripAggregation)\
                .filter(func.date(TripAggregation.date) == date.date())\
                .delete()

            # Create new aggregation
            aggregation = TripAggregation(
                date=date,
                **QueryOptimizer.get_daily_statistics(session, date)
            )
            session.add(aggregation)
            session.flush()
        except Exception as e:
            logger.error(f"Aggregation update failed: {str(e)}")
            session.rollback()
            raise