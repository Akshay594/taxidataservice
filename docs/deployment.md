# TaxiTripDataService Deployment Guide

## Prerequisites
- Docker and Docker Compose
- PostgreSQL 13+
- Python 3.9+
- Redis
- RabbitMQ

## Development Environment

### Local Setup
1. Clone the repository:
```bash
git clone 
cd taxi-trip-data-service
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configurations
```

### Running with Docker Compose
```bash
docker-compose up --build
```

## Production Deployment

### Container Registry
1. Build the Docker image:
```bash
docker build -t taxi-trip-service:latest .
```

2. Push to container registry:
```bash
docker tag taxi-trip-service:latest your-registry/taxi-trip-service:latest
docker push your-registry/taxi-trip-service:latest
```

### Kubernetes Deployment
1. Apply database secrets:
```bash
kubectl apply -f k8s/secrets.yml
```

2. Deploy PostgreSQL:
```bash
kubectl apply -f k8s/postgres.yml
```

3. Deploy Redis and RabbitMQ:
```bash
kubectl apply -f k8s/redis.yml
kubectl apply -f k8s/rabbitmq.yml
```

4. Deploy the application:
```bash
kubectl apply -f k8s/deployment.yml
```

5. Apply service and ingress:
```bash
kubectl apply -f k8s/service.yml
kubectl apply -f k8s/ingress.yml
```

### Monitoring Setup
1. Deploy Prometheus:
```bash
kubectl apply -f monitoring/prometheus/
```

2. Deploy Grafana:
```bash
kubectl apply -f monitoring/grafana/
```

## Environment Variables

### Required Variables
```
DATABASE_URL=postgresql://user:password@localhost:5432/db
REDIS_URL=redis://localhost:6379
RABBITMQ_URL=amqp://guest:guest@localhost:5672
```

### Optional Variables
```
LOG_LEVEL=INFO
API_KEY=your-secret-key
MAX_WORKERS=4
CACHE_TTL=3600
```

## Scaling

### Horizontal Scaling
The service can be scaled horizontally by:
1. Increasing Kubernetes replicas
2. Adding more worker pods
3. Scaling the database read replicas

### Vertical Scaling
Adjust resource limits in `k8s/deployment.yml`:
```yaml
resources:
  limits:
    cpu: "2"
    memory: "4Gi"
  requests:
    cpu: "500m"
    memory: "1Gi"
```

## Backup and Recovery

### Database Backups
1. Automated daily backups:
```bash
kubectl apply -f k8s/backup-cronjob.yml
```

2. Manual backup:
```bash
kubectl exec postgres-0 -- pg_dump -U postgres taxi_trips > backup.sql
```

### Recovery
```bash
kubectl exec -i postgres-0 -- psql -U postgres taxi_trips < backup.sql
```

## Troubleshooting

### Common Issues
1. Connection Issues
```bash
kubectl logs deployment/taxi-trip-service
kubectl describe pod taxi-trip-service
```

2. Performance Issues
- Check resource usage
- Verify cache hit rates
- Monitor database performance

### Health Checks
- Application: http://localhost:8000/health
- Database: http://localhost:8000/health/db
- Cache: http://localhost:8000/health/cache