"""
MLflow Model Serving API

This script serves your trained model as a REST API using MLflow.

MLOps Benefit:
- No custom API code needed
- Automatic input validation
- Built-in model versioning
- Production-ready serving

Simple: Turn your model into a website that accepts house data and returns predictions
"""

import sys
from pathlib import Path
import subprocess

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils import load_config
import mlflow


def serve_model_mlflow_cli(model_name: str = None, port: int = 5001):
    """
    Serve model using MLflow's built-in server (CLI method).

    This uses MLflow's command-line serving which is production-ready.

    Args:
        model_name: Name of registered model (default from config)
        port: Port to serve on (default 5001, MLflow UI uses 5000)
    """
    print("=" * 70)
    print("MLFLOW MODEL SERVING - REST API")
    print("=" * 70)

    # Load config
    config = load_config()

    if model_name is None:
        # Use pipeline model that accepts RAW data
        model_name = "housing_price_predictor_pipeline"

    print(f"\n📦 Model to serve: {model_name}")
    print(f"🌐 API will run on: http://localhost:{port}")

    # Set MLflow tracking URI
    tracking_uri = config['training']['tracking_uri']
    mlflow.set_tracking_uri(tracking_uri)
    print(f"📂 MLflow tracking URI: {tracking_uri}")

    print("\n🔍 Checking for model in MLflow registry...")

    try:
        # Get latest version of the model
        client = mlflow.MlflowClient()
        versions = client.search_model_versions(f"name='{model_name}'")

        if not versions:
            print(f"\n❌ No model named '{model_name}' found in MLflow registry")
            print("\nTo register a model:")
            print("  1. Run: python pipeline/stage_03_train_model_mlflow.py")
            print("  2. Or run: dvc repro (with MLflow enabled)")
            return False

        latest_version = versions[0]
        print(f"✓ Found model: {model_name} (version {latest_version.version})")
        print(f"  Stage: {latest_version.current_stage}")
        print(f"  Run ID: {latest_version.run_id}")

        # Model URI for serving
        model_uri = f"models:/{model_name}/latest"

        print(f"\n🚀 Starting MLflow model server...")
        print(f"   Model URI: {model_uri}")
        print(f"   Port: {port}")
        print("\n⏳ Server starting (this may take a moment)...")
        print("\nOnce started:")
        print(f"  • API endpoint: http://localhost:{port}/invocations")
        print(f"  • Health check: http://localhost:{port}/ping")
        print("\nPress Ctrl+C to stop the server\n")

        # Serve using MLflow CLI
        # This is the production-ready way
        subprocess.run([
            "mlflow", "models", "serve",
            "-m", model_uri,
            "-p", str(port),
            "--no-conda"  # Use current environment
        ])

    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        return True
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def show_api_usage_examples():
    """
    Show examples of how to use the API.
    """
    print("\n" + "=" * 70)
    print("API USAGE EXAMPLES")
    print("=" * 70)

    print("\n1️⃣ Health Check (test if server is running):")
    print("""
    curl http://localhost:5001/ping
    """)

    print("\n2️⃣ Single Prediction:")
    print("""
    curl -X POST http://localhost:5001/invocations \\
      -H 'Content-Type: application/json' \\
      -d '{
        "dataframe_split": {
          "columns": ["median_income", "housing_median_age", "total_rooms",
                      "total_bedrooms", "population", "households",
                      "latitude", "longitude", "ocean_proximity"],
          "data": [[8.3252, 41.0, 880, 129, 322, 126, 37.88, -122.23, "NEAR BAY"]]
        }
      }'
    """)

    print("\n3️⃣ Batch Prediction:")
    print("""
    curl -X POST http://localhost:5001/invocations \\
      -H 'Content-Type: application/json' \\
      -d '{
        "dataframe_split": {
          "columns": ["median_income", "housing_median_age", "total_rooms",
                      "total_bedrooms", "population", "households",
                      "latitude", "longitude", "ocean_proximity"],
          "data": [
            [8.3252, 41.0, 880, 129, 322, 126, 37.88, -122.23, "NEAR BAY"],
            [7.2574, 52.0, 1274, 235, 558, 219, 37.85, -122.24, "NEAR BAY"],
            [3.8462, 52.0, 1627, 280, 565, 259, 37.85, -122.25, "NEAR BAY"]
          ]
        }
      }'
    """)

    print("\n4️⃣ Python Code Example:")
    print("""
    import requests
    import pandas as pd

    # Prepare data
    house = {
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

    # Make request
    response = requests.post(
        'http://localhost:5001/invocations',
        json={'dataframe_split': {
            'columns': list(house.keys()),
            'data': [list(house.values())]
        }}
    )

    prediction = response.json()['predictions'][0]
    print(f"Predicted price: ${prediction:,.0f}")
    """)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--examples":
        show_api_usage_examples()
    else:
        serve_model_mlflow_cli()
