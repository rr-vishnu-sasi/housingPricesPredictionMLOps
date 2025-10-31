# MLflow Integration - All Changes Explained (Simple Terms)

## 🎯 What We Did

We added **MLflow** to your existing project. Think of it as adding a "lab notebook" that automatically records every experiment.

---

## 📁 Files Changed (Summary)

### **NEW Files (Created):**
1. `src/mlflow_tracker.py` - MLflow helper class
2. `pipeline/stage_03_train_model_mlflow.py` - Training with MLflow
3. `serve_model_api.py` - Model serving script
4. `MLFLOW_GUIDE.md` - Documentation

### **MODIFIED Files:**
1. `config/config.yaml` - Enabled MLflow
2. `dvc.yaml` - Updated to use MLflow training
3. `requirements.txt` - Added MLflow package

---

## 🔧 FILE-BY-FILE BREAKDOWN

### **1. src/mlflow_tracker.py** (NEW)

**What it is:** A helper class to make MLflow easier to use

**Simple Analogy:**
> Like a TV remote control. Instead of manually pressing buttons on the TV, you use the remote (easier!).

**The Class:**

```python
class MLflowTracker:
    """Helper for using MLflow"""

    def __init__(self, config):
        # Setup: Where to save MLflow data
        tracking_uri = "file:./logs/mlruns"
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment("housing_price_prediction")
```

**What it does:**
```
Tells MLflow:
- Where to save data: logs/mlruns/
- Experiment name: housing_price_prediction
```

**Methods (Functions):**

```python
1. start_run(run_name)
   # What: Start recording an experiment
   # Like: Opening a new page in your lab notebook
   # Example: tracker.start_run("experiment_1")

2. log_params(params)
   # What: Record the settings you used
   # Like: Writing "Used 150 trees, max depth 20"
   # Example: tracker.log_params({'n_estimators': 150})

3. log_metrics(metrics)
   # What: Record the results you got
   # Like: Writing "Got 82% accuracy, $48k error"
   # Example: tracker.log_metrics({'r2_score': 0.82})

4. log_model(model, name)
   # What: Save the trained model
   # Like: Saving your finished cake recipe
   # Example: tracker.log_model(trained_model, "housing_predictor")

5. end_run()
   # What: Finish recording
   # Like: Closing the notebook page
   # Example: tracker.end_run()
```

**Complete Example:**
```python
# Create tracker
tracker = MLflowTracker(config)

# Start experiment
tracker.start_run("my_experiment")

# Record what you did
tracker.log_params({'n_estimators': 150, 'max_depth': 20})

# Record what you got
tracker.log_metrics({'rmse': 48677, 'r2_score': 0.82})

# Save the model
tracker.log_model(my_trained_model, "housing_price_predictor")

# Done!
tracker.end_run()
```

**Why we created this:**
- Makes MLflow easier to use
- Less code to write
- Consistent across project

---

### **2. pipeline/stage_03_train_model_mlflow.py** (NEW)

**What it is:** Modified training script that uses MLflow

**Simple Analogy:**
> Old version: Train model, save to disk
> New version: Train model, save to disk AND record in MLflow

**Main Function:**

```python
def run_model_training_with_mlflow():
    # 1. Setup
    logger = PipelineLogger("stage_03_train_mlflow")
    config = load_config()
    mlflow_tracker = MLflowTracker(config)  # ← NEW!

    # 2. Start MLflow tracking
    run_name = "random_forest_150_trees"
    mlflow_tracker.start_run(run_name)  # ← NEW! Start recording

    # 3. Load data (same as before)
    df = pd.read_csv('data/features/housing_features.csv')

    # 4. Split data (same as before)
    trainer = ModelTrainer(config)
    X_train, X_val, y_train, y_val = trainer.split_data(df)

    # 5. Log to MLflow ← NEW!
    mlflow_tracker.log_params({
        'n_estimators': 150,
        'max_depth': 20,
        'train_samples': 16512
    })

    # 6. Train model (same as before)
    trainer.train(X_train, y_train)

    # 7. Evaluate (same as before)
    evaluator = ModelEvaluator(config)
    y_pred = trainer.predict(X_val)
    report = evaluator.evaluate(y_val, y_pred)

    # 8. Log metrics to MLflow ← NEW!
    mlflow_tracker.log_metrics({
        'rmse': report['metrics']['rmse'],
        'r2_score': report['metrics']['r2_score'],
        'mae': report['metrics']['mae']
    })

    # 9. Log model to MLflow ← NEW!
    mlflow_tracker.log_model(
        trainer.model,
        registered_model_name="housing_price_predictor"
    )

    # 10. End MLflow tracking ← NEW!
    mlflow_tracker.end_run()

    # 11. Save locally (same as before, for backward compatibility)
    trainer.save_model()
    registry.register_model(...)
```

