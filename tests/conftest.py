# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base
from src.db.database import DatabaseManager
from src.main import app
from fastapi.testclient import TestClient

@pytest.fixture(scope="session")
def test_db():
    # Create test database
    engine = create_engine("postgresql://test_user:test_password@localhost:5432/test_db")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    
    yield TestingSessionLocal()
    
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client

# tests/test_api.py
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

def test_get_trips(test_client):
    response = test_client.get("/api/v1/trips/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_trip_stats(test_client):
    date = datetime.now().date()
    response = test_client.get(f"/api/v1/stats/daily/?date={date}")
    assert response.status_code == 200
    assert "total_trips" in response.json()

# tests/test_data_processor.py
from src.data.processor import TaxiTripDataProcessor
import pandas as pd

def test_process_data():
    processor = TaxiTripDataProcessor({})
    test_data = pd.DataFrame({
        "pickup_datetime": ["2016-01-01 00:00:00"],
        "dropoff_datetime": ["2016-01-01 00:30:00"],
        "passenger_count": [2],
        "pickup_longitude": [-73.974],
        "pickup_latitude": [40.752],
        "dropoff_longitude": [-73.984],
        "dropoff_latitude": [40.742],
    })
    
    processed_data, stats = processor.process_data(test_data)
    assert not processed_data.empty
    assert "trip_distance" in processed_data.columns

# tests/test_service.py
from src.services.trip_service import TripService
import pytest

@pytest.mark.asyncio
async def test_process_trip_data():
    service = TripService({})
    test_data = {
        "pickup_datetime": "2016-01-01 00:00:00",
        "dropoff_datetime": "2016-01-01 00:30:00",
        "passenger_count": 2,
        "pickup_longitude": -73.974,
        "pickup_latitude": 40.752,
        "dropoff_longitude": -73.984,
        "dropoff_latitude": 40.742,
    }
    
    processed_data = await service.process_trip_data(test_data)
    assert processed_data is not None
    assert "trip_distance" in processed_data