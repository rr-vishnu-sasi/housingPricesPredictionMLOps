# DVC + MLflow + Airflow Integration Guide

## ✅ Yes, They Can All Work Together!

### Quick Answer:
- **DVC**: Pipeline definition + data versioning + smart caching
- **MLflow**: Experiment tracking + model registry
- **Airflow**: Production scheduling + monitoring + complex workflows

**They complement each other perfectly!**

---

## 🎯 Three Integration Approaches

### **Approach 1: Airflow Only (Current)**

```
Airflow → Python Scripts → MLflow
```

**Your DAG now:**
```python
task_ingest = BashOperator(
    bash_command='python pipeline/stage_01_ingest_data.py'
)
task_features = BashOperator(
    bash_command='python pipeline/stage_02_feature_engineering.py'
)
task_train = BashOperator(
    bash_command='python pipeline/stage_03_train_model_mlflow.py'
)
```

**Pros:**
- ✅ Full control in Airflow
- ✅ Custom validation logic
- ✅ MLflow logs everything

**Cons:**
- ❌ No caching (reruns everything)
- ❌ Pipeline defined in two places (dvc.yaml + Airflow)

---

### **Approach 2: Airflow + DVC (Recommended!)**

```
Airflow → DVC (dvc repro) → Python Scripts → MLflow
```

**Modified DAG:**
```python
# Single task runs entire DVC pipeline
task_run_dvc = BashOperator(
    task_id='run_dvc_pipeline',
    bash_command=f'cd {PROJECT_ROOT} && dvc repro',
)

# Then Airflow-specific tasks
task_validate = PythonOperator(
    task_id='validate_model',
    python_callable=validate_model_performance,
)

task_promote = PythonOperator(
    task_id='promote_to_staging',
    python_callable=promote_model_to_staging,
)

# Flow
task_run_dvc >> task_validate >> [task_promote, task_alert]
```

**Pros:**
- ✅ DVC smart caching (faster!)
- ✅ Single pipeline definition (dvc.yaml)
- ✅ Reproducibility guaranteed
- ✅ Airflow adds scheduling + advanced logic
- ✅ MLflow still logs everything

**Cons:**
- ⚠️ Less granular control in Airflow UI (one big task)

---

### **Approach 3: Hybrid (Best of Both Worlds)**

```
Airflow orchestrates:
├── DVC for main pipeline (with caching)
└── Custom Airflow tasks for business logic
```

**Hybrid DAG:**
```python
# Run DVC pipeline (gets caching benefits)
task_dvc = BashOperator(
    task_id='run_dvc_pipeline',
    bash_command=f'cd {PROJECT_ROOT} && dvc repro',
)

# Airflow-specific tasks (not in DVC)
task_validate = PythonOperator(
    task_id='validate_model',
    python_callable=validate_model_performance,
)

task_promote = PythonOperator(
    task_id='promote_to_staging',
    python_callable=promote_model_to_staging,
)

task_notify_slack = PythonOperator(
    task_id='notify_slack',
    python_callable=send_slack_notification,
)

task_update_dashboard = PythonOperator(
    task_id='update_dashboard',
    python_callable=update_monitoring_dashboard,
)

# Complex workflow
task_dvc >> task_validate >> [task_promote, task_alert]
task_promote >> [task_notify_slack, task_update_dashboard]
```

**Pros:**
- ✅ DVC caching for ML pipeline
- ✅ Airflow handles complex business logic
- ✅ Best performance
- ✅ Maximum flexibility

---

## 📊 When to Use Which?

### Use **Airflow Only** if:
- ❌ Don't need caching
- ❌ Don't have DVC setup
- ✅ Need full task-level visibility in UI
- ✅ Have complex per-task logic

### Use **Airflow + DVC** if:
- ✅ Have large datasets (caching matters!)
- ✅ Already use DVC
- ✅ Want reproducibility
- ✅ Pipeline stages are stable

### Use **Hybrid** if:
- ✅ Best performance needed
- ✅ Complex workflows beyond ML
- ✅ Want both caching + flexibility

---

## 🔧 Implementing Approach 2 (DVC + Airflow)

### Step 1: Verify DVC Works

```bash
# Test DVC pipeline manually
cd /path/to/project
dvc repro

# Should see:
# Running stage 'ingest_data'
# Running stage 'feature_engineering'
# Running stage 'train_model'
```

### Step 2: Create New Airflow DAG

Create `airflow/dags/housing_ml_pipeline_dvc.py`:

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import os

PROJECT_ROOT = '/Users/vishnu.sasi/Downloads/Vishnu-Personal/housingPricesPredictionProject'