**What Changed:**

**BEFORE (without MLflow):**
```python
# Load data
# Train model
# Evaluate
# Save to disk
# Done!
```

**AFTER (with MLflow):**
```python
# Start MLflow tracking ← NEW
# Load data
# Log parameters to MLflow ← NEW
# Train model
# Evaluate
# Log metrics to MLflow ← NEW
# Log model to MLflow ← NEW
# End MLflow tracking ← NEW
# Save to disk (still do this too!)
# Done!
```

**Why we did this:**
- Records every experiment automatically
- Can compare experiments in UI
- Models versioned in MLflow Registry

---

### **3. config/config.yaml** (MODIFIED)

**What changed:**

```yaml
# BEFORE:
training:
  enable_mlflow: false  # MLflow not installed

model:
  hyperparameters:
    random_forest:
      n_estimators: 100  # Original setting

# AFTER:
training:
  enable_mlflow: true  # ← CHANGED! MLflow now active

model:
  hyperparameters:
    random_forest:
      n_estimators: 300  # ← CHANGED! Experimenting with more trees
```

**Simple Explanation:**
```
enable_mlflow: false  → MLflow tracking OFF
enable_mlflow: true   → MLflow tracking ON (records everything!)

n_estimators: 100  → Use 100 decision trees
n_estimators: 300  → Use 300 decision trees (more = usually better)
```

**Why we changed this:**
- Turn on MLflow tracking
- Experiment with different parameters

---

### **4. dvc.yaml** (MODIFIED)

**What changed:**

```yaml
# BEFORE:
train_model:
  cmd: python pipeline/stage_03_train_model.py  # Old version
  deps:
    - pipeline/stage_03_train_model.py

# AFTER:
train_model:
  cmd: python pipeline/stage_03_train_model_mlflow.py  # ← NEW version with MLflow!
  deps:
    - pipeline/stage_03_train_model_mlflow.py  # ← NEW
    - src/mlflow_tracker.py  # ← NEW dependency
```

**Simple Explanation:**
```
DVC now runs the MLflow-enabled version of training
```

**Why:**
- So `dvc repro` automatically uses MLflow
- Tracks MLflow files as dependencies (reruns if they change)

---

### **5. requirements.txt** (MODIFIED)

**What changed:**

```
# BEFORE:
# mlflow>=2.8.0  # (commented out)

# AFTER:
mlflow>=2.8.0  # Installed! ✓
```

**Simple Explanation:**
- Added MLflow to list of required packages
- Anyone cloning your project will install MLflow automatically

---

### **6. serve_model_api.py** (NEW)

**What it is:** Script to serve your model as a REST API

**Simple Analogy:**
> Your model becomes a website. You send house data, you get price back.

**Main Function:**

```python
def serve_model_mlflow_cli(model_name="housing_price_predictor", port=5001):
    # 1. Get model from MLflow registry
    client = mlflow.MlflowClient()
    versions = client.search_model_versions(f"name='{model_name}'")

    # 2. Get latest version
    latest_version = versions[0]

    # 3. Create model URI
    model_uri = f"models:/{model_name}/latest"

    # 4. Serve it!
    subprocess.run([
        "mlflow", "models", "serve",
        "-m", model_uri,
        "-p", str(port)
    ])
```

**How it works:**
```
1. Looks in MLflow registry for "housing_price_predictor"
2. Gets the latest version (e.g., v3)
3. Starts a web server on port 5001
4. Server accepts house data via HTTP
5. Returns price predictions
```

**Usage:**
```bash
# Terminal 1: Start server
python serve_model_api.py

# Terminal 2: Send prediction request
curl -X POST http://localhost:5001/invocations -d '{...}'
# Response: {"predictions": [452600.0]}
```

