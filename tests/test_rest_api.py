# tests/test_rest_api.py

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from src.main import app
from src.db.database import db

# Create test client
client = TestClient(app)

@pytest.fixture
def sample_trip_data():
    return {
        "vendor_id": "1",
        "pickup_datetime": "2016-01-01T00:00:00",
        "dropoff_datetime": "2016-01-01T00:30:00",
        "passenger_count": 2,
        "pickup_latitude": 40.7589,
        "pickup_longitude": -73.9851,
        "dropoff_latitude": 40.7668,
        "dropoff_longitude": -73.9831,
        "trip_duration": 1800
    }

@pytest.fixture
def test_client():
    return client

class TestTripEndpoints:
    def test_get_trips(self, test_client):
        """Test getting list of trips."""
        response = test_client.get("/api/v1/trips/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "id" in data[0]
            assert "pickup_datetime" in data[0]

    def test_get_trips_with_date_filter(self, test_client):
        """Test getting trips with date filter."""
        params = {
            "start_date": "2016-01-01",
            "end_date": "2016-01-02"
        }
        response = test_client.get("/api/v1/trips/", params=params)
        assert response.status_code == 200
        data = response.json()
        if len(data) > 0:
            trip_date = datetime.fromisoformat(data[0]["pickup_datetime"].replace("Z", ""))
            assert trip_date >= datetime(2016, 1, 1)
            assert trip_date < datetime(2016, 1, 3)

    def test_get_trip_by_id(self, test_client, sample_trip_data):
        """Test getting a specific trip by ID."""
        # First create a trip
        create_response = test_client.post("/api/v1/trips/", json=sample_trip_data)
        assert create_response.status_code == 200
        trip_id = create_response.json()["id"]

        # Then get it by ID
        response = test_client.get(f"/api/v1/trips/{trip_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == trip_id
        assert data["passenger_count"] == sample_trip_data["passenger_count"]

    def test_get_invalid_trip_id(self, test_client):
        """Test getting a trip with invalid ID."""
        response = test_client.get("/api/v1/trips/999999")
        assert response.status_code == 404

    def test_create_trip(self, test_client, sample_trip_data):
        """Test creating a new trip."""
        response = test_client.post("/api/v1/trips/", json=sample_trip_data)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["passenger_count"] == sample_trip_data["passenger_count"]

    def test_create_invalid_trip(self, test_client):
        """Test creating a trip with invalid data."""
        invalid_data = {
            "vendor_id": "1",
            "pickup_datetime": "invalid-date"  # Invalid date format
        }
        response = test_client.post("/api/v1/trips/", json=invalid_data)
        assert response.status_code == 422

class TestStatisticsEndpoints:
    def test_get_daily_stats(self, test_client):
        """Test getting daily statistics."""
        params = {"date": "2016-01-01"}
        response = test_client.get("/api/v1/stats/daily/", params=params)
        assert response.status_code == 200
        data = response.json()
        assert "total_trips" in data
        assert "average_duration" in data
        assert "average_distance" in data

    def test_get_location_stats(self, test_client):
        """Test getting location-based statistics."""
        params = {
            "latitude": 40.7589,
            "longitude": -73.9851,
            "radius": 1.0
        }
        response = test_client.get("/api/v1/stats/location/", params=params)
        assert response.status_code == 200
        data = response.json()
        assert "total_pickups" in data
        assert "popular_hours" in data

    def test_get_stats_invalid_date(self, test_client):
        """Test getting stats with invalid date."""
        params = {"date": "invalid-date"}
        response = test_client.get("/api/v1/stats/daily/", params=params)
        assert response.status_code == 422

class TestErrorHandling:
    def test_invalid_date_format(self, test_client):
        """Test error handling for invalid date format."""
        params = {"date": "invalid-date"}
        response = test_client.get("/api/v1/stats/daily/", params=params)
        assert response.status_code == 422

    def test_future_date(self, test_client):
        """Test error handling for future date."""
        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        params = {"date": future_date}
        response = test_client.get("/api/v1/stats/daily/", params=params)
        assert response.status_code == 400

    def test_invalid_coordinates(self, test_client):
        """Test error handling for invalid coordinates."""
        params = {
            "latitude": 200,  # Invalid latitude
            "longitude": -73.9851
        }
        response = test_client.get("/api/v1/stats/location/", params=params)
        assert response.status_code == 422