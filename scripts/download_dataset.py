import os
import json
import kaggle
from pathlib import Path
import zipfile
from src.config.settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_kaggle_credentials() -> bool:
    """
    Setup Kaggle credentials from environment variables.
    Returns True if successful, False otherwise.
    """
    try:
        # Check if credentials are in environment
        if not settings.KAGGLE_USERNAME or not settings.KAGGLE_KEY:
            logger.error("Kaggle credentials not found in environment variables")
            return False

        # Create .kaggle directory if it doesn't exist
        kaggle_dir = Path.home() / '.kaggle'
        kaggle_dir.mkdir(exist_ok=True)
        
        # Create credentials file
        credentials = {
            "username": settings.KAGGLE_USERNAME,
            "key": settings.KAGGLE_KEY
        }
        
        credentials_path = kaggle_dir / 'kaggle.json'
        with open(credentials_path, 'w') as f:
            json.dump(credentials, f)
        
        # Set proper permissions
        os.chmod(credentials_path, 0o600)
        
        return True
        
    except Exception as e:
        logger.error(f"Error setting up Kaggle credentials: {str(e)}")
        return False

def extract_zip_files(output_dir: str) -> dict:
    """
    Extract all zip files in the output directory.
    
    Args:
        output_dir: Directory containing zip files
        
    Returns:
        dict: Mapping of extracted file names to their paths
    """
    extracted_files = {}
    
    try:
        # List all zip files in the directory
        zip_files = [f for f in os.listdir(output_dir) if f.endswith('.zip')]
        
        for zip_file in zip_files:
            zip_path = os.path.join(output_dir, zip_file)
            logger.info(f"Extracting {zip_file}")
            
            # Extract the zip file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(output_dir)
            
            # Remove the zip file after extraction
            os.remove(zip_path)
            
            # Get the extracted file name (assuming same name without .zip)
            extracted_name = zip_file.replace('.zip', '.csv')
            extracted_path = os.path.join(output_dir, extracted_name)
            
            if os.path.exists(extracted_path):
                extracted_files[extracted_name] = extracted_path
                logger.info(f"Extracted {extracted_name}")
            
        return extracted_files
        
    except Exception as e:
        logger.error(f"Error extracting zip files: {str(e)}")
        raise

def download_dataset(output_dir: str = "data") -> dict:
    """
    Download the NYC Taxi Trip Duration dataset from Kaggle.
    
    Args:
        output_dir: Directory to save the dataset
        
    Returns:
        dict: Mapping of dataset files to their paths
    """
    try:
        # Setup credentials
        if not setup_kaggle_credentials():
            raise Exception("Failed to setup Kaggle credentials")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Set correct dataset name
        competition_name = "nyc-taxi-trip-duration"
        
        # Download dataset
        logger.info(f"Downloading competition dataset: {competition_name}")
        kaggle.api.competition_download_files(
            competition_name,
            path=output_dir,
            quiet=False
        )
        
        # Extract all zip files
        extracted_files = extract_zip_files(output_dir)
        
        if not extracted_files:
            raise FileNotFoundError("No CSV files found after extraction")
        
        logger.info("Dataset files extracted successfully:")
        for name, path in extracted_files.items():
            logger.info(f"- {name}: {path}")
        
        return extracted_files
        
    except Exception as e:
        logger.error(f"Error downloading dataset: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        data_files = download_dataset()
        logger.info("Available dataset files:")
        for name, path in data_files.items():
            logger.info(f"- {name}: {path}")
    except Exception as e:
        logger.error(f"Failed to download dataset: {str(e)}")