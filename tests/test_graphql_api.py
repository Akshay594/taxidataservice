# tests/test_graphql_api.py

import pytest
from fastapi.testclient import TestClient
from graphene.test import Client as GrapheneClient
from datetime import datetime
from src.main import app
from src.api.graphql.schema import schema
from src.db.database import db

# Create test clients
rest_client = TestClient(app)

@pytest.fixture
def graphql_client():
    return GrapheneClient(schema)

@pytest.fixture
def rest_client():
    return TestClient(app)

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

class TestGraphQLQueries:
    def test_get_trip(self, graphql_client, rest_client, sample_trip_data):
        """Test querying a single trip."""
        query = """
        query GetTrip($tripId: Int!) {
            trip(id: $tripId) {
                id
                pickupDatetime
                dropoffDatetime
                passengerCount
                tripDuration
            }
        }
        """
        
        # First create a trip using REST API to get an ID
        response = rest_client.post("/api/v1/trips/", json=sample_trip_data)
        trip_id = response.json()["id"]
        
        # Then query it through GraphQL
        result = graphql_client.execute(query, variables={"tripId": trip_id})
        assert "errors" not in result
        assert result["data"]["trip"]["id"] == str(trip_id)
        assert result["data"]["trip"]["passengerCount"] == sample_trip_data["passenger_count"]

    def test_get_trips(self, graphql_client):
        """Test querying multiple trips."""
        query = """
        query GetTrips($startDate: DateTime, $endDate: DateTime, $limit: Int) {
            trips(startDate: $startDate, endDate: $endDate, limit: $limit) {
                id
                pickupDatetime
                dropoffDatetime
                passengerCount
            }
        }
        """
        
        variables = {
            "startDate": "2016-01-01T00:00:00",
            "endDate": "2016-01-02T00:00:00",
            "limit": 5
        }
        
        result = graphql_client.execute(query, variables=variables)
        assert "errors" not in result
        assert isinstance(result["data"]["trips"], list)
        if len(result["data"]["trips"]) > 0:
            assert "id" in result["data"]["trips"][0]

    def test_get_daily_stats(self, graphql_client):
        """Test querying daily statistics."""
        query = """
        query GetDailyStats($date: Date!) {
            dailyStats(date: $date) {
                totalTrips
                averageDuration
                averageDistance
                peakHour
            }
        }
        """
        
        variables = {
            "date": "2016-01-01"
        }
        
        result = graphql_client.execute(query, variables=variables)
        assert "errors" not in result
        assert "totalTrips" in result["data"]["dailyStats"]

    def test_get_trips_with_filters(self, graphql_client):
        """Test querying trips with multiple filters."""
        query = """
        query GetFilteredTrips(
            $startDate: DateTime,
            $endDate: DateTime,
            $passengerCount: Int,
            $limit: Int
        ) {
            trips(
                startDate: $startDate,
                endDate: $endDate,
                passengerCount: $passengerCount,
                limit: $limit
            ) {
                id
                pickupDatetime
                passengerCount
            }
        }
        """
        
        variables = {
            "startDate": "2016-01-01T00:00:00",
            "endDate": "2016-01-02T00:00:00",
            "passengerCount": 2,
            "limit": 5
        }
        
        result = graphql_client.execute(query, variables=variables)
        assert "errors" not in result
        for trip in result["data"]["trips"]:
            assert trip["passengerCount"] == 2

class TestGraphQLErrorHandling:
    def test_invalid_trip_id(self, graphql_client):
        """Test error handling for invalid trip ID."""
        query = """
        query {
            trip(id: 999999) {
                id
            }
        }
        """
        
        result = graphql_client.execute(query)
        assert "errors" in result

    def test_invalid_date_format(self, graphql_client):
        """Test error handling for invalid date format."""
        query = """
        query {
            dailyStats(date: "invalid-date") {
                totalTrips
            }
        }
        """
        
        result = graphql_client.execute(query)
        assert "errors" in result

    def test_missing_required_arguments(self, graphql_client):
        """Test error handling for missing required arguments."""
        query = """
        query {
            trip {
                id
            }
        }
        """
        
        result = graphql_client.execute(query)
        assert "errors" in result
        assert "Required argument" in result["errors"][0]["message"]

class TestGraphQLValidation:
    def test_required_fields(self, graphql_client):
        """Test validation for required fields."""
        query = """
        query GetTrip {
            trip {
                id
            }
        }
        """
        
        result = graphql_client.execute(query)
        assert "errors" in result
        assert "Required argument" in result["errors"][0]["message"]

    def test_field_type_validation(self, graphql_client):
        """Test validation for field types."""
        query = """
        query {
            trip(id: "invalid-id") {
                id
            }
        }
        """
        
        result = graphql_client.execute(query)
        assert "errors" in result

    def test_max_limit_validation(self, graphql_client):
        """Test validation for maximum limit on trips query."""
        query = """
        query {
            trips(limit: 1001) {
                id
            }
        }
        """
        
        result = graphql_client.execute(query)
        assert "errors" in result