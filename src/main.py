# src/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.graphql import GraphQLApp
from src.api.rest.routes import router as api_router
from src.api.graphql.schema import schema
from src.db.database import db
import uvicorn

app = FastAPI(
    title="TaxiTripDataService",
    description="API for NYC Taxi Trip Data Analysis",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include REST API routes
app.include_router(api_router)

# Add GraphQL endpoint
app.add_route("/graphql", GraphQLApp(schema=schema))

@app.on_event("startup")
async def startup():
    """Initialize database connection on startup."""
    db.init_db()

@app.on_event("shutdown")
async def shutdown():
    """Close database connections on shutdown."""
    db.dispose()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)