---

## 🔄 How Everything Works Together

Let me show you the **complete flow** with all classes:

```
┌─────────────────────────────────────────────────────────────┐
│  YOU: Run Pipeline                                          │
│  $ dvc repro                                                │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  DVC reads: dvc.yaml                                        │
│  Finds: cmd: python pipeline/stage_03_train_model_mlflow.py│
│  Runs: That script                                          │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  FILE: pipeline/stage_03_train_model_mlflow.py             │
│                                                             │
│  def run_model_training_with_mlflow():                     │
│      # Creates instances of classes:                        │
│      config = load_config()  ← Uses: utils.py              │
│      logger = PipelineLogger()  ← Uses: pipeline_logger.py │
│      mlflow_tracker = MLflowTracker()  ← Uses: mlflow_tracker.py │
│      trainer = ModelTrainer()  ← Uses: models/train.py     │
│      evaluator = ModelEvaluator()  ← Uses: evaluation/evaluate.py │
│      registry = ModelRegistry()  ← Uses: models/registry.py│
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: MLflowTracker.start_run()                         │
│  ─────────────────────────────────────────────────────────│
│  What: Tells MLflow "Start recording experiment"           │
│  Creates: New run in logs/mlruns/                          │
│  Result: Run ID = abc123                                   │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: ModelTrainer.split_data()                         │
│  ─────────────────────────────────────────────────────────│
│  What: Splits 20,640 houses into 80/20                     │
│  Class: ModelTrainer (from src/models/train.py)            │
│  Result: 16,512 training, 4,128 validation                 │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: MLflowTracker.log_params()  ← NEW WITH MLFLOW     │
│  ─────────────────────────────────────────────────────────│
│  What: Records settings to MLflow                          │
│  Logs: n_estimators=300, max_depth=20, etc.               │
│  Saved to: logs/mlruns/.../params/                        │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: ModelTrainer.train()                              │
│  ─────────────────────────────────────────────────────────│
│  What: Trains Random Forest model                          │
│  Class: ModelTrainer (from src/models/train.py)            │
│  Result: Trained model object                              │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 5: ModelEvaluator.evaluate()                         │
│  ─────────────────────────────────────────────────────────│
│  What: Tests model on validation set                       │
│  Class: ModelEvaluator (from src/evaluation/evaluate.py)   │
│  Result: {'rmse': 48677, 'r2_score': 0.82, ...}           │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 6: MLflowTracker.log_metrics()  ← NEW WITH MLFLOW    │
│  ─────────────────────────────────────────────────────────│
│  What: Records results to MLflow                           │
│  Logs: rmse=48677, r2_score=0.82, etc.                    │
│  Saved to: logs/mlruns/.../metrics/                       │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 7: MLflowTracker.log_model()  ← NEW WITH MLFLOW      │
│  ─────────────────────────────────────────────────────────│
│  What: Saves model to MLflow registry                      │
│  Registers as: "housing_price_predictor" v1                │
│  Saved to: logs/mlruns/.../artifacts/model/               │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 8: ModelRegistry.register_model()                    │
│  ─────────────────────────────────────────────────────────│
│  What: Also saves to local registry (backward compatible)  │
│  Class: ModelRegistry (from src/models/registry.py)        │
│  Saved to: models/model_registry/registry.json             │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 9: MLflowTracker.end_run()  ← NEW WITH MLFLOW        │
│  ─────────────────────────────────────────────────────────│
│  What: Closes the experiment recording                     │
│  Result: All data saved to MLflow!                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎓 Classes Involved (Detailed Explanation)

### **Class 1: MLflowTracker** (NEW)

**Location:** `src/mlflow_tracker.py`

**Purpose:** Wrapper to make MLflow easy to use

**Attributes (Data it holds):**
```python
self.config           # Configuration from config.yaml
self.training_config  # Training settings
self.logger           # For logging messages
```

**Methods (What it can do):**

| Method | What it does | Example |
|--------|-------------|---------|
| `__init__()` | Setup MLflow | `tracker = MLflowTracker(config)` |
| `start_run()` | Start experiment | `tracker.start_run("exp_1")` |
| `log_params()` | Record settings | `tracker.log_params({'n_estimators': 100})` |
| `log_metrics()` | Record results | `tracker.log_metrics({'rmse': 48726})` |
| `log_model()` | Save model | `tracker.log_model(model, "my_model")` |
| `set_tags()` | Add labels | `tracker.set_tags({'stage': 'dev'})` |
| `end_run()` | Finish recording | `tracker.end_run()` |

**Simple Example:**
```python
# Like writing in a lab notebook:

