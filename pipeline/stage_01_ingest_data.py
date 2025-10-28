"""
Pipeline Stage 1: Data Ingestion

This script fetches and validates data.

MLOps Pattern: Each stage is independent and can be run separately.
This allows:
- Testing individual stages
- Rerunning only failed stages
- Parallel execution where possible
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import load_config
from src.data.ingest import DataIngestor
from src.pipeline_logger import PipelineLogger


def run_data_ingestion():
    """
    Run data ingestion stage.

    What it does:
    1. Fetches California Housing dataset
    2. Validates data quality (missing values, duplicates, outliers)
    3. Saves raw and processed data
    4. Returns quality report

    Returns:
        bool: True if successful, False otherwise
    """
    # Initialize logger
    logger = PipelineLogger(name="stage_01_ingest")
    logger.stage_start("Data Ingestion")

    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = load_config()

        # Create data ingestor
        logger.info("Initializing Data Ingestor...")
        ingestor = DataIngestor(config)

        # Ingest data
        logger.info("Fetching and processing data...")
        df_cleaned, quality_report = ingestor.ingest()

        # Log results
        logger.data_info("Total rows fetched", quality_report['total_rows'])
        logger.data_info("Rows after cleaning", quality_report['final_rows'])
        logger.data_info("Rows removed", quality_report['rows_removed'])

        # Log quality checks
        for check in quality_report['checks_performed']:
            logger.info(f"Quality check performed: {check}")

        logger.stage_end("Data Ingestion", success=True)
        return True

    except Exception as e:
        logger.error(f"Data ingestion failed: {str(e)}")
        logger.stage_end("Data Ingestion", success=False)
        return False


if __name__ == "__main__":
    success = run_data_ingestion()
    sys.exit(0 if success else 1)
