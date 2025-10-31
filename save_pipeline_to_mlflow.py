"""
Save Complete Pipeline to MLflow

This script creates a "pipeline model" that includes:
1. Feature engineering
2. Encoding
3. Scaling
4. Model prediction

Result: API accepts RAW data (as it should!)
"""

import sys
from pathlib import Path
import joblib
import mlflow
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from src.utils import load_config
from src.mlflow_pipeline_model import HousingPricePipelineModel, save_pipeline_model_to_mlflow
from src.models.registry import ModelRegistry

print("=" * 70)
print("SAVING COMPLETE PIPELINE TO MLFLOW")
print("=" * 70)

# Load config
config = load_config()

# Set MLflow tracking
mlflow.set_tracking_uri(config['training']['tracking_uri'])
mlflow.set_experiment(config['training']['experiment_name'])

# Get latest model from local registry
print("\n📦 Loading latest model and artifacts...")
registry = ModelRegistry(config)
latest_model = registry.get_latest_model(stage="staging")

if latest_model is None:
    latest_model = registry.get_latest_model()

if latest_model is None:
    print("✗ No model found. Train a model first:")
    print("  dvc repro")
    sys.exit(1)

print(f"✓ Found model: {latest_model['version_id']}")
print(f"  Performance: R²={latest_model['evaluation']['metrics']['r2_score']:.4f}")

# Load model and artifacts
model = joblib.load(latest_model['model_path'])
scaler = joblib.load("models/saved_models/scaler.joblib")
encoder = joblib.load("models/saved_models/encoder.joblib")
feature_names = joblib.load("models/saved_models/feature_names.joblib")

print("✓ All artifacts loaded")

# Save complete pipeline to MLflow
print("\n📦 Saving complete pipeline to MLflow...")
print("   (This includes: feature engineering + encoding + scaling + model)")

with mlflow.start_run(run_name="complete_pipeline"):
    save_pipeline_model_to_mlflow(
        model=model,
        scaler=scaler,
        encoder=encoder,
        feature_names=feature_names,
        model_name="housing_price_predictor_pipeline"
    )

    # Log metrics for reference
    mlflow.log_metrics(latest_model['evaluation']['metrics'])

print("\n✅ Complete pipeline saved to MLflow!")
print("\nModel name: housing_price_predictor_pipeline")
print("This model accepts RAW data!")

print("\n🚀 To serve it:")
print("   python serve_model_api.py")
print("   (Will automatically use the pipeline model)")

print("\n🧪 To test with RAW data:")
print('   curl -X POST http://localhost:5001/invocations \\')
print('     -H "Content-Type: application/json" \\')
print('     -d \'{"dataframe_split": {')
print('       "columns": ["median_income", "housing_median_age", "total_rooms",')
print('                   "total_bedrooms", "population", "households",')
print('                   "latitude", "longitude", "ocean_proximity"],')
print('       "data": [[8.3252, 41.0, 880, 129, 322, 126, 37.88, -122.23, "NEAR BAY"]]')
print("     }}'")