tracker = MLflowTracker(config)  # Open notebook

tracker.start_run("experiment_1")  # New page: "Experiment 1"

# Write settings:
tracker.log_params({'trees': 150})  # "Used 150 trees"

# Write results:
tracker.log_metrics({'accuracy': 0.82})  # "Got 82% accuracy"

tracker.end_run()  # Close page
```

---

### **Class 2: ModelTrainer** (EXISTING, used by MLflow script)

**Location:** `src/models/train.py`

**Purpose:** Handles model training

**What it does:**
```python
trainer = ModelTrainer(config)

# 1. Split data
X_train, X_val, y_train, y_val = trainer.split_data(df)

# 2. Train model
trainer.train(X_train, y_train)

# 3. Make predictions
predictions = trainer.predict(X_val)

# 4. Get feature importance
importance = trainer.get_feature_importance(X_train)

# 5. Save model
model_path = trainer.save_model()
```

**Nothing changed in this class - we just USE it in the MLflow script!**

---

### **Class 3: ModelEvaluator** (EXISTING, used by MLflow script)

**Location:** `src/evaluation/evaluate.py`

**Purpose:** Calculates model performance metrics

**What it does:**
```python
evaluator = ModelEvaluator(config)

# Evaluate model
report = evaluator.evaluate(
    y_true=y_val,      # Actual prices
    y_pred=predictions # Model's predictions
)

# Returns:
{
    'metrics': {
        'rmse': 48677,
        'mae': 31197,
        'r2_score': 0.8192,
        'mape': 17.30
    },
    'threshold_checks': {'rmse_threshold': True, ...},
    'all_checks_passed': True
}
```

**Nothing changed in this class - we just USE its output in MLflow!**

---

### **Class 4: ModelRegistry** (EXISTING, still used)

**Location:** `src/models/registry.py`

**Purpose:** Local model versioning (your original registry)

**What it does:**
```python
registry = ModelRegistry(config)

# Register model locally
version_id = registry.register_model(
    model_path="models/saved_models/model_*.joblib",
    model_metadata={...},
    evaluation_report={...}
)

# Returns: "v_20251030_091537"
```

**Why we keep this:**
- Backward compatibility
- Dual tracking (local + MLflow)
- Local backup if MLflow unavailable

---

### **Class 5: PipelineLogger** (EXISTING, used everywhere)

**Location:** `src/pipeline_logger.py`

**Purpose:** Logs pipeline activities to files

**What it does:**
```python
logger = PipelineLogger("my_stage")

logger.stage_start("Training")  # "========== STAGE: Training - STARTED =========="
logger.info("Processing data...")  # "INFO - Processing data..."
logger.metric("RMSE", 48677)  # "METRIC | RMSE: 48677"
logger.stage_end("Training")  # "========== STAGE: Training - COMPLETED =========="
```

**Still used everywhere - nothing changed!**

---

## 📊 Complete Data Flow (With Classes)

```
YOU RUN: dvc repro
    ↓
DVC executes: stage_03_train_model_mlflow.py
    ↓
