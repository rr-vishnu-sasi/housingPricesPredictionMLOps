```markdown
# MLflow Integration Guide - Simple Explanation

## 🎯 What is MLflow?

**Simple Answer:** MLflow is like a **lab notebook + version control + deployment tool** for ML models.

Think of it as:
- **Experiment Tracker** - Google Docs for your ML experiments
- **Model Registry** - App Store for your ML models
- **Model Server** - Website that serves your model predictions

---

## 🚀 Quick Start (3 Steps)

### **Step 1: Train a Model with MLflow**
```bash
# Run DVC pipeline (now includes MLflow tracking)
dvc repro
```

### **Step 2: View in MLflow UI**
```bash
# Start MLflow UI
mlflow ui

# Open browser: http://localhost:5000
```

### **Step 3: Serve Model as API**
```bash
# Serve your best model
python serve_model_api.py
```

---

## 📊 Complete Workflow (Simple Explanation)

### **Scenario:** You're training multiple models to find the best one

```
┌──────────────────────────────────────────┐
│  STEP 1: Train Model with MLflow         │
│  Command: dvc repro                      │
├──────────────────────────────────────────┤
│  What happens:                           │
│  • Trains Random Forest (150 trees)      │
│  • MLflow tracks:                        │
│    - Parameters: n_estimators=150        │
│    - Metrics: RMSE=$48,677, R²=81.92%    │
│    - Model: Saved in MLflow registry     │
│  • Creates Run ID: abc123                │
└─────────────────┬────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────┐
│  STEP 2: View in MLflow UI               │
│  Command: mlflow ui                      │
├──────────────────────────────────────────┤
│  What you see:                           │
│  📊 Dashboard showing:                   │
│    • All experiments in a table          │
│    • Parameters (100 trees vs 150)       │
│    • Metrics (R² scores compared)        │
│    • Charts (automatic visualization)    │
│  🔍 Can sort by: R², RMSE, date, etc.    │
└─────────────────┬────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────┐
│  STEP 3: Register Best Model             │
│  (Automatically done in Step 1!)         │
├──────────────────────────────────────────┤
│  Model Registry shows:                   │
│  • Model: housing_price_predictor        │
│  • Version 1: R²=81.88% (100 trees)      │
│  • Version 2: R²=81.92% (150 trees) ★    │
│  • Version 3: R²=80.50% (50 trees)       │
└─────────────────┬────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────┐
│  STEP 4: Serve as REST API               │
│  Command: python serve_model_api.py      │
├──────────────────────────────────────────┤
│  Creates API endpoint:                   │
│  http://localhost:5001/invocations       │
│                                          │
│  Send house data → Get price prediction  │
└──────────────────────────────────────────┘
```

---

## 🎓 MLflow Components Explained

### **1. Experiment Tracking**

**Simple:** Records every model you train

**What gets tracked:**
```
Experiment: housing_price_prediction
├─ Run 1: random_forest_100_trees
│  ├─ Parameters: n_estimators=100, max_depth=20
│  ├─ Metrics: RMSE=$48,726, R²=81.88%
│  └─ Model: Saved ✓
│
├─ Run 2: random_forest_150_trees
│  ├─ Parameters: n_estimators=150, max_depth=20
│  ├─ Metrics: RMSE=$48,677, R²=81.92% ← Better!
│  └─ Model: Saved ✓
│
└─ Run 3: random_forest_200_trees
   ├─ Parameters: n_estimators=200, max_depth=20
   ├─ Metrics: RMSE=$48,500, R²=82.10% ← Best!
   └─ Model: Saved ✓
```

**Why useful:**
- Compare all experiments in one view
- Know what works and what doesn't
- Never lose track of experiments

---

### **2. Model Registry**

**Simple:** Version control for your ML models (like Git for code)

**What it stores:**
```
Model Name: housing_price_predictor

Versions:
├─ Version 1 (Oct 25, 11:00 AM)
│  ├─ R² Score: 81.88%
│  ├─ Stage: Development
│  └─ Tags: baseline
│
├─ Version 2 (Oct 29, 8:55 AM)
│  ├─ R² Score: 81.92%
│  ├─ Stage: Staging
│  └─ Tags: improved
│
└─ Version 3 (Oct 29, 10:00 AM)
   ├─ R² Score: 82.10%
   ├─ Stage: Production ← Currently serving
   └─ Tags: champion
