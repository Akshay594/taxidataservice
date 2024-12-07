import pandas as pd
import logging
from pathlib import Path
import sys
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.data.processor import TaxiTripDataProcessor
from src.data.validator import TaxiDataValidator

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Main function to run the data processing pipeline"""
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # Initialize processor
        processor = TaxiTripDataProcessor()
        
        # Load data
        logger.info("Loading data...")
        data_path = project_root / "data" / "train.csv"
        df = pd.read_csv(data_path)
        logger.info(f"Loaded {len(df)} records")

        # Process data
        logger.info("Processing data...")
        processed_df = processor.process_data(df)
        
        # Save processed data
        output_path = project_root / "data" / "processed_taxi_data.csv"
        processed_df.to_csv(output_path, index=False)
        logger.info(f"Saved processed data to {output_path}")

        # Print some basic stats
        logger.info("\nProcessing Summary:")
        logger.info(f"Original records: {len(df)}")
        logger.info(f"Processed records: {len(processed_df)}")
        logger.info(f"Removed records: {len(df) - len(processed_df)}")

    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        raise

if __name__ == "__main__":
    main()