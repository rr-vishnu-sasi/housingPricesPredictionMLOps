"""
Pipeline Stage 2: Feature Engineering

This script transforms raw data into features for ML.

MLOps Critical: Feature transformations must be:
- Reproducible (same input = same output)
- Versioned (track which features are used)
- Saved (artifacts needed for inference)
"""

import sys
import pandas as pd
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import load_config
from src.features.engineer import FeatureEngineer
from src.pipeline_logger import PipelineLogger


def run_feature_engineering():
    """
    Run feature engineering stage.

    What it does:
    1. Loads processed data from stage 1
    2. Creates derived features (rooms per household, etc.)
    3. Encodes categorical features
    4. Scales numerical features
    5. Saves feature engineering artifacts

    Returns:
        bool: True if successful, False otherwise
    """
    # Initialize logger
    logger = PipelineLogger(name="stage_02_features")
    logger.stage_start("Feature Engineering")

    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = load_config()

        # Load processed data from stage 1
        logger.info("Loading processed data...")
        processed_data_path = config['data']['processed_data_path']
        df = pd.read_csv(processed_data_path)
        logger.data_info("Rows loaded", len(df))

        # Create feature engineer
        logger.info("Initializing Feature Engineer...")
        feature_engineer = FeatureEngineer(config)

        # Engineer features
        logger.info("Engineering features...")
        df_features = feature_engineer.engineer_features(df, is_training=True)

        # Save artifacts
        logger.info("Saving feature engineering artifacts...")
        feature_engineer.save_artifacts()

        # Save featured data
        features_path = config['data']['features_data_path']
        df_features.to_csv(features_path, index=False)
        logger.data_info("Features created", len(df_features.columns) - 1)  # Exclude target
        logger.info(f"Featured data saved to: {features_path}")

        logger.stage_end("Feature Engineering", success=True)
        return True

    except Exception as e:
        logger.error(f"Feature engineering failed: {str(e)}")
        logger.stage_end("Feature Engineering", success=False)
        return False


if __name__ == "__main__":
    success = run_feature_engineering()
    sys.exit(0 if success else 1)