default_args = {
    'owner': 'mlops-team',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='housing_ml_pipeline_dvc',
    default_args=default_args,
    description='ML pipeline using DVC + Airflow + MLflow',
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
    tags=['ml-pipeline', 'dvc', 'mlflow'],
) as dag:

    # Run entire DVC pipeline
    run_dvc_pipeline = BashOperator(
        task_id='run_dvc_pipeline',
        bash_command=f'cd {PROJECT_ROOT} && dvc repro',
        doc_md="""
        ### DVC Pipeline Execution

        Runs: dvc repro

        This executes all stages defined in dvc.yaml:
        1. stage_01_ingest_data
        2. stage_02_feature_engineering
        3. stage_03_train_model_mlflow

        DVC smart caching:
        - Skips stages where inputs haven't changed
        - Faster than rerunning everything

        MLflow tracking:
        - Each stage logs to MLflow automatically
        - Check MLflow UI for metrics
        """,
    )

    # Validate model (Airflow custom logic)
    def validate_model(**context):
        import json
        report_path = f'{PROJECT_ROOT}/logs/evaluation_report.json'
        with open(report_path) as f:
            report = json.load(f)

        r2 = report['metrics']['r2_score']
        rmse = report['metrics']['rmse']

        print(f"Model R²: {r2}, RMSE: ${rmse:,.0f}")

        if r2 >= 0.75 and rmse <= 50000:
            print("✅ Model validation PASSED!")
            return 'promote_to_staging'
        else:
            print("❌ Model validation FAILED!")
            return 'send_failure_alert'

    validate = BranchPythonOperator(
        task_id='validate_model',
        python_callable=validate_model,
    )

    # Promote model (Airflow custom logic)
    def promote_model(**context):
        import sys
        sys.path.insert(0, PROJECT_ROOT)
        from src.utils import load_config
        from src.models.registry import ModelRegistry

        config = load_config()
        registry = ModelRegistry(config)
        latest = registry.get_latest_model()

        registry.transition_model_stage(
            version_id=latest['version_id'],
            new_stage='staging',
        )

        print(f"✅ Model {latest['version_id']} promoted to STAGING")

    promote = PythonOperator(
        task_id='promote_to_staging',
        python_callable=promote_model,
    )

    # Alert on failure
    def alert(**context):
        print("❌ MODEL VALIDATION FAILED - ALERTING TEAM")

    alert = PythonOperator(
        task_id='send_failure_alert',
        python_callable=alert,
    )

    # Define workflow
    run_dvc_pipeline >> validate >> [promote, alert]
```

### Step 3: Test It

```bash
# 1. Enable the new DAG in Airflow UI
# 2. Trigger manual run
# 3. Watch it execute!
```

---

## 🎭 Role Summary

### **Development Workflow:**

```
You (Developer):
│
├─ Change config/code
│
├─ Run: dvc repro
│  └─ DVC: Smart caching, runs only changed stages
│     └─ Each stage: Logs to MLflow
│        └─ MLflow: Tracks experiments
│
├─ Check MLflow UI:
│  └─ Compare experiments
│  └─ Pick best model
│
└─ Commit: git add dvc.lock config.yaml
   └─ Reproducibility guaranteed!
```

### **Production Workflow:**

```
Airflow (Midnight):
│
├─ Triggers: housing_ml_pipeline_dvc
│
├─ Runs: dvc repro
│  └─ DVC: Smart caching
│     └─ MLflow: Tracks production runs
│
├─ Validates: Check metrics
│
├─ Promotes: If good model
│
└─ Alerts: If failures
```

---

## 🔥 Pro Tips

### 1. **DVC Caching is FAST**

```bash
# First run: Everything executes (50 seconds)
dvc repro

# Only change config (n_estimators: 300)
# Second run: Only training reruns! (30 seconds)
dvc repro
# Data ingestion: SKIPPED (cached)
# Feature engineering: SKIPPED (cached)
# Training: RUNS (config changed)
```

### 2. **MLflow Still Tracks Everything**

Even with DVC, every training run logs to MLflow:
- All experiments visible in MLflow UI
- Can compare DVC runs and Airflow runs
- Single source of truth for model performance

### 3. **Airflow Adds Production Logic**

Airflow is for things DVC can't do:
- Complex conditional logic
- External API calls
- Slack notifications
- Database updates
- Dashboard updates
- Multi-pipeline coordination

---

## 📋 Comparison: Your Current vs. DVC Integration

### **Current Setup:**

```
Airflow DAG:
├── Task: ingest_data (5s)
├── Task: feature_engineering (3s)
├── Task: train_model (30s)
├── Task: validate (1s)
└── Task: promote (1s)

Total: 40s every time (no caching)
Visibility: ✅ Each task visible in UI
Caching: ❌ None
```

### **With DVC Integration:**

```
Airflow DAG:
├── Task: run_dvc_pipeline (5-40s, depending on cache)
│   └── DVC runs 3 stages internally
├── Task: validate (1s)
└── Task: promote (1s)

Total: 7-42s (faster with cache!)
Visibility: ⚠️ DVC is one task
Caching: ✅ DVC smart caching
```

### **Real-World Benefit:**

```
Day 1: New data arrives
├── DVC: Runs all stages (40s)
└── Airflow: Validates + promotes (2s)
Total: 42s

Day 2: Only config changed (tune model)
├── DVC: Skips data stages, only trains (30s)
└── Airflow: Validates + promotes (2s)
Total: 32s (10s saved!)

Day 3: Nothing changed
├── DVC: Everything cached (5s)
└── Airflow: Validates + promotes (2s)
Total: 7s (35s saved!)
```

---

## 🎯 Recommendation for Your Project

### **Start with Current Setup (Airflow + MLflow)**
- Already working ✅
- Good visibility in UI
- Simpler to debug

### **Add DVC Integration Later If:**
- Pipelines become slower (>5 min)
- Need better reproducibility
- Want caching benefits
- Team grows (need consistency)

### **You Have Both Options Available!**

**Current DAG:** `housing_ml_pipeline.py` (no DVC)
**Optional DVC DAG:** Create `housing_ml_pipeline_dvc.py` (with DVC)

Run whichever suits your needs! 🚀

---

## 📚 Summary

| Tool | Purpose | When to Use |
|------|---------|-------------|
| **DVC** | Data versioning, pipeline caching, reproducibility | Development & Production |
| **MLflow** | Experiment tracking, model registry | Always! |
| **Airflow** | Scheduling, monitoring, complex workflows | Production |

**They work together beautifully!** ✨

Your project already has all three set up. You can:
1. Keep current Airflow DAG (works great!)
2. Or switch to DVC-based Airflow DAG (faster with caching)
3. Or use both (different scenarios)

**Choice is yours!** 🎉