# Airflow Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Start Airflow

```bash
bash start_airflow.sh
```

**What happens:**
- Starts Airflow webserver (port 8080)
- Starts Airflow scheduler
- Takes ~30-60 seconds to be ready

### Step 2: Access Airflow UI

1. Open browser: **http://localhost:8080**
2. Login:
   - Username: `admin`
   - Password: `admin`

### Step 3: Run Your Pipeline

1. Find DAG: `housing_price_ml_pipeline`
2. **Toggle the switch** to enable it (top-left)
3. Click the **▶️ play button** → "Trigger DAG"
4. **Watch it run!** (Graph view recommended)

---

## 📊 What to Expect

### Your Pipeline Will:

1. **Ingest Data** (~5 sec)
   - Fetches 20,640 California houses
   - Validates data quality

2. **Engineer Features** (~3 sec)
   - Creates 15 ML-ready features
   - Scales and encodes data

3. **Train Model** (~30 sec)
   - Trains Random Forest (275 trees)
   - Logs to MLflow

4. **Validate Model** (~1 sec)
   - Checks if R² ≥ 0.75
   - Checks if RMSE ≤ $50,000

5. **Promote or Alert** (~1 sec)
   - ✅ Good model → Promote to staging
   - ❌ Bad model → Send failure alert

**Total Duration**: ~40-50 seconds

---

## 📍 Where to Check Results

### 1. Airflow UI (http://localhost:8080)
- **Graph View**: Visual pipeline status
- **Grid View**: Run history
- **Logs**: Detailed task output

### 2. MLflow UI (http://localhost:5000)
```bash
# Start MLflow if not running
mlflow ui
```
- View experiment metrics
- Compare model versions
- Check feature importance

### 3. Local Files
- **Evaluation Report**: `logs/evaluation_report.json`
- **Model Registry**: `models/model_registry/registry.json`
- **Data Quality**: `logs/data_quality_report.json`

---

## 🛑 Stop Airflow

```bash
bash stop_airflow.sh
```

---

## 📅 Schedule Options

Your pipeline runs **@daily** (every night at midnight).

To change the schedule, edit `airflow/dags/housing_ml_pipeline.py`:

```python
# Line 79
schedule_interval='@daily',  # ← Change this
```

**Options:**
- `'@daily'` - Every day at midnight
- `'@weekly'` - Every Sunday at midnight
- `'@hourly'` - Every hour
- `'0 3 * * *'` - Every day at 3 AM
- `None` - Manual trigger only

After editing, restart Airflow:
```bash
bash stop_airflow.sh
bash start_airflow.sh
```

---

## 🔧 Troubleshooting

### DAG Not Showing Up?
```bash
# Check scheduler logs
tail -f airflow/logs/scheduler.log

# List all DAGs
source .venv_airflow/bin/activate
export AIRFLOW_HOME=$PWD/airflow
airflow dags list | grep housing
```

### Task Failed?
1. Click the red task box in Graph View
2. Click "Log" to see error details
3. Fix the issue in the corresponding stage file:
   - `pipeline/stage_01_ingest_data.py`
   - `pipeline/stage_02_feature_engineering.py`
   - `pipeline/stage_03_train_model_mlflow.py`
4. Clear the task and rerun

### Port 8080 Already in Use?
```bash
# Check what's using port 8080
lsof -ti:8080

# Kill it
pkill -f "airflow webserver"

# Or use a different port
airflow webserver --port 8081
```

### Can't Login?
- Username: `admin`
- Password: `admin`

If forgotten, create new user:
```bash
source .venv_airflow/bin/activate
export AIRFLOW_HOME=$PWD/airflow
airflow users create --username newadmin --password newpass --role Admin --firstname Admin --lastname User --email admin@example.com
```

---

## 💡 Pro Tips

### 1. View Logs in Real-Time
```bash
# Webserver logs
tail -f airflow/logs/webserver.log

# Scheduler logs
tail -f airflow/logs/scheduler.log

# Specific task logs
tail -f airflow/logs/dag_id=housing_price_ml_pipeline/run_id=*/task_id=train_model/*/attempt=1.log
```

### 2. Clear and Rerun Failed Tasks
1. Click the failed task (red box)
2. Click "Clear"
3. Choose "Downstream" to rerun dependent tasks too
4. Click "OK"

### 3. Run Single Task for Testing
```bash
source .venv_airflow/bin/activate
export AIRFLOW_HOME=$PWD/airflow

# Test a specific task
airflow tasks test housing_price_ml_pipeline ingest_data 2025-11-04
```

### 4. Pause DAG
- Click the toggle switch to pause
- Prevents scheduled runs
- Useful during maintenance

### 5. Skip Tasks
- Mark tasks as "success" to skip
- Useful for testing downstream tasks

---

## 📚 Learn More

- **Full Tutorial**: Read `AIRFLOW_TUTORIAL_SIMPLE.md`
- **Official Docs**: https://airflow.apache.org/docs/
- **Your DAG Code**: `airflow/dags/housing_ml_pipeline.py`

---

## ✅ Success Checklist

- [ ] Airflow UI opens at http://localhost:8080
- [ ] Can login with admin/admin
- [ ] DAG `housing_price_ml_pipeline` is visible
- [ ] DAG is enabled (toggle switch ON)
- [ ] Can trigger manual run
- [ ] All tasks turn green ✅
- [ ] MLflow shows new experiment
- [ ] Model in staging (`models/model_registry/registry.json`)

**All checked?** Congratulations! 🎉 Your ML pipeline is now automated!

---

## 🆘 Need Help?

1. Check `AIRFLOW_TUTORIAL_SIMPLE.md` for detailed explanations
2. Look at task logs in Airflow UI
3. Check scheduler logs: `airflow/logs/scheduler.log`
4. Verify DAG syntax:
   ```bash
   python airflow/dags/housing_ml_pipeline.py
   ```

---

**Happy Automating! 🚀**