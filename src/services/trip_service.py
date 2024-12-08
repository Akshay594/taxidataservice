# src/services/trip_service.py

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from src.db.operations import TaxiTripOperations, QueryOptimizer
from src.db.models import TaxiTrip
from src.data.processor import TaxiTripDataProcessor
from src.data.validator import TaxiDataValidator

logger = logging.getLogger(__name__)

class TripService:
    """
    Service layer for handling taxi trip business logic.
    Implements Domain-Driven Design principles.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.validator = TaxiDataValidator()
        self.processor = TaxiTripDataProcessor(config)
        
    async def process_trip_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming trip data through validation and transformation.
        """
        try:
            # Validate raw data
            if not self.validator.validate_trip_data(raw_data):
                raise ValueError("Invalid trip data")
                
            # Process and transform data
            processed_data = await self.processor.process_single_trip(raw_data)
            
            return processed_data
        except Exception as e:
            logger.error(f"Error processing trip data: {str(e)}")
            raise

    async def create_trip(self, session: Session, trip_data: Dict[str, Any]) -> TaxiTrip:
        """
        Create a new trip with validation and processing.
        """
        try:
            processed_data = await self.process_trip_data(trip_data)
            return TaxiTripOperations.create_trip(session, processed_data)
        except Exception as e:
            logger.error(f"Error creating trip: {str(e)}")
            raise

    async def get_trip_statistics(
        self,
        session: Session,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Get comprehensive trip statistics for a date range.
        """
        try:
            return await QueryOptimizer.get_trip_stats(session, start_date, end_date)
        except Exception as e:
            logger.error(f"Error getting trip statistics: {str(e)}")
            raise

    async def process_batch_trips(
        self,
        session: Session,
        trips_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process and store multiple trips in batch.
        """
        try:
            processed_trips = []
            for trip_data in trips_data:
                processed_trip = await self.process_trip_data(trip_data)
                processed_trips.append(processed_trip)
                
            result = await TaxiTripOperations.bulk_insert_trips(session, processed_trips)
            return {"processed": len(processed_trips), "success": result}
        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}")
            raise