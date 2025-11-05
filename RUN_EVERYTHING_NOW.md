# 🚀 Run Everything Together - Step by Step

## ✅ Current Status

**All services are RUNNING!** ✅

- ✅ **MLflow UI**: http://localhost:5000
- ✅ **Airflow UI**: http://localhost:8080
- ✅ **DVC Pipeline**: Ready to use
- ✅ **Latest Model**: R² = 82%, RMSE = $48,475

---

## 🎯 Option 1: Run via Airflow UI (Recommended!)

### **Step 1: Open Airflow**

```
http://localhost:8080
```

**Login:**
- Username: `admin`
- Password: `admin`

---

### **Step 2: Find Your Pipeline**

Look for: **`housing_price_ml_pipeline`**

You'll see it in the DAGs list with:
- Description: "Automated ML pipeline for housing price prediction with MLflow tracking"
- Schedule: @daily

---

### **Step 3: Enable the DAG**

**Click the toggle switch** on the left side of the row (it will turn blue/green)

---

### **Step 4: Trigger the Pipeline**

**Click the ▶️ play button** on the right side

Select: **"Trigger DAG"**

Click: **"Trigger"** to confirm

---

### **Step 5: Watch it Run!**

1. **Click on the DAG name** to open it
2. **Select "Graph" view** at the top
3. **Watch the magic happen!** 🎬

You'll see tasks change colors:
- ⚪ White → Waiting
- 🟡 Yellow → Running
- 🟢 Green → Success!

**Expected timeline:**
```
0:00 - 0:05  🟡 ingest_data
0:05 - 0:08  🟡 feature_engineering
0:08 - 0:38  🟡 train_model (longest!)
0:38 - 0:39  🟡 validate_model
0:39 - 0:40  🟡 promote_to_staging
0:40 - 0:41  🟡 send_success_notification

Total: ~40-50 seconds
```

---

### **Step 6: Check MLflow Tracking**

While pipeline is running or after it completes:

**Open MLflow UI:**
```
http://localhost:5000
```

You'll see:
- **New experiment** logged
- **All metrics**: RMSE, MAE, R², MAPE
- **Parameters**: n_estimators, max_depth, etc.
- **Model artifacts**
- **Feature importance**

---

### **Step 7: View Results**

After pipeline completes (all tasks green):

**In Airflow:**
- Click any task box → "Log" to see detailed output
- Check "send_success_notification" task for summary

**In MLflow:**
- See the new experiment run
- Compare with previous runs
- Check model registry

**In Files:**
```bash
# Evaluation Report
cat logs/evaluation_report.json

# Model Registry
cat models/model_registry/registry.json

# Data Quality
cat logs/data_quality_report.json
```

---

## 🎯 Option 2: Run via DVC (Development Mode)

If you want to test with DVC's smart caching:

```bash
# Run complete pipeline with DVC
dvc repro -v
```

**What happens:**
1. ✅ DVC checks what changed
2. ✅ Skips unchanged stages (faster!)
3. ✅ Runs only necessary stages
4. ✅ MLflow logs everything
5. ✅ Results saved

**Benefits:**
- ⚡ Faster with caching
- 🎯 Only reruns what changed
- 📊 Still logs to MLflow

---

## 🎯 Option 3: Run Complete Pipeline Script

Use the interactive script I created:

```bash
bash run_complete_pipeline.sh
```

This will:
1. ✅ Check all services
2. ✅ Show current status
3. ✅ Give you 3 options:
   - Manual DVC run
   - Airflow trigger
   - Full integration

Choose option **2** for Airflow trigger!

---

## 📊 Real-Time Monitoring

**Open these 2 tabs in your browser:**

### Tab 1: Airflow (Pipeline Execution)
```
http://localhost:8080
```
- See task progress
- Check task logs
- Monitor failures
- View task history

### Tab 2: MLflow (Metrics & Models)
```
http://localhost:5000
```
- See experiment metrics
- Compare runs
- Check model versions
- View artifacts

---

## 🎬 What's Happening Behind the Scenes

When you trigger the pipeline:

```
Airflow (Orchestrator)
    │
    ├─ Runs: python pipeline/stage_01_ingest_data.py
    │  └─ Fetches 20,640 houses
    │  └─ Validates quality
    │  └─ Saves to data/
    │
    ├─ Runs: python pipeline/stage_02_feature_engineering.py
    │  └─ Creates 15 features
    │  └─ Encodes & scales
    │  └─ Saves artifacts
    │
    ├─ Runs: python pipeline/stage_03_train_model_mlflow.py
    │  └─ Trains Random Forest
    │  └─ 🚀 LOGS TO MLFLOW! 🚀
    │  │   ├─ Parameters: n_estimators=275, max_depth=20
    │  │   ├─ Metrics: RMSE, MAE, R², MAPE
    │  │   ├─ Model: Saved and registered
    │  │   └─ Artifacts: Feature importance, plots
    │  └─ Saves to models/
    │
    ├─ Validates: Check if R² ≥ 0.75 and RMSE ≤ $50k
    │  └─ ✅ PASS → Continue
    │  └─ ❌ FAIL → Alert and stop
    │
    └─ Promotes: Model to "staging" stage
       └─ Updates registry
       └─ Sends success notification
```

---

## 🎉 Expected Output

### Airflow UI - All Tasks Green:
```
🟢 ingest_data
🟢 feature_engineering
🟢 train_model
🟢 validate_model
🟢 promote_to_staging
⚫ send_failure_alert (skipped)
🟢 send_success_notification
```

### MLflow UI - New Experiment:
```
Experiment: housing_price_prediction
Run Name: run_2025-11-05_...
Metrics:
  • RMSE: $48,475
  • MAE: $32,000
  • R²: 0.82 (82%)
  • MAPE: 17.8%
Model: Registered as housing_price_predictor v1.X
```

### Files Updated:
```
✅ data/features/housing_features.csv
✅ models/saved_models/model_v*.joblib
✅ logs/evaluation_report.json
✅ logs/mlruns/[new experiment]
✅ models/model_registry/registry.json
```

---

## 🔥 Pro Tips

### 1. **Auto-refresh Airflow Graph**
- In Graph view, enable "Auto-refresh"
- View updates every 5 seconds automatically

### 2. **Compare MLflow Runs**
- In MLflow UI, select multiple runs
- Click "Compare"
- See side-by-side metrics

### 3. **Check Task Logs in Real-Time**
- Click task in Airflow
- Click "Log"
- Watch logs stream live!

### 4. **Retry Failed Tasks**
- Click red task box
- Click "Clear"
- Choose "Downstream" to rerun dependents
- Click "OK"

---

## 🆘 Troubleshooting

### DAG Not Showing?
```bash
# Check scheduler logs
tail -f airflow/logs/scheduler.log
```

### Task Failed?
1. Click red task box
2. Click "Log"
3. Read error at bottom
4. Fix issue
5. Clear and rerun

### MLflow Not Logging?
Check `config/config.yaml`:
```yaml
training:
  enable_mlflow: true  # Make sure this is true!
```

---

## ✅ Quick Status Check Anytime

```bash
bash check_status.sh
```

Shows:
- ✅ What services are running
- ✅ Latest model performance
- ✅ Last evaluation metrics
- ✅ Quick actions

---

## 🎊 You're Ready!

**Everything is set up and running!**

**Just open:**
1. http://localhost:8080 (Airflow)
2. Click ▶️ on `housing_price_ml_pipeline`
3. Watch the magic! ✨

**Then check:**
- http://localhost:5000 (MLflow) for metrics
- Airflow Graph view for task progress

---

## 📚 What You're Running

### The Complete Stack:

```
┌─────────────────────────────────────┐
│         AIRFLOW (Scheduler)         │
│      Triggers at midnight daily     │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│      PYTHON PIPELINE STAGES         │
│  stage_01 → stage_02 → stage_03     │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│           MLFLOW TRACKING           │
│   Logs all params, metrics, models │
└─────────────────────────────────────┘
```

**Optional:** Can add DVC for caching benefits

---

## 🎯 Next Steps

After your first successful run:

1. ✅ Check MLflow experiments
2. ✅ Compare multiple runs
3. ✅ Try changing config/config.yaml
4. ✅ Trigger another run
5. ✅ Compare the difference!

---

**Go ahead and trigger it! The UI is waiting for you!** 🚀

Open: http://localhost:8080
