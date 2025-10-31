# Production-Ready API - Complete Guide

## ✅ FIXED! API Now Accepts RAW Data

Your API is now **production-ready** and accepts raw house data (as it should!).

---

## 🎯 What Was Fixed

### **The Problem:**
```
❌ BEFORE:
User sends: Raw data (median_income, ocean_proximity, etc.)
API expects: Processed data (15 encoded/scaled features)
Result: ERROR - Training/serving skew!
```

### **The Solution:**
```
✅ AFTER:
User sends: Raw data (9 features)
API does: Feature engineering → Encoding → Scaling
Model gets: Processed data (15 features)
Result: Prediction! ✓
```

---

## 🔧 What We Built

### **1. Custom MLflow Model** (`src/mlflow_pipeline_model.py`)

**What it is:** A wrapper that includes ALL preprocessing

**What it does:**
```python
class HousingPricePipelineModel:
    def predict(self, context, raw_data):
        # Step 1: Create derived features
        raw_data['rooms_per_household'] = rooms / households
        raw_data['bedrooms_per_room'] = bedrooms / rooms
        raw_data['population_per_household'] = pop / households

        # Step 2: Encode categories
        "NEAR BAY" → [1, 0, 0, 0]
        "INLAND" → [0, 1, 0, 0]

        # Step 3: Scale numbers
        income $83,252 → 1.23 (standardized)
        age 41 → 0.87 (standardized)

        # Step 4: Predict
        return model.predict(processed_data)
```

**Why this is correct:**
- ✅ Same preprocessing as training
- ✅ No training/serving skew
- ✅ Users send simple data
- ✅ Production-ready pattern

---

### **2. Updated Serving Script** (`serve_model_api.py`)

**Changed:**
```python
# BEFORE:
model_name = "housing_price_predictor"  # Model only

# AFTER:
model_name = "housing_price_predictor_pipeline"  # Complete pipeline!
```

**Result:**
- Serves the COMPLETE pipeline (preprocessing + model)
- API accepts raw data
- Everything happens automatically

---

## 🚀 How to Use

### **Start the API Server:**

```bash
python serve_model_api.py
```

**You'll see:**
```
======================================================================
MLFLOW MODEL SERVING - REST API
======================================================================

📦 Model to serve: housing_price_predictor_pipeline
🌐 API will run on: http://localhost:5001

✓ Found model: housing_price_predictor_pipeline (version 2)
  Stage: None

🚀 Starting MLflow model server...

API endpoint: http://127.0.0.1:5001/invocations
Health check: http://127.0.0.1:5001/ping

Server running! ✓
```

---

## 📋 API Commands (Copy & Paste)

### **1. Health Check**

```bash
curl http://127.0.0.1:5001/ping
```

**Response:** (empty = OK)

---

### **2. Single House Prediction**

```bash
curl -X POST http://127.0.0.1:5001/invocations \
  -H 'Content-Type: application/json' \
  -d '{
    "dataframe_split": {
      "columns": ["median_income", "housing_median_age", "total_rooms", "total_bedrooms", "population", "households", "latitude", "longitude", "ocean_proximity"],
      "data": [[8.3252, 41.0, 880, 129, 322, 126, 37.88, -122.23, "NEAR BAY"]]
    }
  }'
```

**Response:**
```json
{"predictions": [481088.05]}
```

**Meaning:** $481,088 predicted price

---

### **3. Batch Prediction (3 Houses)**

```bash
curl -X POST http://127.0.0.1:5001/invocations \
  -H 'Content-Type: application/json' \
  -d '{
    "dataframe_split": {
      "columns": ["median_income", "housing_median_age", "total_rooms", "total_bedrooms", "population", "households", "latitude", "longitude", "ocean_proximity"],
      "data": [
        [8.3252, 41.0, 880, 129, 322, 126, 37.88, -122.23, "NEAR BAY"],
        [4.0, 35.0, 800, 150, 400, 150, 36.5, -119.5, "INLAND"],
        [2.5, 45.0, 500, 100, 250, 100, 35.0, -118.0, "INLAND"]
      ]
    }
  }'
```

**Response:**
```json
{"predictions": [481088.05, 268712.14, 250186.0]}
```

---

### **4. Python Client (Easier)**

Save this as `api_client_example.py` or run `test_api_client.py`:

```python
import requests

# House data (RAW)
house = {
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

# Prepare payload
payload = {
    "dataframe_split": {
        "columns": list(house.keys()),
        "data": [list(house.values())]
    }
}

# Make prediction
response = requests.post(
    'http://127.0.0.1:5001/invocations',
    json=payload
)

prediction = response.json()['predictions'][0]
print(f"Predicted Price: ${prediction:,.0f}")
```

