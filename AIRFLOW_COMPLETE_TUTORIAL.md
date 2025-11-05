# Apache Airflow - Complete Tutorial (Simple Terms)

## 🎯 What is Apache Airflow?

**Simple Answer:** Airflow is a **task scheduler and monitor** for complex workflows.

### **Real-World Analogy:**

Think of Airflow like a **project manager**:

```
Project Manager (Airflow):
  ✅ Schedules tasks ("Data ingestion every morning at 3 AM")
  ✅ Makes sure tasks run in order ("Don't train model before data is ready")
  ✅ Monitors progress ("Is the pipeline still running?")
  ✅ Handles failures ("Data fetch failed? Retry 3 times, then alert the team")
  ✅ Provides dashboard ("Show me all pipeline runs from last week")
```

### **Without Airflow (Manual):**
```bash
# Every day, you manually run:
python stage_01_ingest.py
# Wait...
python stage_02_features.py
# Wait...
python stage_03_train.py
# Check if it worked...
# If failed, figure out what went wrong...
```

### **With Airflow (Automated):**
```python
# Define once:
DAG: "Run these 3 tasks, in order, every day at 3 AM"

# Airflow does:
  → Runs automatically every day
  → Monitors each task
  → Retries on failure
  → Alerts you if something breaks
  → Shows visual dashboard
```

---

## 📚 Core Concepts (Simple Explanation)

### **1. DAG (Directed Acyclic Graph)**

**What:** A DAG is your **workflow definition** (what tasks to run, in what order)

**Simple Analogy:** A recipe card

```
Recipe Card (DAG):
  Title: "Chocolate Cake"
  Schedule: "Make every Sunday"
  Steps:
    1. Mix dry ingredients
    2. Mix wet ingredients
    3. Combine all
    4. Bake for 30 minutes
    5. Let cool
    6. Frost

  Rules:
    • Must do in order (can't frost before baking!)
    • If step fails, stop
    • Alert chef if something burns
```

**In Code:**
```python
dag = DAG(
    'chocolate_cake',           # Name
    schedule_interval='@weekly', # Every Sunday
    start_date=datetime(2025, 1, 1),
)

# Tasks defined below...
```

