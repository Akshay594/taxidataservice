# src/db/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from ..config.settings import settings
import logging

# Initialize logging
logger = logging.getLogger(__name__)

# Create declarative base instance
Base = declarative_base()

class Database:
    """Database connection and session management."""
    
    def __init__(self):
        self.engine = create_engine(
            settings.DATABASE_URL,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,  # Recycle connections after 30 minutes
            echo=False  # Set to True for SQL query logging
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def create_tables(self):
        """Create all tables in the database."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            raise

    def get_session(self):
        """Get a database session."""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

# Create database instance
db = Database()