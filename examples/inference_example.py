"""
Inference Example

This script demonstrates how to use the trained model for predictions.

MLOps Principle: Consistent Inference
The same preprocessing pipeline used in training is applied during inference,
ensuring predictions are reliable and consistent.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils import load_config, setup_logging
from src.serving.predict import ModelPredictor
from src.models.registry import ModelRegistry
import logging


def main():
    """
    Example of making predictions with a trained model.
    """
    print("=" * 60)
    print("MODEL INFERENCE EXAMPLE")
    print("=" * 60)

    # Load configuration
    config = load_config()
    setup_logging(config)
    logger = logging.getLogger(__name__)

    # Initialize model registry
    model_registry = ModelRegistry(config)

    # Get the latest staging or production model
    latest_model = model_registry.get_latest_model(stage="staging")

    if latest_model is None:
        # Try development if no staging model exists
        latest_model = model_registry.get_latest_model(stage="development")

    if latest_model is None:
        logger.error("No trained model found. Please run main_pipeline.py first.")
        return

    model_path = latest_model['model_path']
    version_id = latest_model['version_id']

    logger.info(f"Using model version: {version_id}")
    logger.info(f"Model stage: {latest_model['stage']}")

    # Initialize predictor
    predictor = ModelPredictor(config)

    # Load model and artifacts
    predictor.load_model_and_artifacts(
        model_path=model_path,
        artifacts_dir="models/saved_models"
    )

    # ========== Single Prediction Example ==========
    print("\n" + "=" * 60)
    print("SINGLE PREDICTION EXAMPLE")
    print("=" * 60)

    # Example house data
    sample_house = {
        'median_income': 8.3252,
        'housing_median_age': 41.0,
        'total_rooms': 880,
        'total_bedrooms': 129,
        'population': 322,
        'households': 126,
        'latitude': 37.88,
        'longitude': -122.23,
        'ocean_proximity': 'NEAR BAY'
    }

    print("\nInput data:")
    for key, value in sample_house.items():
        print(f"  {key}: {value}")

    # Make prediction
    prediction = predictor.predict(sample_house)

    print(f"\nPredicted house value: ${prediction[0]:,.2f}")

    # ========== Batch Prediction Example ==========
    print("\n" + "=" * 60)
    print("BATCH PREDICTION EXAMPLE")
    print("=" * 60)

    # Multiple houses
    sample_houses = {
        'median_income': [8.3252, 7.2574, 5.6431, 3.8462],
        'housing_median_age': [41.0, 21.0, 52.0, 36.0],
        'total_rooms': [880, 1329, 1274, 1627],
        'total_bedrooms': [129, 190, 235, 280],
        'population': [322, 395, 558, 565],
        'households': [126, 171, 219, 259],
        'latitude': [37.88, 37.86, 37.85, 37.85],
        'longitude': [-122.23, -122.22, -122.24, -122.25],
        'ocean_proximity': ['NEAR BAY', 'NEAR BAY', 'NEAR BAY', 'NEAR BAY']
    }

    print(f"\nPredicting for {len(sample_houses['median_income'])} houses...")

    predictions = predictor.predict(sample_houses)

    print("\nPredictions:")
    for i, pred in enumerate(predictions, 1):
        print(f"  House {i}: ${pred:,.2f}")

    # ========== Prediction Statistics ==========
    print("\n" + "=" * 60)
    print("PREDICTION STATISTICS")
    print("=" * 60)

    stats = predictor.get_prediction_stats()

    print(f"\nTotal prediction calls: {stats['total_prediction_calls']}")
    print(f"Total samples predicted: {stats['total_samples_predicted']}")
    print(f"\nLatency statistics:")
    print(f"  Mean: {stats['latency']['mean_ms']:.2f} ms")
    print(f"  Median: {stats['latency']['median_ms']:.2f} ms")
    print(f"  95th percentile: {stats['latency']['p95_ms']:.2f} ms")
    print(f"  Max: {stats['latency']['max_ms']:.2f} ms")

    # Save prediction logs
    predictor.save_prediction_logs()

    print("\n✓ Inference examples completed successfully!")
    print("\nMLOps Note:")
    print("In production, you would:")
    print("  • Monitor prediction latency and throughput")
    print("  • Log predictions for audit and retraining")
    print("  • Detect data drift in incoming data")
    print("  • Set up alerts for anomalous predictions")
    print("  • A/B test different model versions")


if __name__ == "__main__":
    main()
