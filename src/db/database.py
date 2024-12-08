# src/db/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator
import logging
from src.config.settings import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages database connections and sessions.
    """
    def __init__(self):
        self.engine = create_engine(
            settings.DATABASE_URL,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800  # Recycle connections after 30 minutes
        )
        
        # Create session factory
        self._session_factory = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
        )

    @contextmanager
    def get_session(self) -> Generator:
        """
        Provide a transactional scope around a series of operations.
        """
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            session.close()

    def init_db(self) -> None:
        """
        Initialize database by creating all tables.
        """
        from .models import Base
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database initialized successfully")

    def dispose(self) -> None:
        """
        Dispose of the database engine.
        """
        self.engine.dispose()
        logger.info("Database connections disposed")

# Create a global instance
db = DatabaseManager()