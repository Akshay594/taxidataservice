# TaxiTripDataService Setup Guide

## Project Overview
TaxiTripDataService is a microservice that processes NYC taxi trip data, providing both REST and GraphQL APIs for data analysis.

## Installation Steps

### 1. Initial Setup

#### Clone the Repository
```bash
git clone
cd taxi-trip-data-service
```

#### Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configuration

#### Environment Variables
Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` with your configurations:
```env
# Database
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=taxi_trips
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@localhost:5672

# API
API_KEY=your_secret_key
MAX_WORKERS=4

# Kaggle
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_key
```

### 3. Database Setup

#### Using Docker
```bash
docker-compose up -d db
```

#### Manual Setup
1. Install PostgreSQL
2. Create database:
```bash
createdb taxi_trips
```

3. Run migrations:
```bash
python scripts/init_db.py
```

### 4. Data Processing

#### Download Dataset
```bash
python scripts/download_dataset.py
```

#### Process Data
```bash
python scripts/process_data.py
```

### 5. Running the Service

#### Using Docker Compose
```bash
docker-compose up --build
```

#### Manual Run
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 6. Verify Installation

#### Check API Status
```bash
curl http://localhost:8000/health
```

#### Test Endpoints
```bash
# REST API
curl http://localhost:8000/api/v1/trips/

# GraphQL
curl -X POST http://localhost:8000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ trips { id pickupDatetime } }"}'
```

## Development Setup

### Code Quality Tools
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Check code style
black .
flake8 .
```

### Pre-commit Hooks
```bash
pre-commit install
```

### Database Migrations
```bash
# Create new migration
alembic revision -m "description"

# Run migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Monitoring

### Logging
Logs are written to:
- Console (development)
- JSON files (production)
- Configured logging service

### Metrics
Access metrics at:
- http://localhost:8000/metrics (Prometheus)
- http://localhost:3000 (Grafana)

## Security

### API Authentication
Add API key to requests:
```bash
curl -H "Authorization: Bearer your-api-key" http://localhost:8000/api/v1/trips/
```

### Database Security
- Use strong passwords
- Enable SSL connections
- Restrict network access

## Maintenance

### Backup Database
```bash
pg_dump -U postgres taxi_trips > backup.sql
```

### Update Dependencies
```bash
pip-compile requirements.in
pip-compile requirements-dev.in
pip install -r requirements.txt
```

### Clean Up
```bash
# Remove cached data
redis-cli FLUSHALL

# Clean Docker
docker-compose down -v
```

## Support
- GitHub Issues: Report bugs and feature requests
- Documentation: Check `docs/` directory
- Logs: Check application logs for troubleshooting