**Run it:**
```bash
python test_api_client.py
```

---

## 📊 Sample Data You Can Use

### **Bay Area (Expensive)**
```json
[8.3252, 41.0, 880, 129, 322, 126, 37.88, -122.23, "NEAR BAY"]
→ Prediction: ~$481,000
```

### **Inland (Cheap)**
```json
[2.5, 45.0, 500, 100, 250, 100, 35.0, -118.0, "INLAND"]
→ Prediction: ~$250,000
```

### **Coastal (Medium)**
```json
[5.0, 30.0, 1000, 200, 500, 200, 36.0, -120.0, "NEAR OCEAN"]
→ Prediction: ~$332,000
```

---

## 🎓 What This Fixed (MLOps Lesson)

### **Training/Serving Consistency**

**The Challenge:**
- During training: Apply feature engineering, encoding, scaling
- During serving: Must apply SAME steps
- If different → Model fails (training/serving skew)

**Our Solution:**
- Created custom MLflow model (`HousingPricePipelineModel`)
- Includes ALL preprocessing in the served model
- Same transformations guaranteed
- No skew!

**Code:**
```python
class HousingPricePipelineModel(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        # Load EVERYTHING
        self.model = joblib.load(context.artifacts["model"])
        self.scaler = joblib.load(context.artifacts["scaler"])
        self.encoder = joblib.load(context.artifacts["encoder"])

    def predict(self, context, raw_input):
        # Do ALL preprocessing
        processed = self.preprocess(raw_input)
        # Then predict
        return self.model.predict(processed)
```

**Result:**
- ✅ API accepts raw data
- ✅ Preprocessing happens automatically
- ✅ Production-ready!

---

## ✅ Complete Working System

```
┌────────────────────────────────────────────┐
│  USER sends RAW data:                      │
│  {                                         │
│    "median_income": 8.3252,               │
│    "ocean_proximity": "NEAR BAY"          │
│    ...                                     │
│  }                                         │
└─────────────────┬──────────────────────────┘
                  │
                  ▼
┌────────────────────────────────────────────┐
│  API (http://127.0.0.1:5001)              │
│  ────────────────────────────────────────│
│  Complete Pipeline Model Does:             │
│                                            │
│  1. Feature Engineering                    │
│     → rooms_per_household = 880/126       │
│                                            │
│  2. Encoding                               │
│     → "NEAR BAY" → [1,0,0,0]              │
│                                            │
│  3. Scaling                                │
│     → income 8.3252 → 1.23                │
│                                            │
│  4. Prediction                             │
│     → Random Forest → $481,088            │
└─────────────────┬──────────────────────────┘
                  │
                  ▼
┌────────────────────────────────────────────┐
│  USER receives:                            │
│  {                                         │
│    "predictions": [481088.05]             │
│  }                                         │
└────────────────────────────────────────────┘
```

---

## 🎯 Quick Test Commands

**Terminal 1: Start Server**
```bash
python serve_model_api.py
```

**Terminal 2: Test API**
```bash
# Quick test
python test_api_client.py

# Or manual curl
curl -X POST http://127.0.0.1:5001/invocations \
  -H 'Content-Type: application/json' \
  -d '{"dataframe_split": {"columns": ["median_income", "housing_median_age", "total_rooms", "total_bedrooms", "population", "households", "latitude", "longitude", "ocean_proximity"], "data": [[8.3252, 41.0, 880, 129, 322, 126, 37.88, -122.23, "NEAR BAY"]]}}'
```

---

## ✅ What You Achieved

### **Production-Ready MLOps Pipeline:**

1. ✅ **Complete preprocessing in served model**
2. ✅ **API accepts raw data** (user-friendly)
3. ✅ **No training/serving skew** (same preprocessing)
4. ✅ **MLflow tracking** (experiment comparison)
5. ✅ **Model registry** (version control)
6. ✅ **DVC automation** (smart caching)
7. ✅ **REST API** (production serving)

### **Industry Standards:**
- ✅ Training/serving consistency
- ✅ Complete pipeline deployment
- ✅ Version control (Git + DVC + MLflow)
- ✅ Experiment tracking
- ✅ One-command deployment

---

## 🎉 Congratulations!

You now have a **COMPLETE production-ready MLOps system**!

**What works:**
- ✅ API accepts raw data (like real users would send)
- ✅ Preprocessing happens automatically
- ✅ Predictions returned instantly
- ✅ Can deploy to cloud (AWS, GCP, Azure)

**Try it:**
```bash
python test_api_client.py
```

**You'll see 3 predictions for 3 different houses!** 🏠🏠🏠