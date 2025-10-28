"""
Quick Dataset Preview

This script shows you what the California Housing dataset looks like
before running the full pipeline.
"""

from sklearn.datasets import fetch_california_housing
import pandas as pd

print("=" * 70)
print("CALIFORNIA HOUSING DATASET - PREVIEW")
print("=" * 70)

# Fetch dataset
print("\n📥 Fetching dataset from scikit-learn...")
housing_data = fetch_california_housing(as_frame=True)
df = housing_data.frame

# Rename for clarity (same as in the pipeline)
df.rename(columns={
    'MedInc': 'median_income',
    'HouseAge': 'housing_median_age',
    'AveRooms': 'avg_rooms',
    'AveBedrms': 'avg_bedrooms',
    'Population': 'population',
    'AveOccup': 'avg_occupancy',
    'Latitude': 'latitude',
    'Longitude': 'longitude',
    'MedHouseVal': 'median_house_value'
}, inplace=True)

# Convert to actual prices (multiply by 100,000)
df['median_house_value'] = df['median_house_value'] * 100000

print(f"✓ Dataset loaded successfully!")
print(f"\n📊 Dataset Statistics:")
print(f"   Total houses: {len(df):,}")
print(f"   Features: {len(df.columns) - 1} (excluding target)")
print(f"   Target variable: median_house_value")

print(f"\n📋 Features:")
for i, col in enumerate(df.columns, 1):
    print(f"   {i}. {col}")

print(f"\n💰 Price Range:")
print(f"   Minimum: ${df['median_house_value'].min():,.0f}")
print(f"   Maximum: ${df['median_house_value'].max():,.0f}")
print(f"   Average: ${df['median_house_value'].mean():,.0f}")
print(f"   Median: ${df['median_house_value'].median():,.0f}")

print(f"\n🏠 Sample Houses (first 5):")
print("=" * 70)
print(df.head().to_string())

print(f"\n📈 Statistical Summary:")
print("=" * 70)
print(df.describe())

print(f"\n✅ This is the dataset your ML model will learn from!")
print(f"\nTo run the full pipeline and train a model:")
print(f"   python main_pipeline.py")