┌─────────────────────────────────────────────────┐
│ Inside stage_03_train_model_mlflow.py:          │
├─────────────────────────────────────────────────┤
│                                                 │
│ config = load_config()                          │
│   ↓                                             │
│   Returns: Dictionary with all settings         │
│                                                 │
│ logger = PipelineLogger(config)                 │
│   ↓                                             │
│   Creates: Logger instance                      │
│   Saves logs to: logs/stage_03_train_*.log     │
│                                                 │
│ mlflow_tracker = MLflowTracker(config)  ← NEW   │
│   ↓                                             │
│   Creates: MLflow tracker instance              │
│   Sets up: logs/mlruns/ directory               │
│                                                 │
│ mlflow_tracker.start_run("random_forest_300")   │
│   ↓                                             │
│   MLflow creates: New experiment folder         │
│   Assigns: Run ID (e.g., abc123)                │
│                                                 │
│ trainer = ModelTrainer(config)                  │
│   ↓                                             │
│   Creates: Trainer instance                     │
│                                                 │
│ X_train, X_val, y_train, y_val =                │
│     trainer.split_data(df)                      │
│   ↓                                             │
│   Splits: 80/20                                 │
│                                                 │
│ mlflow_tracker.log_params({...})  ← NEW         │
│   ↓                                             │
│   MLflow saves: n_estimators=300, etc.          │
│   Location: logs/mlruns/.../params/             │
│                                                 │
│ trainer.train(X_train, y_train)                 │
│   ↓                                             │
│   Trains: Random Forest model                   │
│   Result: trainer.model (trained object)        │
│                                                 │
│ evaluator = ModelEvaluator(config)              │
│   ↓                                             │
│   Creates: Evaluator instance                   │
│                                                 │
│ predictions = trainer.predict(X_val)            │
│   ↓                                             │
│   Predicts: 4,128 house prices                  │
│                                                 │
│ report = evaluator.evaluate(y_val, predictions) │
│   ↓                                             │
│   Calculates: RMSE, R², MAE, MAPE              │
│   Returns: Dictionary with all metrics          │
│                                                 │
│ mlflow_tracker.log_metrics(report['metrics'])   │
│   ↓                                             │
│   MLflow saves: RMSE=48677, R²=0.82, etc.      │
│   Location: logs/mlruns/.../metrics/            │
│                                                 │
│ mlflow_tracker.log_model(trainer.model, ...)    │
│   ↓                                             │
│   MLflow saves: Complete trained model          │
│   Registers: "housing_price_predictor" v2       │
│   Location: logs/mlruns/.../artifacts/model/    │
│                                                 │
│ registry = ModelRegistry(config)                │
│ registry.register_model(...)                    │
│   ↓                                             │
│   Local registry saves: v_20251030_091537       │
│   Location: models/model_registry/registry.json │
│                                                 │
│ mlflow_tracker.end_run()  ← NEW                 │
│   ↓                                             │
│   MLflow finalizes: Experiment complete         │
│                                                 │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  RESULT:                                                    │
│  ✓ Model trained and saved locally                         │
│  ✓ Model tracked in MLflow (params + metrics + model)      │
│  ✓ Model registered in MLflow Model Registry               │
│  ✓ Model registered in local registry                      │
│  ✓ All logs saved                                          │
│  ✓ Can view in MLflow UI: http://127.0.0.1:5002           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Simple Comparison: Before vs After

### **BEFORE MLflow:**

```python
# Train model
trainer = ModelTrainer(config)
trainer.train(X_train, y_train)

# Evaluate
evaluator = ModelEvaluator(config)
metrics = evaluator.evaluate(y_val, predictions)

# Save
trainer.save_model()  # Saved to disk

# Problem:
# - Hard to compare experiments
# - Metrics scattered in different files
# - No visual dashboard
```

### **AFTER MLflow:**

```python
# Start tracking
mlflow_tracker = MLflowTracker(config)  # ← NEW
mlflow_tracker.start_run("experiment_1")  # ← NEW

# Log parameters
mlflow_tracker.log_params({'n_estimators': 150})  # ← NEW

# Train model (same as before)
trainer = ModelTrainer(config)
trainer.train(X_train, y_train)

# Evaluate (same as before)
evaluator = ModelEvaluator(config)
metrics = evaluator.evaluate(y_val, predictions)

# Log metrics
mlflow_tracker.log_metrics(metrics)  # ← NEW

# Log model
mlflow_tracker.log_model(trainer.model, "my_model")  # ← NEW

# End tracking
mlflow_tracker.end_run()  # ← NEW

# Save locally too
trainer.save_model()

# Benefits:
# ✓ All experiments in one place (MLflow UI)
# ✓ Easy comparison (visual charts)
# ✓ Model versioning (v1, v2, v3)
# ✓ One-click serving
```

---

## 💡 Real-World Example

**Scenario:** You want to find the best number of trees