**Key Points:**
- **Directed:** Tasks have a specific order (A → B → C)
- **Acyclic:** No loops (can't go backwards)
- **Graph:** Can visualize as a flowchart

---

### **2. Tasks**

**What:** Individual steps in your workflow

**Simple Analogy:** Steps in a recipe

```
Task 1: Mix dry ingredients
  • Input: Flour, sugar, cocoa
  • Does: Mix in bowl
  • Output: Dry mixture

Task 2: Mix wet ingredients
  • Input: Eggs, milk, oil
  • Does: Mix in separate bowl
  • Output: Wet mixture

Task 3: Combine
  • Input: Dry mixture + wet mixture
  • Does: Combine and stir
  • Output: Cake batter
```

**In Your ML Pipeline:**
```python
Task 1: ingest_data
  • Input: None (fetches from internet)
  • Does: Download housing data, validate quality
  • Output: data/raw/housing_data.csv

Task 2: feature_engineering
  • Input: data/raw/housing_data.csv
  • Does: Create features, encode, scale
  • Output: data/features/housing_features.csv

Task 3: train_model
  • Input: data/features/housing_features.csv
  • Does: Train Random Forest, evaluate
  • Output: models/saved_models/model_*.joblib
```

---

### **3. Operators**

**What:** **Types** of tasks you can run

**Simple Analogy:** Different kitchen tools

```
BashOperator  = Using a food processor (run shell commands)
PythonOperator = Using your hands (run Python functions)
EmailOperator = Using a messenger (send notifications)
SensorOperator = Using a timer (wait for something)
```

**Most Common Operators:**

#### **BashOperator** (Run shell commands)
```python
task = BashOperator(
    task_id='run_script',
    bash_command='python my_script.py'
)

# Like running in terminal:
# $ python my_script.py
```

#### **PythonOperator** (Run Python functions)
```python
def my_function():
    print("Hello from Airflow!")
    return "success"

task = PythonOperator(
    task_id='run_function',
    python_callable=my_function
)

# Calls: my_function()
```

#### **EmailOperator** (Send emails)
```python
task = EmailOperator(
    task_id='send_alert',
    to='team@example.com',
    subject='Pipeline Failed!',
    html_content='<h1>Check the logs!</h1>'
)
```

---

### **4. Dependencies**

**What:** Defines task order (which task runs after which)

**Simple Analogy:** Recipe steps

```
You can't frost a cake before baking it!

bake_cake >> cool_cake >> frost_cake
```

**In Code:**
```python
# Method 1: >> operator
task_a >> task_b >> task_c
# Means: A first, then B, then C

# Method 2: set_downstream()
task_a.set_downstream(task_b)
task_b.set_downstream(task_c)

# Method 3: set_upstream()
task_c.set_upstream(task_b)
task_b.set_upstream(task_a)
```

**Visual:**
```
task_a >> task_b
    ↓        ↓
┌────────┐  ┌────────┐
│Task A  │→ │Task B  │
└────────┘  └────────┘
```

---

### **5. Scheduling**

**What:** When the DAG runs

**Simple Analogy:** Setting an alarm

```
@daily     = Every day at midnight
@hourly    = Every hour
@weekly    = Every week (Sunday midnight)
@monthly   = Every month (1st day)

Custom:
'0 3 * * *'    = Every day at 3 AM
'0 */6 * * *'  = Every 6 hours
'0 0 * * 1'    = Every Monday at midnight
```

**In Code:**
```python
dag = DAG(
    'my_pipeline',
    schedule_interval='@daily'  # Run every day
)

# Airflow automatically:
# - Runs at midnight every day
# - No manual intervention needed!
```

---

## 📊 Complete Example (Your ML Pipeline)

Let me show you a **complete Airflow DAG** for your housing price prediction:

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

# ===========================
# Default Settings
# ===========================
default_args = {
    'owner': 'mlops-team',
    'retries': 2,                        # Retry twice if fails
    'retry_delay': timedelta(minutes=5), # Wait 5 min between retries
    'email': ['team@example.com'],
    'email_on_failure': True,            # Alert if fails
}

# ===========================
# Create DAG
# ===========================
dag = DAG(
    'housing_ml_pipeline',    # DAG name
    default_args=default_args,
    schedule_interval='@daily',  # Run every day
    start_date=datetime(2025, 10, 1),
    catchup=False,            # Don't backfill old dates
)

# ===========================
# Define Tasks
# ===========================

# Task 1: Data Ingestion
ingest = BashOperator(
    task_id='ingest_data',
    bash_command='python pipeline/stage_01_ingest_data.py',
    dag=dag,
)

# Task 2: Feature Engineering
features = BashOperator(
    task_id='engineer_features',
    bash_command='python pipeline/stage_02_feature_engineering.py',
    dag=dag,
)

# Task 3: Model Training
train = BashOperator(
    task_id='train_model',
    bash_command='python pipeline/stage_03_train_model_mlflow.py',
    dag=dag,
)

# Task 4: Validate Model
def validate():
    import json
    with open('logs/evaluation_report.json') as f:
        report = json.load(f)

    r2 = report['metrics']['r2_score']

    if r2 < 0.75:
        raise ValueError(f"Model too poor: R²={r2}")

    print(f"✓ Model validated: R²={r2}")


validate_task = PythonOperator(
    task_id='validate_model',
    python_callable=validate,
    dag=dag,
)

# ===========================
# Define Workflow
# ===========================
ingest >> features >> train >> validate_task
```

**Visual:**
```
┌──────────────┐
│ ingest_data  │  ← Runs first
└──────┬───────┘
       │
       ▼
┌────────────────────┐
│engineer_features   │  ← Runs second
└──────┬─────────────┘
       │
       ▼
┌──────────────┐
│ train_model  │  ← Runs third
└──────┬───────┘
       │
       ▼
┌─────────────────┐
│validate_model   │  ← Runs fourth
└─────────────────┘
```

---

## 🔄 How Airflow Works (Complete Flow)

### **Behind the Scenes:**

```
┌──────────────────────────────────────────────────────────┐
│  AIRFLOW COMPONENTS                                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  1. Scheduler                                            │
│     • Checks DAG schedules every minute                  │
│     • Creates DAG Runs when it's time                    │
│     • Submits tasks to executor                          │
│                                                          │
│  2. Executor                                             │
│     • Runs the actual tasks                              │
│     • Can run locally or distributed (Celery, Kubernetes)│
│                                                          │
│  3. Webserver (UI)                                       │
│     • Dashboard to view DAGs                             │
│     • Monitor pipeline runs                              │
│     • Trigger manual runs                                │
│                                                          │
│  4. Metadata Database                                    │
│     • Stores DAG runs, task states, logs                 │
│     • Usually PostgreSQL or MySQL                        │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### **Execution Flow:**

```
TIME: 3:00 AM (Scheduled time)
     ↓
┌──────────────────────────────────────────────────────────┐
│  AIRFLOW SCHEDULER (always running in background)        │
│  Checks: "Is it time to run housing_ml_pipeline?"       │
│  Answer: "Yes! Schedule says @daily at 3 AM"            │
└─────────────────┬────────────────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────────────────┐
│  CREATES: DAG Run Instance                               │
│  Run ID: housing_ml_pipeline_2025-10-31T03:00:00        │
│  Status: RUNNING                                         │
└─────────────────┬────────────────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────────────────┐
│  TASK 1: ingest_data                                     │
│  Status: QUEUED → RUNNING                                │
│  Command: python pipeline/stage_01_ingest_data.py        │
│  Start: 3:00:05 AM                                       │
│  End: 3:00:10 AM (5 seconds)                            │
│  Status: SUCCESS ✓                                       │
│  Output: Saved to logs/                                  │
└─────────────────┬────────────────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────────────────┐
│  TASK 2: feature_engineering                             │
│  (Waits for Task 1 to succeed)                          │
│  Status: QUEUED → RUNNING                                │
│  Start: 3:00:11 AM                                       │
│  End: 3:00:14 AM (3 seconds)                            │
│  Status: SUCCESS ✓                                       │
└─────────────────┬────────────────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────────────────┐
│  TASK 3: train_model                                     │
│  Status: QUEUED → RUNNING                                │
│  Start: 3:00:15 AM                                       │
│  End: 3:00:45 AM (30 seconds)                           │
│  Status: SUCCESS ✓                                       │
│  Metrics: R²=82%, RMSE=$48,500                          │
└─────────────────┬────────────────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────────────────┐
│  TASK 4: validate_model                                  │
│  Status: RUNNING                                         │
│  Checks: R² >= 0.75? ✓  RMSE <= $50k? ✓                │
│  Status: SUCCESS ✓                                       │
└─────────────────┬────────────────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────────────────┐
│  DAG Run Complete                                        │
│  Status: SUCCESS                                         │
│  Duration: 45 seconds                                    │
│  Next Run: Tomorrow at 3:00 AM                          │
└──────────────────────────────────────────────────────────┘
```

---

## 🎓 Airflow Concepts Explained

### **Concept 1: DAG (Directed Acyclic Graph)**

**What it is:** Your workflow blueprint

**Example:**
```python
from airflow import DAG
from datetime import datetime

dag = DAG(
    dag_id='my_ml_pipeline',           # Name (unique ID)
    description='My first ML pipeline', # Description
    schedule_interval='@daily',         # When to run
    start_date=datetime(2025, 10, 1),  # When DAG becomes active
    catchup=False,                      # Don't backfill
)
```

**What each setting means:**

| Setting | Example | Simple Explanation |
|---------|---------|-------------------|
| `dag_id` | 'my_ml_pipeline' | Like naming a file |
| `schedule_interval` | '@daily' | How often to run |
| `start_date` | datetime(2025,10,1) | When to start scheduling |
| `catchup` | False | Don't run for missed dates |

**Schedules (Common):**
```python
'@daily'      # Every day at midnight
'@hourly'     # Every hour
'@weekly'     # Every Sunday at midnight
'@monthly'    # 1st of month at midnight
'0 3 * * *'   # Every day at 3 AM (cron format)
'*/15 * * * *' # Every 15 minutes
None          # Manual trigger only
```

---

### **Concept 2: Tasks**

**What:** Individual units of work

**Example: BashOperator (runs shell commands)**
```python
from airflow.operators.bash import BashOperator

task_1 = BashOperator(
    task_id='download_data',           # Unique name
    bash_command='python fetch_data.py', # What to run
    dag=dag,                            # Attach to DAG
)
```

**Example: PythonOperator (runs Python functions)**
```python
from airflow.operators.python import PythonOperator

def process_data():
    print("Processing data...")
    # Your Python code here
    return "success"

task_2 = PythonOperator(
    task_id='process_data',
    python_callable=process_data,  # Function to call
    dag=dag,
)
```

**Comparison:**

| Operator | Use When | Example |
|----------|----------|---------|
| **BashOperator** | Running scripts | `python script.py` |
| **PythonOperator** | Python functions | `process_data()` |
| **EmailOperator** | Sending alerts | Send failure email |
| **SensorOperator** | Waiting for files | Wait for data file |

---

### **Concept 3: Dependencies**

**What:** Defines task order

**Example:**
```python
task_a >> task_b >> task_c

# This means:
# 1. Run task_a
# 2. When task_a succeeds, run task_b
# 3. When task_b succeeds, run task_c
```

**Visual Patterns:**

**Linear (Sequential):**
```python
A >> B >> C

┌───┐    ┌───┐    ┌───┐
│ A │ → │ B │ → │ C │
└───┘    └───┘    └───┘
```

**Fan-out (Parallel):**
```python
A >> [B, C, D]

        ┌─ B ─┐
    A ─┼─ C ─┤
        └─ D ─┘

A runs first, then B, C, D run simultaneously
```

**Fan-in (Join):**
```python
[A, B, C] >> D

┌─ A ─┐
├─ B ─┤─ D
└─ C ─┘

A, B, C run in parallel, D waits for all to finish
```

**Complex:**
```python
A >> B >> [C, D] >> E

┌───┐    ┌───┐    ┌───┐
│ A │ → │ B │ → │ C │ ┐
└───┘    └───┘    └───┘ │
                         ├→ ┌───┐
               ┌───┐    │  │ E │
               │ D │ ───┘  └───┘
               └───┘
```

---

## 🏠 Your ML Pipeline as Airflow DAG

### **Current Setup (DVC):**
```bash
dvc repro  # Runs all stages
```

### **Same Pipeline in Airflow:**

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

# Define DAG
dag = DAG(
    'housing_ml_pipeline',
    schedule_interval='@daily',
    start_date=datetime(2025, 10, 1),
    catchup=False,
)

# Define tasks
ingest = BashOperator(
    task_id='ingest_data',
    bash_command='python pipeline/stage_01_ingest_data.py',
    dag=dag
)

features = BashOperator(
    task_id='engineer_features',
    bash_command='python pipeline/stage_02_feature_engineering.py',
    dag=dag
)

train = BashOperator(
    task_id='train_model',
    bash_command='python pipeline/stage_03_train_model_mlflow.py',
    dag=dag
)

# Define order
ingest >> features >> train
```

**What Airflow adds:**
```
DVC: Runs when you manually type 'dvc repro'

Airflow: Runs automatically every day at 3 AM
         Monitors execution
         Retries on failure
         Alerts on errors
         Visual dashboard
         Execution history
```

---

## 🎯 Simple Examples

### **Example 1: Daily Data Pipeline**

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

dag = DAG(
    'daily_data_pipeline',
    schedule_interval='@daily',  # Every day at midnight
    start_date=datetime(2025, 10, 1),
)

# Task: Download data
download = BashOperator(
    task_id='download',
    bash_command='curl https://api.example.com/data > data.json',
    dag=dag,
)

# Task: Process data
process = BashOperator(
    task_id='process',
    bash_command='python process_data.py',
    dag=dag,
)

# Task: Upload results
upload = BashOperator(
    task_id='upload',
    bash_command='python upload_results.py',
    dag=dag,
)

# Workflow: download → process → upload
download >> process >> upload
```

**What happens:**
```
Every day at 00:00:
  00:01 - Download data from API
  00:05 - Process data (Python script)
  00:10 - Upload results
  00:15 - Done! Sleep until tomorrow
```

---

### **Example 2: ML Pipeline with Validation**

```python
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from datetime import datetime

dag = DAG(
    'ml_with_validation',
    schedule_interval='@weekly',  # Every Sunday
    start_date=datetime(2025, 10, 1),
)

# Train model
def train_model():
    # Training code...
    accuracy = 0.85
    return accuracy

train_task = PythonOperator(
    task_id='train',
    python_callable=train_model,
    dag=dag,
)

# Validate model
def validate_model(**context):
    # Get accuracy from previous task
    ti = context['task_instance']
    accuracy = ti.xcom_pull(task_ids='train')

    print(f"Model accuracy: {accuracy}")

    # Decision: good or bad?
    if accuracy >= 0.80:
        return 'deploy_model'  # Good! Deploy it
    else:
        return 'alert_team'    # Bad! Alert team

validate_task = BranchPythonOperator(
    task_id='validate',
    python_callable=validate_model,
    provide_context=True,
    dag=dag,
)

# Deploy if good
def deploy():
    print("Deploying model to production!")

deploy_task = PythonOperator(
    task_id='deploy_model',
    python_callable=deploy,
    dag=dag,
)

# Alert if bad
def alert():
    print("ALERT: Model quality too low!")

alert_task = PythonOperator(
    task_id='alert_team',
    python_callable=alert,
    dag=dag,
)

# Workflow with branching
train_task >> validate_task >> [deploy_task, alert_task]
```

**Visual:**
```
┌───────┐
│ Train │
└───┬───┘
    │
    ▼
┌──────────┐
│Validate  │
└────┬─────┘
     │
     ├─ If good (accuracy >= 80%) ─→ ┌────────┐
     │                                │ Deploy │
     │                                └────────┘
     │
     └─ If bad (accuracy < 80%) ──→ ┌────────┐
                                     │ Alert  │
                                     └────────┘
```

---

## 📊 Airflow UI (What You'd See)

### **Main Dashboard:**
```
┌─────────────────────────────────────────────────────────┐
│  Apache Airflow                             [Settings]  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  [DAGs] [Datasets] [Admin]                              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  DAG Name              │ Schedule │ Next Run │ Status  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  housing_ml_pipeline   │ @daily   │ Tomorrow │ Success │
│  data_refresh_pipeline │ @hourly  │ 1 hour   │ Running │
│  model_retraining      │ @weekly  │ Sunday   │ Failed  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### **Click on DAG → Graph View:**
```
┌─────────────────────────────────────────────────────────┐
│  housing_ml_pipeline - Graph View                       │
│  Run: 2025-10-31 03:00:00                              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│         ┌──────────────────┐                           │
│         │   ingest_data    │ ✓ Success (5s)           │
│         └────────┬─────────┘                           │
│                  │                                      │
│                  ▼                                      │
│         ┌──────────────────┐                           │
│         │engineer_features │ ✓ Success (3s)           │
│         └────────┬─────────┘                           │
│                  │                                      │
│                  ▼                                      │
│         ┌──────────────────┐                           │
│         │   train_model    │ ✓ Success (30s)          │
│         └────────┬─────────┘                           │
│                  │                                      │
│                  ▼                                      │
│         ┌──────────────────┐                           │
│         │ validate_model   │ ✓ Success (1s)           │
│         └──────────────────┘                           │
│                                                         │
│  Status: All tasks succeeded ✓                         │
│  Duration: 39 seconds                                   │
└─────────────────────────────────────────────────────────┘
```

### **Click on Task → Task Instance Details:**
```
┌─────────────────────────────────────────────────────────┐
│  Task: train_model                                      │
│  Status: Success                                        │
│  Duration: 30.5 seconds                                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  📊 Task Instance Details:                             │
│    Task ID: train_model                                 │
│    Run ID: manual__2025-10-31T03:00:00                 │
│    Start: 2025-10-31 03:00:15                          │
│    End: 2025-10-31 03:00:45                            │
│    Duration: 30.5s                                      │
│    Try Number: 1                                        │
│    Max Tries: 2                                         │
│                                                         │
│  📝 Logs:                                               │
│    [2025-10-31 03:00:15] INFO - Training model...       │
│    [2025-10-31 03:00:20] INFO - Model trained           │
│    [2025-10-31 03:00:21] INFO - R² Score: 0.8207       │
│    [2025-10-31 03:00:21] INFO - RMSE: $48,475          │
│    [2025-10-31 03:00:45] INFO - Task completed         │
│                                                         │
│  🔄 Actions:                                            │
│    [Clear] [Mark Success] [Mark Failed] [Run]          │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete Workflow Example

### **Your ML Pipeline in Airflow (Full Code)**

Save this as `airflow/dags/housing_pipeline.py`:

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

# Settings
default_args = {
    'owner': 'data-science-team',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,
    'email': ['alerts@company.com'],
}

# Create DAG
dag = DAG(
    'housing_price_ml_pipeline',
    default_args=default_args,
    description='Daily ML retraining pipeline',
    schedule_interval='0 3 * * *',  # 3 AM daily
    start_date=datetime(2025, 10, 1),
    catchup=False,
    tags=['ml', 'production', 'housing'],
)

# Task 1: Ingest Data
ingest_data = BashOperator(
    task_id='ingest_data',
    bash_command='cd /path/to/project && python pipeline/stage_01_ingest_data.py',
    dag=dag,
)

# Task 2: Engineer Features
engineer_features = BashOperator(
    task_id='engineer_features',
    bash_command='cd /path/to/project && python pipeline/stage_02_feature_engineering.py',
    dag=dag,
)

# Task 3: Train Model
train_model = BashOperator(
    task_id='train_model',
    bash_command='cd /path/to/project && python pipeline/stage_03_train_model_mlflow.py',
    dag=dag,
)

# Task 4: Validate Model
def validate_model_quality():
    """Check if model is good enough"""
    import json

    with open('/path/to/project/logs/evaluation_report.json') as f:
        report = json.load(f)

    r2 = report['metrics']['r2_score']
    rmse = report['metrics']['rmse']

    print(f"Model Performance: R²={r2:.4f}, RMSE=${rmse:,.0f}")

    # Quality gates
    if r2 < 0.75:
        raise ValueError(f"Model R² too low: {r2:.4f}")
    if rmse > 50000:
        raise ValueError(f"Model RMSE too high: ${rmse:,.0f}")

    print("✓ Model validation passed!")
    return True

validate_model = PythonOperator(
    task_id='validate_model',
    python_callable=validate_model_quality,
    dag=dag,
)

# Task 5: Deploy to Staging
def deploy_to_staging():
    """Promote model to staging environment"""
    print("Deploying model to staging...")
    # Your deployment code here
    print("✓ Model deployed to staging!")
    return "staging"

deploy_staging = PythonOperator(
    task_id='deploy_to_staging',
    python_callable=deploy_to_staging,
    dag=dag,
)

# Define workflow
ingest_data >> engineer_features >> train_model >> validate_model >> deploy_staging
```

---

## 🎯 How This Works (Step-by-Step Example)

**Day 1 - October 31, 2025:**

```
03:00:00 AM - Airflow Scheduler: "Time to run housing_ml_pipeline!"
03:00:01 AM - Creates new DAG Run
03:00:02 AM - Queues task: ingest_data
03:00:03 AM - Starts task: ingest_data
03:00:08 AM - ✓ ingest_data SUCCESS (5 sec)
03:00:09 AM - Queues task: engineer_features (depends on ingest_data ✓)
03:00:10 AM - Starts task: engineer_features
03:00:13 AM - ✓ engineer_features SUCCESS (3 sec)
03:00:14 AM - Queues task: train_model
03:00:15 AM - Starts task: train_model
03:00:45 AM - ✓ train_model SUCCESS (30 sec)
              Metrics: R²=0.8207, RMSE=$48,475
03:00:46 AM - Queues task: validate_model
03:00:47 AM - Starts task: validate_model
              Checks: R² >= 0.75? ✓  RMSE <= $50k? ✓
03:00:48 AM - ✓ validate_model SUCCESS
03:00:49 AM - Queues task: deploy_to_staging
03:00:50 AM - Starts task: deploy_to_staging
03:00:55 AM - ✓ deploy_to_staging SUCCESS
03:00:56 AM - DAG Run COMPLETE ✅
              Total duration: 53 seconds
              All 5 tasks succeeded
              Next run: November 1 at 3:00 AM
```

**Day 2 - November 1, 2025** (Automatic!)

```
03:00:00 AM - Airflow: "Time to run again!"
03:00:01 AM - Creates new DAG Run
              ... (same process)
```

**Day 3 - November 2, 2025** (Something fails)

```
03:00:00 AM - Pipeline starts
03:00:15 AM - Starts task: train_model
03:00:45 AM - ✓ train_model SUCCESS
              But... R²=0.72 (below 0.75 threshold!)
03:00:46 AM - Starts task: validate_model
03:00:47 AM - ✗ validate_model FAILED!
              Error: "Model R² too low: 0.72"
03:00:48 AM - Pipeline STOPPED ❌
03:00:49 AM - Email sent to: alerts@company.com
              Subject: "Airflow Task Failed: validate_model"
              Body: "Check the logs!"

You wake up, see email, investigate, fix the issue.
```

---

## 📊 Airflow vs DVC vs Manual

| Feature | Manual | DVC | Airflow |
|---------|--------|-----|---------|
| **Scheduling** | ❌ Manual | ❌ Manual (use cron) | ✅ Built-in |
| **Visual UI** | ❌ No | ❌ No | ✅ Yes |
| **Retry on Failure** | ❌ Manual | ❌ Manual | ✅ Automatic |
| **Email Alerts** | ❌ Manual | ❌ Manual | ✅ Built-in |
| **Execution History** | ❌ No | ⚠️ Partial (dvc.lock) | ✅ Complete |
| **Monitor Running** | ❌ No | ❌ No | ✅ Live view |
| **Smart Caching** | ❌ No | ✅ Yes | ❌ No |
| **Complexity** | ✅ Simple | ✅ Moderate | ⚠️ Complex |
| **Best for** | Learning | Development | Production |

---

## 🎓 Key Airflow Concepts (Interview Prep)

### **1. DAG (Workflow Definition)**

**Question:** "What is a DAG?"

**Answer:**
> "A DAG is a Directed Acyclic Graph that defines a workflow. In my housing price prediction project, the DAG defines three tasks - data ingestion, feature engineering, and model training - that must run in sequence. It's directed because tasks have dependencies, and acyclic because there are no loops. I can schedule the DAG to run daily at 3 AM for automated retraining."

### **2. Tasks and Operators**

**Question:** "What operators have you used?"

**Answer:**
> "I've used BashOperator for running Python scripts like data ingestion and feature engineering, and PythonOperator for custom validation logic that checks model quality thresholds. I also used BranchPythonOperator for conditional logic - if model validation passes, promote to staging; if fails, alert the team."

### **3. Dependencies and Scheduling**

**Question:** "How do you handle task dependencies?"

**Answer:**
> "I use Airflow's >> operator to define dependencies. For example, `ingest >> features >> train` ensures data is ingested before feature engineering, and features are ready before training. Airflow's scheduler monitors these dependencies and only runs downstream tasks after upstream tasks succeed."

### **4. Error Handling**

**Question:** "How do you handle failures?"

**Answer:**
> "I configure retries in the DAG default_args - typically 2 retries with a 5-minute delay. If a task fails after retries, Airflow marks it as failed and sends an email alert. I also implement quality gates using Python operators that validate model performance and stop the pipeline if metrics don't meet thresholds."

---

## 🎯 Practical Use Cases

### **Use Case 1: Daily Retraining**

```python
# Retrains model every day with fresh data
schedule_interval='@daily'

# Workflow:
# Day 1: Train on data up to Oct 31
# Day 2: Train on data up to Nov 1
# Day 3: Train on data up to Nov 2
# ...
```

### **Use Case 2: Weekly Model Comparison**

```python
# Every Sunday, train 3 different models and compare
schedule_interval='@weekly'

# Tasks:
train_rf_100 >> validate_rf_100
train_rf_200 >> validate_rf_200
train_gb >> validate_gb
[validate_rf_100, validate_rf_200, validate_gb] >> compare_models >> deploy_best
```

### **Use Case 3: Event-Driven Pipeline**

```python
# Run when new data file appears
from airflow.sensors.filesystem import FileSensor

wait_for_data = FileSensor(
    task_id='wait_for_new_data',
    filepath='/data/incoming/*.csv',
    poke_interval=60,  # Check every 60 seconds
)

wait_for_data >> ingest_data >> ...
```

---

## ✅ Summary

### **What is Airflow?**
A workflow scheduler that:
- ✅ Runs pipelines automatically (scheduled)
- ✅ Handles dependencies (task order)
- ✅ Retries on failure
- ✅ Sends alerts
- ✅ Provides visual dashboard
- ✅ Tracks execution history

### **Core Components:**
1. **DAG** - Workflow definition
2. **Tasks** - Individual steps
3. **Operators** - Types of tasks (Bash, Python, Email)
4. **Dependencies** - Task order (>>)
5. **Scheduler** - Runs DAGs on schedule
6. **UI** - Visual dashboard

### **When to Use:**
- ✅ Production ML pipelines
- ✅ Scheduled retraining
- ✅ Complex workflows with many steps
- ✅ Need monitoring and alerts
- ✅ Team collaboration

---

## 🎯 For Your Portfolio

**You can say:**

> "I designed my ML pipeline to be Airflow-ready. Each stage is a separate script that can be orchestrated by Airflow using BashOperators. The pipeline includes data validation, feature engineering, model training with MLflow tracking, and automated quality gates. While I currently use DVC for local development, the modular design allows easy migration to Airflow for production scheduling with built-in monitoring, retries, and alerting."

**Key points:**
- ✅ Understand Airflow concepts (DAG, tasks, operators)
- ✅ Know when to use it (production, scheduling)
- ✅ Pipeline is Airflow-ready (modular scripts)
- ✅ Can explain benefits (monitoring, scheduling, retries)

---

**You now understand Airflow!** Even without running it locally, you know the concepts and can discuss it in interviews. 🎓🚀