```

**Lifecycle:**
```
Development → Staging → Production → Archived
```

---

### **3. Model Serving**

**Simple:** Turn your model into a website (REST API)

**Before MLflow:**
- Write custom Flask/FastAPI code
- Handle input validation manually
- Manage model loading
- Deal with errors

**With MLflow:**
- One command: `mlflow models serve`
- Auto input validation
- Auto model loading
- Production-ready

---

## 🚀 Let's Use MLflow! (Step-by-Step)

### **PART 1: Train Models and Track in MLflow**

Run the pipeline with MLflow tracking:

```bash
dvc repro
```

**What happens:**
1. ✅ Trains model
2. ✅ Logs to MLflow:
   - Parameters (n_estimators, max_depth, etc.)
   - Metrics (RMSE, R², MAE, MAPE)
   - Model (saved in MLflow)
3. ✅ Registers in MLflow Model Registry

---

### **PART 2: View in MLflow UI**

Start the MLflow UI:

```bash
mlflow ui
```

**Output:**
```
[INFO] Starting gunicorn 23.0.0
[INFO] Listening at: http://127.0.0.1:5000
```

**Then:**
1. Open browser: http://localhost:5000
2. You'll see MLflow dashboard with:
   - ✅ All experiments
   - ✅ All runs
   - ✅ Parameters and metrics
   - ✅ Charts for comparison

**What you can do in UI:**
- 📊 Compare models side-by-side
- 📈 See metric trends
- 🔍 Search and filter experiments
- 📥 Download models
- 🏷️ Add tags and notes

---

### **PART 3: Compare Multiple Models**

Let's train 3 different models and compare:

**Experiment 1: Baseline (100 trees)**
```bash
# Edit config: n_estimators: 100
dvc repro
# Result: R² = 81.88%
```

**Experiment 2: More trees (150 trees)**
```bash
# Edit config: n_estimators: 150
dvc repro
# Result: R² = 81.92%
```

**Experiment 3: Even more (200 trees)**
```bash
# Edit config: n_estimators: 200
dvc repro
# Result: R² = 82.10%
```

**View comparison:**
```bash
mlflow ui
# Click "Experiments" → See all 3 runs in a table
# Sort by R² score → Best model on top!
```

---

### **PART 4: Register Best Model**

**Good news:** Already done automatically!

When you run the pipeline, models are auto-registered in MLflow Model Registry with name: `housing_price_predictor`

**Check registered models:**
```bash
mlflow models list
```

**Or in UI:**
- Click "Models" tab
- See: housing_price_predictor
- See all versions with metrics

---

### **PART 5: Serve Model as REST API**

Serve your best model:

```bash
python serve_model_api.py
```

**Output:**
```
======================================================================
MLFLOW MODEL SERVING - REST API
======================================================================

📦 Model to serve: housing_price_predictor
🌐 API will run on: http://localhost:5001

✓ Found model: housing_price_predictor (version 3)
  Stage: Production

🚀 Starting MLflow model server...

API endpoint: http://localhost:5001/invocations
Health check: http://localhost:5001/ping

Server started! ✓
```

**Test the API:**

```bash
# Terminal 1: Server running
python serve_model_api.py

# Terminal 2: Make prediction
curl -X POST http://localhost:5001/invocations \
  -H 'Content-Type: application/json' \
  -d '{
    "dataframe_split": {
      "columns": ["median_income", "housing_median_age", "total_rooms",
                  "total_bedrooms", "population", "households",
                  "latitude", "longitude", "ocean_proximity"],
      "data": [[8.3252, 41.0, 880, 129, 322, 126, 37.88, -122.23, "NEAR BAY"]]
    }
  }'

# Response:
# {"predictions": [452600.0]}
```

---

## 📊 MLflow UI Walkthrough

### **Experiments Tab:**
```
┌────────────────────────────────────────────────────────┐
│  Experiments                                           │
├────────────────────────────────────────────────────────┤
│  Name: housing_price_prediction                        │
│  Runs: 3                                               │
│                                                        │
│  Run Name              │ RMSE    │ R²     │ Trees     │
│  ─────────────────────────────────────────────────────│
│  random_forest_200     │ 48,500  │ 82.10% │ 200  ★   │
│  random_forest_150     │ 48,677  │ 81.92% │ 150      │
│  random_forest_100     │ 48,726  │ 81.88% │ 100      │
│                                                        │
│  [Compare Selected] [Download] [Delete]                │
└────────────────────────────────────────────────────────┘
```

### **Compare View:**
```
Click 2+ runs → Click "Compare"

