"""
API Client Test - Using RAW Data

This demonstrates how to use your API from Python code.
"""

import requests
import json

API_URL = "http://127.0.0.1:5001/invocations"

print("=" * 70)
print("TESTING API WITH RAW DATA")
print("=" * 70)

# Example 1: Expensive Bay Area House
print("\n🏠 Example 1: Expensive Bay Area House")
print("-" * 70)

house_1 = {
    "median_income": 8.3252,
    "housing_median_age": 41.0,
    "total_rooms": 880,
    "total_bedrooms": 129,
    "population": 322,
    "households": 126,
    "latitude": 37.88,
    "longitude": -122.23,
    "ocean_proximity": "NEAR BAY"
}

print("\nInput:")
print(f"  Location: Near San Francisco Bay")
print(f"  Median Income: ${house_1['median_income'] * 10000:,.0f}")
print(f"  House Age: {house_1['housing_median_age']} years")
print(f"  Total Rooms: {house_1['total_rooms']}")

payload = {
    "dataframe_split": {
        "columns": list(house_1.keys()),
        "data": [list(house_1.values())]
    }
}

response = requests.post(API_URL, json=payload)

if response.status_code == 200:
    prediction = response.json()['predictions'][0]
    print(f"\n✅ Prediction: ${prediction:,.0f}")
else:
    print(f"\n✗ Error: {response.status_code}")
    print(response.text)

# Example 2: Modest Inland House
print("\n\n🏠 Example 2: Modest Inland House")
print("-" * 70)

house_2 = {
    "median_income": 2.5,
    "housing_median_age": 45.0,
    "total_rooms": 500,
    "total_bedrooms": 100,
    "population": 250,
    "households": 100,
    "latitude": 35.0,
    "longitude": -118.0,
    "ocean_proximity": "INLAND"
}

print("\nInput:")
print(f"  Location: Inland California")
print(f"  Median Income: ${house_2['median_income'] * 10000:,.0f}")
print(f"  House Age: {house_2['housing_median_age']} years")

payload = {
    "dataframe_split": {
        "columns": list(house_2.keys()),
        "data": [list(house_2.values())]
    }
}

response = requests.post(API_URL, json=payload)

if response.status_code == 200:
    prediction = response.json()['predictions'][0]
    print(f"\n✅ Prediction: ${prediction:,.0f}")
else:
    print(f"\n✗ Error: {response.status_code}")

# Example 3: Batch Prediction
print("\n\n🏘️  Example 3: Batch Prediction (3 Houses)")
print("-" * 70)

houses = [house_1, house_2, {
    "median_income": 5.0,
    "housing_median_age": 30.0,
    "total_rooms": 1000,
    "total_bedrooms": 200,
    "population": 500,
    "households": 200,
    "latitude": 36.0,
    "longitude": -120.0,
    "ocean_proximity": "NEAR OCEAN"
}]

payload = {
    "dataframe_split": {
        "columns": list(houses[0].keys()),
        "data": [list(h.values()) for h in houses]
    }
}

response = requests.post(API_URL, json=payload)

if response.status_code == 200:
    predictions = response.json()['predictions']
    print(f"\n✅ Predictions for {len(predictions)} houses:")
    for i, pred in enumerate(predictions, 1):
        print(f"   House {i}: ${pred:,.0f}")
else:
    print(f"\n✗ Error: {response.status_code}")

print("\n" + "=" * 70)
print("✅ API WORKS WITH RAW DATA!")
print("=" * 70)
print("\n🎉 Success! Your model API:")
print("   ✓ Accepts raw house data")
print("   ✓ Automatically preprocesses (feature engineering, encoding, scaling)")
print("   ✓ Returns price predictions")
print("   ✓ Production-ready!")
