# scripts/init_db.py

import sys
import logging
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.db.database import db
from src.config.settings import settings
from alembic.config import Config
from alembic import command

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """
    Initialize the database and run migrations.
    """
    try:
        # Create database engine and tables
        logger.info("Initializing database...")
        db.init_db()
        
        # Run Alembic migrations
        logger.info("Running database migrations...")
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
        command.upgrade(alembic_cfg, "head")
        
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

if __name__ == "__main__":
    init_database()