┌────────────────────────────────────────────────────────┐
│  Parallel Coordinates Chart                            │
│  (Visual comparison of parameters & metrics)           │
│                                                        │
│  Parameters:                                           │
│  n_estimators: 100 ──────── 150 ──────── 200          │
│  max_depth:    20  ──────── 20  ──────── 20           │
│                                                        │
│  Metrics:                                              │
│  R²:           0.8188 ─── 0.8192 ─── 0.8210           │
│  RMSE:         48,726 ─── 48,677 ─── 48,500           │
└────────────────────────────────────────────────────────┘
```

### **Models Tab:**
```
┌────────────────────────────────────────────────────────┐
│  Registered Models                                     │
├────────────────────────────────────────────────────────┤
│  Name: housing_price_predictor                         │
│  Latest Version: 3                                     │
│                                                        │
│  Version │ Stage      │ R²     │ Created              │
│  ──────────────────────────────────────────────────── │
│  3       │ Production │ 82.10% │ Oct 29, 10:00 AM  ★  │
│  2       │ Staging    │ 81.92% │ Oct 29, 8:55 AM      │
│  1       │ None       │ 81.88% │ Oct 25, 11:00 AM     │
│                                                        │
│  [Transition Stage] [Download] [Delete]                │
└────────────────────────────────────────────────────────┘
```

---

## 💡 Simple Examples

### **Example 1: Compare 3 Models**

```bash
# Train model 1
# Edit config: n_estimators: 100
dvc repro

# Train model 2
# Edit config: n_estimators: 150
dvc repro

# Train model 3
# Edit config: n_estimators: 200
dvc repro

# View comparison
mlflow ui
# Open: http://localhost:5000
# Click: Experiments → Select all 3 → Compare
# See: Which performed best!
```

**Result in UI:**
```
Model Comparison Table:
┌─────────────────────────────────────────────┐
│ Run          │ Trees │ RMSE    │ R²       │
├─────────────────────────────────────────────┤
│ Run 1        │ 100   │ $48,726 │ 81.88%   │
│ Run 2        │ 150   │ $48,677 │ 81.92%   │
│ Run 3 ★      │ 200   │ $48,500 │ 82.10%   │ ← Best!
└─────────────────────────────────────────────┘
```

---

### **Example 2: Register and Serve Best Model**

```bash
# 1. Model is auto-registered during training
dvc repro
# MLflow saves it as: housing_price_predictor (version 3)

# 2. View in registry
mlflow ui
# Click "Models" → See housing_price_predictor

# 3. Serve it
python serve_model_api.py
# API running at: http://localhost:5001
```

**Make prediction:**
```bash
curl -X POST http://localhost:5001/invocations \
  -H 'Content-Type: application/json' \
  -d '{"dataframe_split": {
    "columns": ["median_income", "housing_median_age", ...],
    "data": [[8.3252, 41.0, 880, 129, 322, 126, 37.88, -122.23, "NEAR BAY"]]
  }}'

# Response:
# {"predictions": [452600.0]}
# → Predicted price: $452,600
```

---

## 🔍 What Each File Does

### **src/mlflow_tracker.py**
**Purpose:** Wrapper for MLflow functions
**Simple:** Makes MLflow easier to use

**Functions:**
```python
start_run()     # Start tracking experiment
log_params()    # Record settings (n_estimators, etc.)
log_metrics()   # Record results (RMSE, R², etc.)
log_model()     # Save model to MLflow
end_run()       # Stop tracking
```

### **pipeline/stage_03_train_model_mlflow.py**
**Purpose:** Training script with MLflow integration
**Simple:** Same training but now tracks everything to MLflow

**What it logs:**
- All hyperparameters
- All metrics
- Trained model
- Feature importance
- Evaluation report

### **serve_model_api.py**
**Purpose:** Serves model as REST API
**Simple:** Turns model into a website

**API endpoints:**
- `GET /ping` - Check if server is alive
- `POST /invocations` - Make predictions

---

## 📖 Common Commands

### **Training & Tracking:**
```bash
# Train with MLflow tracking
dvc repro

# Train single stage
python pipeline/stage_03_train_model_mlflow.py
```

### **Viewing Experiments:**
```bash
# Start UI
mlflow ui

# UI on custom port
mlflow ui --port 8080

# View in browser
http://localhost:5000
```

### **Model Registry:**
```bash
# List registered models
mlflow models list

# List specific model versions
mlflow models list --name housing_price_predictor
```

### **Model Serving:**
```bash
# Serve latest model
python serve_model_api.py

