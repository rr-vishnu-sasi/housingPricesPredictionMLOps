"""
Pipeline Stage 1: Data Ingestion (Modified for New Data)

This version reads from a CSV file instead of fetching from scikit-learn.
Use this when you have NEW data arriving.

How to use:
1. Place new data in: data/incoming/new_housing_data.csv
2. Run: python pipeline/stage_01_ingest_data_new.py
3. Pipeline validates and processes the new data
"""

import sys
import pandas as pd
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import load_config
from src.data.ingest import DataIngestor
from src.pipeline_logger import PipelineLogger


def run_data_ingestion_from_file(input_file: str = None):
    """
    Run data ingestion from a file (for new data).

    Args:
        input_file: Path to new data CSV file

    Returns:
        bool: True if successful, False otherwise
    """
    logger = PipelineLogger(name="stage_01_ingest_new")
    logger.stage_start("Data Ingestion (New Data)")

    try:
        config = load_config()

        # Default to incoming directory if not specified
        if input_file is None:
            input_file = "data/incoming/new_housing_data.csv"

        logger.info(f"Reading new data from: {input_file}")

        # Check if file exists
        if not Path(input_file).exists():
            logger.error(f"Input file not found: {input_file}")
            logger.info("Please place new data in: data/incoming/new_housing_data.csv")
            return False

        # Read new data
        df = pd.read_csv(input_file)
        logger.data_info("Rows in new data", len(df))

        # Create data ingestor (for quality checks)
        ingestor = DataIngestor(config)

        # Perform quality checks on new data
        logger.info("Performing quality checks on new data...")
        df_cleaned, quality_report = ingestor.perform_quality_checks(df)

        # Log results
        logger.data_info("Rows after cleaning", quality_report['final_rows'])
        logger.data_info("Rows removed", quality_report['rows_removed'])

        # Save to standard locations (so rest of pipeline can use it)
        logger.info("Saving processed data...")
        ingestor.save_data(df, config['data']['raw_data_path'])
        ingestor.save_data(df_cleaned, config['data']['processed_data_path'])

        logger.info("✓ New data processed and saved!")
        logger.info("  Next: Run Stage 2 (Feature Engineering)")

        logger.stage_end("Data Ingestion (New Data)", success=True)
        return True

    except Exception as e:
        logger.error(f"Data ingestion failed: {str(e)}")
        logger.stage_end("Data Ingestion (New Data)", success=False)
        return False


if __name__ == "__main__":
    # Get input file from command line argument if provided
    input_file = sys.argv[1] if len(sys.argv) > 1 else None
    success = run_data_ingestion_from_file(input_file)
    sys.exit(0 if success else 1)
