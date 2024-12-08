# TaxiTripDataService API Documentation

## Overview
This document details the REST and GraphQL APIs provided by the TaxiTripDataService.

## REST API Endpoints

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
All endpoints require an API key to be passed in the header:
```
Authorization: Bearer <your-api-key>
```

### Endpoints

#### 1. Get Trips
```http
GET /trips
```

Query Parameters:
- `start_date` (optional): Start date for filtering (YYYY-MM-DD)
- `end_date` (optional): End date for filtering (YYYY-MM-DD)
- `pickup_location` (optional): Pickup location area
- `limit` (optional): Number of results (default: 100, max: 1000)
- `offset` (optional): Pagination offset

Response:
```json
[
    {
        "id": 1,
        "vendor_id": "1",
        "pickup_datetime": "2016-01-01T00:00:00",
        "dropoff_datetime": "2016-01-01T00:15:00",
        "passenger_count": 2,
        "pickup_latitude": 40.7589,
        "pickup_longitude": -73.9851,
        "dropoff_latitude": 40.7668,
        "dropoff_longitude": -73.9831,
        "trip_duration": 900,
        "distance": 1.2,
        "average_speed": 15.5
    }
]
```

#### 2. Get Trip Statistics
```http
GET /stats/daily
```

Query Parameters:
- `date` (required): Date for statistics (YYYY-MM-DD)

Response:
```json
{
    "date": "2016-01-01",
    "total_trips": 1500,
    "average_duration": 15.5,
    "average_distance": 2.3,
    "average_passengers": 1.8,
    "peak_hour": 18,
    "total_passengers": 2700
}
```

#### 3. Get Location Statistics
```http
GET /stats/location
```

Query Parameters:
- `latitude` (required): Location latitude
- `longitude` (required): Location longitude
- `radius` (optional): Radius in kilometers (default: 1.0)

Response:
```json
{
    "location": "Manhattan",
    "total_pickups": 500,
    "total_dropoffs": 450,
    "average_trip_duration": 18.5,
    "popular_hours": [9, 17, 18],
    "average_fare": 25.50
}
```

## GraphQL API

### Endpoint
```
http://localhost:8000/graphql
```

### Queries

#### 1. Get Single Trip
```graphql
query {
    trip(id: 123) {
        id
        pickupDatetime
        dropoffDatetime
        passengerCount
        tripDuration
        distance
        averageSpeed
    }
}
```

#### 2. Get Multiple Trips
```graphql
query {
    trips(
        startDate: "2016-01-01",
        endDate: "2016-01-02",
        limit: 100
    ) {
        id
        pickupDatetime
        dropoffDatetime
        passengerCount
        tripDuration
    }
}
```

#### 3. Get Daily Statistics
```graphql
query {
    dailyStats(date: "2016-01-01") {
        totalTrips
        averageDuration
        averageDistance
        peakHour
        totalPassengers
    }
}
```

### Error Handling
Both APIs return standard HTTP status codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

Error responses include a message explaining the error:
```json
{
    "error": "Invalid date range specified",
    "details": "End date must be after start date"
}
```

## Rate Limiting
API requests are limited to:
- 100 requests per minute for authenticated users
- 10 requests per minute for unauthenticated users

## Data Caching
- Trip data is cached for 1 hour
- Statistics are cached for 15 minutes