# src/main.py

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.api.rest.routes import router as api_router
from src.api.graphql.schema import schema
from src.db.database import db
from src.queue.queue_handler import QueueHandler
from src.cache.cache_manager import CacheManager
from src.services.trip_service import TripService
from src.config.settings import settings
import uvicorn

# Create service instances
queue_handler = QueueHandler()
cache_manager = CacheManager()
trip_service = TripService(settings.dict())

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await queue_handler.connect()
    await cache_manager.connect()
    db.init_db()
    
    yield
    
    # Shutdown
    await queue_handler.close()
    await cache_manager.close()
    db.dispose()

app = FastAPI(
    title="TaxiTripDataService",
    description="Scalable microservice for NYC Taxi Trip Data Analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register message handlers
@app.on_event("startup")
async def setup_handlers():
    await queue_handler.register_handler(
        "trip.created",
        trip_service.process_trip_data
    )
    await queue_handler.register_handler(
        "trip.batch",
        trip_service.process_batch_trips
    )

# Include routers
app.include_router(api_router)
app.mount("/graphql", schema)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        workers=settings.WORKERS
    )