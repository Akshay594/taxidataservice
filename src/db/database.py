from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import logging

from src.config.settings import DATABASE_URL

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        
    def init_db(self):
        """Initialize database connection"""
        try:
            self.engine = create_engine(
                DATABASE_URL,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30
            )
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            logger.info("Database connection initialized successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
            
    def get_session(self):
        """Get database session"""
        if not self.SessionLocal:
            self.init_db()
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
            
    def create_tables(self):
        """Create all tables in the database"""
        from src.db.models import Base
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to create tables: {str(e)}")
            raise

# Create global database instance
db = Database()