# Or use MLflow CLI directly
mlflow models serve -m "models:/housing_price_predictor/latest" -p 5001
```

---

## 🎯 Real-World Workflow

**Monday: Baseline Model**
```bash
$ dvc repro
✓ Model trained: R²=81.88%
✓ Logged to MLflow
✓ Registered as v1
```

**Tuesday: Optimization**
```bash
# Try 150 trees
$ edit config.yaml
$ dvc repro
✓ Model trained: R²=81.92%
✓ Logged to MLflow
✓ Registered as v2

# Compare in UI
$ mlflow ui
→ See v2 is better than v1!
```

**Wednesday: More experiments**
```bash
# Try different algorithms
$ edit config: type: "gradient_boosting"
$ dvc repro
✓ Model trained: R²=82.50%
✓ Logged to MLflow
✓ Registered as v3

# Compare all models
$ mlflow ui
→ Gradient Boosting wins!
```

**Thursday: Deploy to Production**
```bash
# Promote best model in MLflow UI
# Click v3 → Transition to "Production"

# Serve it
$ python serve_model_api.py
✓ Serving v3 (production)
✓ API at http://localhost:5001
```

---

## 🎓 Key MLOps Concepts

### **1. Experiment Tracking**

**Problem without MLflow:**
```
# You train 10 models
# Results scattered in notebooks, logs, files
# Hard to remember: "Which hyperparameters gave R²=82%?"
# No easy way to compare
```

**Solution with MLflow:**
```
# All 10 experiments in one dashboard
# Click to compare
# See exactly what worked
# Reproducible (can rerun any experiment)
```

---

### **2. Model Versioning**

**Problem without MLflow:**
```
models/
├─ model_final.joblib (which final?)
├─ model_final_v2.joblib (v2 of what?)
├─ model_really_final.joblib (is it though?)
└─ model_use_this_one.joblib (which version?)
```

**Solution with MLflow:**
```
Model: housing_price_predictor
├─ Version 1: Baseline
├─ Version 2: Optimized
├─ Version 3: Production ← Clear versioning!
```

---

### **3. Model Serving**

**Problem without MLflow:**
```python
# Custom API code (100+ lines)
@app.post("/predict")
def predict(data: dict):
    # Load model
    # Validate input
    # Preprocess
    # Predict
    # Handle errors
    # Return response
```

**Solution with MLflow:**
```bash
# One command (0 lines of custom code!)
mlflow models serve -m "models:/housing_price_predictor/latest"
```

---

## 📊 Where Everything is Stored

### **MLflow Data:**
```
logs/mlruns/              ← MLflow tracking data
├─ 0/                     ← Experiment ID
│  ├─ abc123/            ← Run ID
│  │  ├─ metrics/        ← RMSE, R², etc.
│  │  ├─ params/         ← Hyperparameters
│  │  ├─ artifacts/      ← Saved models
│  │  └─ meta.yaml       ← Metadata
│  └─ def456/            ← Another run
└─ models/               ← Model registry
   └─ housing_price_predictor/
```

**Also tracked in:**
```
models/model_registry/registry.json  ← Your local registry
logs/evaluation_report.json          ← Local metrics
```

---

## 🎯 Interview Talking Points

**Question:** "How do you track ML experiments?"

**Your Answer:**

> "I use MLflow for comprehensive experiment tracking and model management. Every training run automatically logs parameters, metrics, and artifacts to MLflow. This allows me to compare dozens of experiments visually, identify the best performing models, and maintain a central model registry with proper versioning and lifecycle management. I can then serve any registered model as a REST API with a single command using MLflow's built-in serving capabilities, which is production-ready with automatic input validation and error handling."

**Key terms:**
- Experiment tracking (MLflow Tracking)
- Model registry (MLflow Model Registry)
- Model serving (MLflow Models)
- Reproducibility
- Version control for models
- One-click deployment

---

## ✅ Success Checklist

After completing this guide, you should have:

- [x] MLflow installed
- [x] MLflow tracking integrated in training
- [x] Config updated (enable_mlflow: true)
- [x] Models automatically registered
- [x] MLflow UI accessible
- [x] Model serving API ready

---

## 🚀 Next Steps

1. **Train your first model with MLflow:**
   ```bash
   dvc repro
   ```

2. **View in MLflow UI:**
   ```bash
   mlflow ui
   # Open: http://localhost:5000
   ```

3. **Experiment with different settings:**
   - Change `n_estimators` in config.yaml
   - Run `dvc repro` each time
   - Compare in MLflow UI

4. **Serve your best model:**
   ```bash
   python serve_model_api.py
   ```

5. **Test the API:**
   See examples with: `python serve_model_api.py --examples`

---

**Congratulations!** You now have a production-grade MLOps pipeline with MLflow! 🎉
```
