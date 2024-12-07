import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # Project configs
    PROJECT_NAME: str = "TaxiTripDataService"
    VERSION: str = "1.0.0"
    
    # Database configs
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "taxi_trips")
    
    # Kaggle configs
    KAGGLE_USERNAME: str = os.getenv("KAGGLE_USERNAME")
    KAGGLE_KEY: str = os.getenv("KAGGLE_KEY")
    DATASET_NAME: str = "nyc-taxi-trip-duration"
    
    # Data processing configs
    CHUNK_SIZE: int = 100_000
    MAX_TRIP_DURATION: int = 24 * 60 * 60  # 24 hours in seconds
    MAX_SPEED_MPH: float = 100.0
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    def get_kaggle_config(self) -> Dict[str, Any]:
        return {
            "username": self.KAGGLE_USERNAME,
            "key": self.KAGGLE_KEY,
        }

settings = Settings()