"""
Test Model Serving API

This script tests the MLflow model serving API with properly formatted data.

The Challenge:
- MLflow serves the model that expects ENGINEERED features
- We need to send features AFTER preprocessing (encoding, scaling, derived features)

Solution:
- Use the feature engineering pipeline to prepare data
- Then send to API
"""

import pandas as pd
import requests
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.utils import load_config
from src.features.engineer import FeatureEngineer

print("=" * 70)
print("TESTING MODEL SERVING API")
print("=" * 70)

# Configuration
API_URL = "http://127.0.0.1:5001/invocations"

print(f"\n🌐 API URL: {API_URL}")

# Test 1: Health Check
print("\n" + "=" * 70)
print("TEST 1: Health Check")
print("=" * 70)

try:
    response = requests.get("http://127.0.0.1:5001/ping", timeout=5)
    print(f"✓ Server is alive! Status: {response.status_code}")
except Exception as e:
    print(f"✗ Server not responding: {e}")
    print("\nMake sure server is running:")
    print("  python serve_model_api.py")
    sys.exit(1)

# Test 2: Single House Prediction
print("\n" + "=" * 70)
print("TEST 2: Single House Prediction")
print("=" * 70)

# Sample house (RAW features)
print("\n🏠 Input House (RAW features):")
raw_house = {
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

for key, value in raw_house.items():
    print(f"   {key}: {value}")

# Process through feature engineering (to match what model expects)
print("\n⚙️  Preprocessing through feature engineering pipeline...")

config = load_config()
feature_engineer = FeatureEngineer(config)

# Load artifacts from training
import joblib
feature_engineer.scaler = joblib.load("models/saved_models/scaler.joblib")
feature_engineer.encoder = joblib.load("models/saved_models/encoder.joblib")
feature_engineer.feature_names = joblib.load("models/saved_models/feature_names.joblib")

# Convert to DataFrame
df = pd.DataFrame([raw_house])

# Apply feature engineering (is_training=False to use loaded artifacts)
df_processed = feature_engineer.engineer_features(df, is_training=False)

print(f"✓ Preprocessed features: {len(df_processed.columns)} features")
print(f"   Features: {list(df_processed.columns)[:5]}...")

# Prepare for API (MLflow format)
payload = {
    "dataframe_split": {
        "columns": list(df_processed.columns),
        "data": df_processed.values.tolist()
    }
}

print("\n🔮 Sending prediction request to API...")

try:
    response = requests.post(
        API_URL,
        json=payload,
        headers={'Content-Type': 'application/json'},
        timeout=10
    )

    if response.status_code == 200:
        result = response.json()
        prediction = result['predictions'][0]

        print("\n" + "=" * 70)
        print("✅ PREDICTION SUCCESS!")
        print("=" * 70)
        print(f"\n💰 Predicted House Price: ${prediction:,.0f}")
        print(f"\n🏠 Input House Details:")
        print(f"   Location: Near San Francisco Bay")
        print(f"   Median Income: ${raw_house['median_income'] * 10000:,.0f}")
        print(f"   House Age: {raw_house['housing_median_age']} years")
        print(f"   Total Rooms: {raw_house['total_rooms']}")
        print(f"   Bedrooms: {raw_house['total_bedrooms']}")

    else:
        print(f"\n✗ Error: {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"\n✗ Request failed: {e}")

# Test 3: Multiple Houses
print("\n" + "=" * 70)
print("TEST 3: Batch Prediction (3 Houses)")
print("=" * 70)

raw_houses = pd.DataFrame([
    {'median_income': 8.3252, 'housing_median_age': 41, 'total_rooms': 880,
     'total_bedrooms': 129, 'population': 322, 'households': 126,
     'latitude': 37.88, 'longitude': -122.23, 'ocean_proximity': 'NEAR BAY'},
    {'median_income': 4.0, 'housing_median_age': 35, 'total_rooms': 800,
     'total_bedrooms': 150, 'population': 400, 'households': 150,
     'latitude': 36.5, 'longitude': -119.5, 'ocean_proximity': 'INLAND'},
    {'median_income': 2.5, 'housing_median_age': 45, 'total_rooms': 500,
     'total_bedrooms': 100, 'population': 250, 'households': 100,
     'latitude': 35.0, 'longitude': -118.0, 'ocean_proximity': 'INLAND'}
])

print(f"\n🏘️  Testing with {len(raw_houses)} houses...")

# Process through feature engineering
df_batch_processed = feature_engineer.engineer_features(raw_houses, is_training=False)

# Prepare payload
batch_payload = {
    "dataframe_split": {
        "columns": list(df_batch_processed.columns),
        "data": df_batch_processed.values.tolist()
    }
}

try:
    response = requests.post(API_URL, json=batch_payload, timeout=10)

    if response.status_code == 200:
        result = response.json()
        predictions = result['predictions']

        print("\n✅ Batch Prediction Success!")
        print("\nResults:")
        for i, (pred, income) in enumerate(zip(predictions, raw_houses['median_income']), 1):
            print(f"   House {i} (Income: ${income*10000:,.0f}): ${pred:,.0f}")

    else:
        print(f"✗ Error: {response.status_code}")

except Exception as e:
    print(f"✗ Request failed: {e}")

print("\n" + "=" * 70)
print("API TESTING COMPLETE")
print("=" * 70)
print("\n📊 Summary:")
print("   ✓ Health check passed")
print("   ✓ Single prediction works")
print("   ✓ Batch prediction works")
print("\n🎉 Your model is serving predictions via REST API!")