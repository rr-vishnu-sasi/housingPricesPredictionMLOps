"""
Simple Prediction Script

This demonstrates how to use your trained model to predict house prices.
"""

import pandas as pd
import joblib
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils import load_config
from src.models.registry import ModelRegistry

print("=" * 70)
print("HOUSING PRICE PREDICTION - SIMPLE DEMO")
print("=" * 70)

# Load configuration
config = load_config()

# Get the latest model from registry
print("\n📦 Loading trained model...")
registry = ModelRegistry(config)
latest_model = registry.get_latest_model(stage="staging")

if latest_model is None:
    latest_model = registry.get_latest_model(stage="development")

if latest_model is None:
    print("❌ No trained model found. Please run: python main_pipeline.py")
    sys.exit(1)

model_path = latest_model['model_path']
print(f"✓ Loaded model: {latest_model['version_id']}")
print(f"  Stage: {latest_model['stage']}")
print(f"  Accuracy (R²): {latest_model['evaluation']['metrics']['r2_score']:.2%}")

# Load model and preprocessing artifacts
model = joblib.load(model_path)
scaler = joblib.load("models/saved_models/scaler.joblib")
encoder = joblib.load("models/saved_models/encoder.joblib")
feature_names = joblib.load("models/saved_models/feature_names.joblib")

print(f"✓ Loaded preprocessing artifacts")

# ========== SINGLE HOUSE PREDICTION ==========
print("\n" + "=" * 70)
print("EXAMPLE 1: SINGLE HOUSE PREDICTION")
print("=" * 70)

# Example house near San Francisco Bay
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

print("\n🏠 Input House Details:")
print(f"   Location: Near San Francisco Bay")
print(f"   Median Income: ${sample_house['median_income'] * 10000:,.0f}")
print(f"   House Age: {sample_house['housing_median_age']} years")
print(f"   Total Rooms: {sample_house['total_rooms']}")
print(f"   Bedrooms: {sample_house['total_bedrooms']}")
print(f"   Population: {sample_house['population']}")
print(f"   Households: {sample_house['households']}")

# Convert to DataFrame
df = pd.DataFrame([sample_house])

# Feature Engineering (same as training)
print("\n⚙️  Applying feature engineering...")

# 1. Create derived features
df['rooms_per_household'] = df['total_rooms'] / df['households']
df['bedrooms_per_room'] = df['total_bedrooms'] / df['total_rooms']
df['population_per_household'] = df['population'] / df['households']

# 2. Encode categorical
ocean_encoded = encoder.transform(df[['ocean_proximity']])
ocean_feature_names = encoder.get_feature_names_out(['ocean_proximity'])
for i, name in enumerate(ocean_feature_names):
    df[name] = ocean_encoded[:, i]

# Remove original categorical column
df = df.drop('ocean_proximity', axis=1)

# 3. Scale numerical features
numerical_cols = [col for col in df.columns]
df[numerical_cols] = scaler.transform(df[numerical_cols])

# Ensure correct feature order
df = df[feature_names]

# 4. Make prediction
print("🔮 Making prediction...")
prediction = model.predict(df)[0]

print(f"\n💰 PREDICTED HOUSE VALUE: ${prediction:,.0f}")
print(f"   (Based on your 82% accurate model)")

# ========== MULTIPLE HOUSES PREDICTION ==========
print("\n" + "=" * 70)
print("EXAMPLE 2: MULTIPLE HOUSES PREDICTION")
print("=" * 70)

# Different types of houses
houses = [
    {
        'name': 'Expensive Bay Area Home',
        'median_income': 10.0,
        'housing_median_age': 25.0,
        'total_rooms': 2000,
        'total_bedrooms': 400,
        'population': 1000,
        'households': 400,
        'latitude': 37.88,
        'longitude': -122.23,
        'ocean_proximity': 'NEAR BAY'
    },
    {
        'name': 'Average Inland Home',
        'median_income': 4.0,
        'housing_median_age': 35.0,
        'total_rooms': 800,
        'total_bedrooms': 150,
        'population': 400,
        'households': 150,
        'latitude': 36.5,
        'longitude': -119.5,
        'ocean_proximity': 'INLAND'
    },
    {
        'name': 'Modest Rural Home',
        'median_income': 2.5,
        'housing_median_age': 45.0,
        'total_rooms': 500,
        'total_bedrooms': 100,
        'population': 250,
        'households': 100,
        'latitude': 35.0,
        'longitude': -118.0,
        'ocean_proximity': 'INLAND'
    }
]

print("\n🏘️  Predicting prices for 3 different houses:\n")

for i, house in enumerate(houses, 1):
    # Extract name
    house_name = house.pop('name')

    # Convert to DataFrame
    df = pd.DataFrame([house])

    # Feature engineering
    df['rooms_per_household'] = df['total_rooms'] / df['households']
    df['bedrooms_per_room'] = df['total_bedrooms'] / df['total_rooms']
    df['population_per_household'] = df['population'] / df['households']

    # Encode
    ocean_encoded = encoder.transform(df[['ocean_proximity']])
    for j, name in enumerate(ocean_feature_names):
        df[name] = ocean_encoded[:, j]
    df = df.drop('ocean_proximity', axis=1)

    # Scale
    df[numerical_cols] = scaler.transform(df[numerical_cols])
    df = df[feature_names]

    # Predict
    prediction = model.predict(df)[0]

    print(f"{i}. {house_name}")
    print(f"   Income: ${house['median_income'] * 10000:,.0f} | "
          f"Age: {house['housing_median_age']:.0f}yr | "
          f"Location: {house['ocean_proximity']}")
    print(f"   → Predicted Value: ${prediction:,.0f}\n")

# ========== SUMMARY ==========
print("=" * 70)
print("✅ PREDICTIONS COMPLETED!")
print("=" * 70)

print("\n📊 Your Model Stats:")
print(f"   • Model Type: {latest_model['metadata']['model_type']}")
print(f"   • Trained on: {latest_model['metadata']['training_samples']:,} houses")
print(f"   • Accuracy (R²): {latest_model['evaluation']['metrics']['r2_score']:.2%}")
print(f"   • Average Error: ${latest_model['evaluation']['metrics']['mae']:,.0f}")

print("\n💡 MLOps Note:")
print("   This prediction used the SAME preprocessing (scaler, encoder)")
print("   as during training - preventing training/serving skew!")

print("\n🎯 Next Steps:")
print("   • Try your own house values!")
print("   • Run: python examples/model_comparison_example.py")
print("   • Experiment with different models in config/config.yaml")
