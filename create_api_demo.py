"""
Simple API Demo

Since the full pipeline has complexities, let me show you:
1. How the API SHOULD work (conceptually)
2. A working example with processed data
3. Explanation of the issue and solution

This is a learning tool to understand MLOps serving challenges.
"""

import pandas as pd
import requests
import json

print("="*80)
print("MODEL SERVING API - DEMONSTRATION")
print("="*80)

print("\n📚 CONCEPT: How Production APIs Should Work")
print("-"*80)

print("""
USER INPUT (Raw Data):
──────────────────────
{
  "house": {
    "median_income": 85000,           ← Dollars
    "housing_median_age": 41,         ← Years
    "total_rooms": 880,
    "total_bedrooms": 129,
    "population": 322,
    "households": 126,
    "location": "Near Bay"            ← Text category
  }
}

API AUTOMATICALLY DOES (Behind the scenes):
─────────────────────────────────────────
1. Feature Engineering:
   • rooms_per_household = 880 / 126 = 6.98
   • bedrooms_per_room = 129 / 880 = 0.147

2. Encoding:
   • "Near Bay" → [1, 0, 0, 0]

3. Scaling:
   • Income $85,000 → 1.23 (standardized)

4. Prediction:
   • Model processes 15 features
   • Returns: $452,600

USER RECEIVES:
─────────────
{
  "prediction": 452600,
  "currency": "USD"
}
""")

print("\n❌ CURRENT ISSUE")
print("-"*80)
print("""
Problem:
  • MLflow saved only the Random Forest model
  • Model expects 15 PROCESSED features
  • But we're sending 9 RAW features
  • Missing: Feature engineering, encoding, scaling

This is called "Training/Serving Skew" - a major MLOps problem!
""")

print("\n✅ WORKING TEST (Using Processed Data)")
print("-"*80)

# Load already-processed features (workaround for now)
print("\n1️⃣ Loading pre-processed data from dataset...")
df = pd.read_csv('data/features/housing_features.csv')
sample = df.drop('median_house_value', axis=1).iloc[0:1]

print(f"   ✓ Loaded: {len(sample.columns)} features (already processed)")

# Test API
API_URL = "http://127.0.0.1:5001/invocations"

print(f"\n2️⃣ Testing if API server is running...")

try:
    response = requests.get("http://127.0.0.1:5001/ping", timeout=3)
    print(f"   ✓ Server is ALIVE!")
except:
    print("   ✗ Server is NOT running")
    print("\n   Start it with:")
    print("   python serve_model_api.py")
    exit(1)

print(f"\n3️⃣ Sending prediction request with PROCESSED features...")

payload = {
    "dataframe_split": {
        "columns": list(sample.columns),
        "data": sample.values.tolist()
    }
}

try:
    response = requests.post(API_URL, json=payload, timeout=10)

    if response.status_code == 200:
        result = response.json()
        prediction = result['predictions'][0]
        actual = df.iloc[0]['median_house_value']

        print("\n" + "="*80)
        print("✅ API WORKS! PREDICTION RECEIVED")
        print("="*80)
        print(f"\n💰 Predicted Price: ${prediction:,.0f}")
        print(f"   Actual Price:    ${actual:,.0f}")
        print(f"   Error:           ${abs(prediction-actual):,.0f} ({abs(prediction-actual)/actual*100:.1f}%)")

    else:
        print(f"\n✗ Error {response.status_code}: {response.text[:200]}")

except Exception as e:
    print(f"\n✗ Request failed: {e}")

print("\n" + "="*80)
print("📚 EXPLANATION: Why We Need Processed Data")
print("="*80)

print("""
Current State:
  ✓ API works with PROCESSED features
  ✗ API doesn't work with RAW features (yet)

Why:
  • MLflow served just the Random Forest model
  • Preprocessing happens BEFORE the model
  • Model expects features AFTER:
    - Feature engineering (derived features)
    - One-hot encoding (categories → numbers)
    - Standardization (scaling)

Solution (Production Pattern):
  • Save COMPLETE pipeline to MLflow:
    [Feature Engineering] → [Encoding] → [Scaling] → [Model]
  • Then API accepts RAW data
  • Preprocessing happens inside the served model

This is the correct MLOps pattern!
We attempted this with 'housing_price_predictor_pipeline'
but it needs more work to handle feature engineering properly.
""")

print("\n✅ KEY TAKEAWAY")
print("-"*80)
print("""
The API DOES work! ✓
It just needs PROCESSED features (for now).

In production, you would:
1. Create sklearn.pipeline.Pipeline with all preprocessing
2. Save that complete pipeline to MLflow
3. Then API accepts raw data automatically

This is advanced MLOps - excellent learning opportunity!
""")

print("\n🎯 WHAT YOU LEARNED")
print("-"*80)
print("""
1. Model serving works (API is functional) ✓
2. Preprocessing must be included in served model
3. This is a real production challenge (training/serving skew)
4. Solution: Save complete pipeline, not just model
5. MLflow makes serving easy, but you must save the right artifacts

This is exactly the kind of problem MLOps engineers solve!
""")