**Without MLflow (hard way):**
```bash
# Try 100 trees
# Edit config manually
python main_pipeline.py
# Write down: "100 trees → RMSE: 48,726"

# Try 150 trees
# Edit config manually
python main_pipeline.py
# Write down: "150 trees → RMSE: 48,677"

# Try 200 trees
# Edit config manually
python main_pipeline.py
# Write down: "200 trees → RMSE: 48,500"

# Compare manually (look at your notes)
# Best: 200 trees!
```

**With MLflow (easy way):**
```bash
# Try 100 trees
# Edit config: n_estimators: 100
dvc repro
# MLflow automatically records everything

# Try 150 trees
# Edit config: n_estimators: 150
dvc repro
# MLflow automatically records everything

# Try 200 trees
# Edit config: n_estimators: 200
dvc repro
# MLflow automatically records everything

# Compare in UI:
# Open: http://127.0.0.1:5002
# Click: Experiments → Select all 3 → Compare
# See: Beautiful chart showing 200 is best!
```

---

## 🔍 What Gets Saved Where

### **Local Files (Always saved):**
```
models/saved_models/
  ├─ model_random_forest_*.joblib  ← Trained model
  ├─ scaler.joblib
  └─ encoder.joblib

models/model_registry/
  └─ registry.json  ← Local registry

logs/
  └─ evaluation_report.json  ← Metrics
```

### **MLflow Files (NEW):**
```
logs/mlruns/
  ├─ 0/                           ← Default experiment
  ├─ 223965389543970541/          ← housing_price_prediction experiment
  │   ├─ abc123/                  ← Run 1 (150 trees)
  │   │   ├─ params/
  │   │   │   ├─ n_estimators    (contains: "150")
  │   │   │   └─ max_depth       (contains: "20")
  │   │   ├─ metrics/
  │   │   │   ├─ rmse            (contains: "48677")
  │   │   │   └─ r2_score        (contains: "0.8192")
  │   │   ├─ artifacts/
  │   │   │   └─ model/          ← Trained model
  │   │   └─ meta.yaml           ← Metadata
  │   │
  │   └─ def456/                  ← Run 2 (100 trees)
  │       ├─ params/
  │       ├─ metrics/
  │       └─ artifacts/
  │
  └─ models/                      ← Model Registry
      └─ housing_price_predictor/
          ├─ version-1/
          ├─ version-2/
          └─ version-3/
```

---

## 🎯 Key Takeaways

### **What MLflow Added:**

1. **Automatic Experiment Tracking**
   - Every run recorded automatically
   - Parameters and metrics saved
   - Models versioned

2. **Visual Dashboard (MLflow UI)**
   - http://127.0.0.1:5002
   - Compare experiments visually
   - Charts and graphs

3. **Model Registry**
   - Version control for models (v1, v2, v3)
   - Lifecycle management (dev → staging → production)
   - Easy rollback

4. **Model Serving**
   - One-command deployment
   - REST API automatically created
   - Production-ready

### **Classes Involved:**

| Class | File | Purpose | New/Modified |
|-------|------|---------|--------------|
| **MLflowTracker** | `src/mlflow_tracker.py` | MLflow wrapper | ✅ NEW |
| **ModelTrainer** | `src/models/train.py` | Train models | Existing |
| **ModelEvaluator** | `src/evaluation/evaluate.py` | Evaluate models | Existing |
| **ModelRegistry** | `src/models/registry.py` | Local versioning | Existing |
| **PipelineLogger** | `src/pipeline_logger.py` | Logging | Existing |
| **FeatureEngineer** | `src/features/engineer.py` | Feature engineering | Existing |
| **DataIngestor** | `src/data/ingest.py` | Data loading | Existing |

**Summary:**
- Added **1 new class** (MLflowTracker)
- Modified **0 existing classes** (just use them!)
- Created **1 new pipeline script** that uses all classes together

---

## ✅ Summary

**What we did:**
1. Created `MLflowTracker` class (makes MLflow easy)
2. Created new training script that uses MLflowTracker
3. Updated config to enable MLflow
4. Updated DVC to use new training script

**Result:**
- All experiments tracked automatically
- Visual dashboard to compare models
- Model registry with versioning
- One-command model serving

**You can now:**
- ✅ Train models with automatic tracking
- ✅ Compare experiments in UI
- ✅ Register models with versions
- ✅ Serve models as REST API

---

**Simple enough?** Try running another experiment and see it appear in the UI! 🚀
