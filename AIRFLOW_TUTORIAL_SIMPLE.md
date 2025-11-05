# Apache Airflow Tutorial - Super Simple Explanation

## 📚 Table of Contents
1. [What is Airflow?](#what-is-airflow)
2. [What are DAGs?](#what-are-dags)
3. [Scheduling ML Training](#scheduling-ml-training)
4. [Pipeline Modularization](#pipeline-modularization)
5. [Your Housing Pipeline Explained](#your-housing-pipeline-explained)
6. [How to Use It](#how-to-use-it)

---

## What is Airflow?

###  Real-World Analogy

**Think of Airflow like a smart robot assistant that runs your ML pipeline automatically.**

Imagine you're a chef with a recipe book:
- **Without Airflow**: You have to manually check your recipe book every day, remember each step, and do everything yourself
- **With Airflow**: You have a robot chef that:
  - Reads your recipes
  - Knows when to start cooking
  - Follows each step in order
  - Tells you if something goes wrong
  - Works while you sleep!

### What Airflow Actually Does

Airflow is a **workflow automation tool** that:

1. **Schedules tasks** - "Run this ML training every day at midnight"
2. **Manages dependencies** - "Don't start training until data is ready"
3. **Monitors execution** - "Send me an alert if training fails"
4. **Provides a UI** - "Show me a visual dashboard of what's happening"
5. **Handles retries** - "If data fetch fails, try again 3 times"

### Why Do ML Teams Use Airflow?

**Problem**: Machine learning models need regular retraining
- New data arrives daily
- Model performance degrades over time
- Manual retraining is tedious and error-prone

**Solution**: Airflow automates the entire process
- Runs your training automatically
- Handles failures gracefully
- Keeps track of what ran when
- Makes ML ops hands-free!

---

## What are DAGs?

### The Simple Explanation

**DAG** = Directed Acyclic Graph (fancy name for a simple concept)

Think of a DAG as a **flowchart** or **recipe** that shows:
- What tasks to do
- In what order
- What depends on what

### Breaking Down "DAG"

**Directed** = Tasks flow in one direction (like a recipe - you don't cook the pasta before boiling water)

```
Task A  →  Task B  →  Task C
```

**Acyclic** = No loops (you don't go back to previous steps)

```
✅ Allowed:     A → B → C
❌ Not allowed: A → B → C → A (loop!)
```

**Graph** = Visual representation of tasks and their connections

### Visual Example: Morning Coffee

```
       ┌──────────────┐
       │  Boil Water  │
       └──────┬───────┘
              │
              ▼
       ┌──────────────┐
       │  Grind Beans │
       └──────┬───────┘
              │
       ┌──────┴───────┐
       │              │
       ▼              ▼
┌────────────┐  ┌─────────────┐
│ Brew Coffee│  │  Heat Milk  │
└─────┬──────┘  └──────┬──────┘
      │                │
      └────────┬───────┘
               ▼
        ┌────────────┐
        │ Pour & Enjoy│
        └────────────┘
```

This is a DAG! Each box is a **task**, arrows show **dependencies**.

### Your ML Pipeline DAG

```
┌─────────────┐
│ Ingest Data │  ← Fetch housing data
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│Feature Engineer │  ← Create ML features
└───────┬─────────┘
        │
        ▼
┌─────────────┐
│Train Model  │  ← Train Random Forest
└──────┬──────┘
       │
       ▼
┌──────────────┐
│Validate Model│  ← Check if model is good
└──────┬───────┘
       │
   ┌───┴───┐
   │       │
   ▼       ▼
┌────┐   ┌────┐
│ ✅ │   │ ❌ │  ← Success or Failure path
└────┘   └────┘
```

---

## Scheduling ML Training

### Why Schedule?

**Scenario**: Your housing price model

- **Monday**: Model trained, R² = 82% (good!)
- **1 week later**: New housing data arrives, model performance drops to 75%
- **2 weeks later**: Even more drift, performance now 70%
- **1 month later**: Model is outdated and inaccurate

**Solution**: Automatic retraining!

### Airflow Scheduling Syntax

Airflow uses **cron expressions** (don't worry, I'll explain!)

#### Common Schedules

| Expression | Meaning | Example Use Case |
|------------|---------|------------------|
| `@daily` | Every day at midnight | Retrain with yesterday's data |
| `@weekly` | Every Sunday at midnight | Weekly model updates |
| `@monthly` | First day of month | Monthly full retraining |
| `@hourly` | Every hour | Real-time model updates |
| `None` | Manual only | Experimental runs |

#### Custom Schedules (Cron)

Format: `minute hour day month day_of_week`

```python
# Every day at 3 AM
schedule_interval='0 3 * * *'

# Every 6 hours
schedule_interval='0 */6 * * *'

# Monday to Friday at 9 AM
schedule_interval='0 9 * * 1-5'

# First day of every month at noon
schedule_interval='0 12 1 * *'
```

### Your Housing Pipeline Schedule

In `housing_ml_pipeline.py`:

```python
schedule_interval='@daily'  # Runs every day at midnight
```

**What this means**:
- Every night at 12:00 AM, Airflow wakes up
- It runs your entire ML pipeline
- By morning, you have a fresh model trained on latest data!

### Schedule in Action

```
Day 1 (Today):
  00:00 → Pipeline starts
  00:05 → Data ingested (20,640 houses)
  00:10 → Features engineered (15 features)
  00:40 → Model trained (R² = 82%)
  00:41 → Model validated & promoted
  00:42 → ✅ Success notification

Day 2 (Tomorrow):
  00:00 → Pipeline starts again automatically
  [Same process repeats]

Day 3, 4, 5...
  [Keeps running every night, forever!]
```

---

## Pipeline Modularization

### What is Modularization?

**Think LEGO blocks**: Each block does one thing, but combined they build something amazing.

### Without Modularization (Bad! ❌)

**One giant script** (`train_everything.py`):

```python
# 1000 lines of mixed code
def do_everything():
    # Fetch data
    # Clean data
    # Engineer features
    # Train model
    # Evaluate model
    # Save model
    # Send email
    # Update database
    # Generate report
    # Deploy model
    # ... (all in one function!)
```

**Problems**:
- Can't test individual parts
- Hard to debug
- Can't reuse code
- Can't run parts independently
- One bug breaks everything
- Can't skip expensive steps

### With Modularization (Good! ✅)

**Separate tasks**, each with one responsibility:

```python
# Stage 1: Data Ingestion
def ingest_data():
    fetch_housing_data()
    validate_quality()
    save_clean_data()

# Stage 2: Feature Engineering
def engineer_features():
    load_clean_data()
    create_derived_features()
    encode_categories()
    scale_numbers()

# Stage 3: Train Model
def train_model():
    load_features()
    train_random_forest()
    log_to_mlflow()

# ... separate, focused functions
```

**Benefits**:
- **Test individually**: "Did feature engineering work?"
- **Debug easily**: "Training failed? Check only training code"
- **Reuse**: Use `ingest_data()` in multiple pipelines
- **Run selectively**: "Just retrain, skip data fetch"
- **Parallel execution**: Run independent tasks at same time
- **Cache results**: "Data unchanged? Skip ingestion!"

### Your Modularized Pipeline

You have **3 separate stage files**:

```
pipeline/
├── stage_01_ingest_data.py          # 🎯 One job: Get data
├── stage_02_feature_engineering.py  # 🎯 One job: Make features
└── stage_03_train_model_mlflow.py   # 🎯 One job: Train model
```

Each can be:
- Run independently: `python pipeline/stage_02_feature_engineering.py`
- Tested separately
- Modified without breaking others
- Reused in different pipelines

### Real-World Example

**Scenario**: Your training suddenly fails

**Without modularization**:
```
❌ Error in line 847 of train_everything.py
   (Is it data? features? training? Who knows!)
   Must debug 1000 lines of code
```

**With modularization**:
```
✅ Stage 1 (ingest_data): Success ✓
✅ Stage 2 (feature_engineering): Success ✓
❌ Stage 3 (train_model): Failed ✗
   → Problem is in training code only
   → Check stage_03_train_model_mlflow.py
   → Only ~200 lines to debug
```

---

## Your Housing Pipeline Explained

Let's walk through YOUR actual pipeline: `housing_ml_pipeline.py`

### The DAG Definition

```python
with DAG(
    dag_id='housing_price_ml_pipeline',
    schedule_interval='@daily',  # ← Runs every day
    start_date=days_ago(1),
    catchup=False,  # ← Don't backfill old dates
) as dag:
```

**Translation**:
- Name: `housing_price_ml_pipeline`
- Runs: Every day at midnight
- Started: Yesterday (so it can run tonight!)
- Don't run for historical dates

### Task 1: Data Ingestion

```python
task_ingest_data = BashOperator(
    task_id='ingest_data',
    bash_command='cd /path/to/project && python pipeline/stage_01_ingest_data.py',
)
```

**What it does**:
- Fetches California Housing dataset (20,640 houses)
- Checks for missing values, duplicates, outliers
- Saves: `data/raw/housing_data.csv` and `data/processed/housing_processed.csv`

**Duration**: ~5 seconds

### Task 2: Feature Engineering

```python
task_feature_engineering = BashOperator(
    task_id='feature_engineering',
    bash_command='cd /path/to/project && python pipeline/stage_02_feature_engineering.py',
)
```

**What it does**:
- Creates derived features (rooms_per_household, etc.)
- One-hot encodes ocean_proximity
- Scales all numbers with StandardScaler
- Saves: Features + scaler/encoder artifacts

**Duration**: ~3 seconds

### Task 3: Model Training

```python
task_train_model = BashOperator(
    task_id='train_model',
    bash_command='cd /path/to/project && python pipeline/stage_03_train_model_mlflow.py',
)
```

**What it does**:
- Trains Random Forest (275 trees, max_depth=20)
- Logs everything to MLflow
- Registers model in MLflow registry
- Expected: R² ~82%, RMSE ~$48,500

**Duration**: ~30 seconds

### Task 4: Model Validation (Quality Gate)

```python
def validate_model_performance(**context):
    # Load evaluation metrics
    metrics = load_metrics()
    r2 = metrics['r2_score']
    rmse = metrics['rmse']

    # Check thresholds
    if r2 < 0.75 or rmse > 50000:
        return 'send_failure_alert'  # ← Bad model!
    else:
        return 'promote_to_staging'   # ← Good model!

task_validate = BranchPythonOperator(
    task_id='validate_model',
    python_callable=validate_model_performance,
)
```

**What it does**:
- Reads: `logs/evaluation_report.json`
- Checks if model is good enough:
  - R² must be ≥ 0.75 (75% accuracy)
  - RMSE must be ≤ $50,000
- **Branches** to either success or failure path

**This is a QUALITY GATE** - prevents bad models from reaching production!

### Task 5a: Promote to Staging (Success Path)

```python
def promote_model_to_staging(**context):
    # Get latest model from registry
    latest_model = registry.get_latest_model()

    # Promote to staging
    registry.transition_model_stage(
        version_id=latest_model['version_id'],
        new_stage='staging',
    )

task_promote = PythonOperator(
    task_id='promote_to_staging',
    python_callable=promote_model_to_staging,
)
```

**What it does**:
- Updates model registry
- Marks model as "staging" (ready for testing)
- Records promotion timestamp

**Only runs if**: Model passed validation

### Task 5b: Send Failure Alert (Failure Path)

```python
def send_failure_alert(**context):
    # Get metrics
    r2 = context['task_instance'].xcom_pull(key='r2_score')
    rmse = context['task_instance'].xcom_pull(key='rmse')

    # Alert team
    print(f"❌ MODEL VALIDATION FAILED!")
    print(f"   R²: {r2}, RMSE: ${rmse}")

    # In production: Send to Slack/PagerDuty/Email

task_alert = PythonOperator(
    task_id='send_failure_alert',
    python_callable=send_failure_alert,
)
```

**What it does**:
- Sends urgent alert
- Includes model metrics
- Stops pipeline (no bad model deployed!)

**Only runs if**: Model failed validation

### Task 6: Success Notification

```python
def send_success_notification(**context):
    # Gather all info
    version_id = context['ti'].xcom_pull(task_ids='promote_to_staging')
    r2 = context['ti'].xcom_pull(task_ids='validate_model', key='r2_score')
    rmse = context['ti'].xcom_pull(task_ids='validate_model', key='rmse')

    # Send summary
    print(f"✅ Pipeline Success!")
    print(f"   Model {version_id} in staging")
    print(f"   R²: {r2:.4f}, RMSE: ${rmse:,.2f}")

task_notify = PythonOperator(
    task_id='send_success_notification',
    python_callable=send_success_notification,
)
```

**What it does**:
- Celebrates! 🎉
- Summarizes results
- Notifies team of successful retraining

### Task Dependencies (The Flow)

```python
# Main pipeline flow
task_ingest_data >> task_feature_engineering >> task_train_model >> task_validate_model

# Conditional branching
task_validate_model >> task_promote_staging >> task_notify_success  # Success path
task_validate_model >> task_send_failure_alert                       # Failure path
```

**Visual**:

```
     Ingest Data
          │
          ▼
  Feature Engineering
          │
          ▼
     Train Model
          │
          ▼
    Validate Model
          │
     ┌────┴────┐
     │         │
     ▼         ▼
  Promote   Alert
     │
     ▼
  Notify
```

---

## How to Use It

### Step 1: Start Airflow

```bash
# Start Airflow (webserver + scheduler)
bash start_airflow.sh

# Output:
# ✅ Airflow started!
# Open http://localhost:8080
```

### Step 2: Access Airflow UI

1. Open browser: `http://localhost:8080`
2. Login:
   - Username: `admin`
   - Password: `admin`

### Step 3: Find Your DAG

1. You'll see the **DAGs** page
2. Look for: `housing_price_ml_pipeline`
3. Toggle the switch to **enable** it

### Step 4: Trigger a Test Run

**Option A: Manual Trigger**
1. Click the ▶️ play button on the right
2. Select "Trigger DAG"
3. Watch it run in real-time!

**Option B: Wait for Schedule**
- If it's enabled, it will run automatically at midnight

### Step 5: Monitor Execution

**Graph View** (Recommended):
1. Click on the DAG name
2. Click "Graph" tab
3. See visual representation of tasks
4. Colors indicate status:
   - 🟢 Green = Success
   - 🔴 Red = Failed
   - 🟡 Yellow = Running
   - ⚪ White = Not started

**Grid View**:
- See history of all runs
- Click any run to see details

**Logs**:
- Click any task box
- Click "Log" to see detailed output

### Step 6: Check Results

After successful run:

1. **MLflow UI** (http://localhost:5000):
   - See new experiment logged
   - Check metrics: R², RMSE, etc.
   - View model artifacts

2. **Model Registry**:
   ```bash
   cat models/model_registry/registry.json
   ```
   - See model version
   - Check stage (should be "staging")

3. **Evaluation Report**:
   ```bash
   cat logs/evaluation_report.json
   ```
   - See detailed metrics
   - Check feature importance

### Real-World Usage Scenarios

**Scenario 1: Daily Retraining**
- Enable DAG
- Let it run automatically every night
- Check dashboard once a week

**Scenario 2: Experiment**
- Make changes to `config/config.yaml`
- Trigger manual run
- Compare results in MLflow

**Scenario 3: Debugging**
- Pipeline failed? Check Airflow logs
- Find which task failed
- Fix and rerun from that task

### Stop Airflow

```bash
bash stop_airflow.sh
```

---

## Key Takeaways

### 1. Airflow = Automation Robot
- Runs your ML pipeline automatically
- Handles scheduling, retries, monitoring
- Makes ML ops hands-free

### 2. DAGs = Flowcharts
- Visual representation of your pipeline
- Shows tasks and dependencies
- Ensures correct execution order

### 3. Scheduling = Set It and Forget It
- `@daily` = runs every night
- `@weekly` = runs every Sunday
- Or custom cron expressions

### 4. Modularization = LEGO Blocks
- Each task does one thing
- Easy to test, debug, reuse
- Can run independently

### 5. Your Pipeline = Production-Ready
- **7 tasks** working together
- **Quality gates** prevent bad models
- **Conditional logic** (success/failure paths)
- **Monitoring** and **alerts**

---

## Next Steps

1. **✅ Start Airflow**: `bash start_airflow.sh`
2. **✅ Enable DAG**: Toggle switch in UI
3. **✅ Trigger test run**: Click ▶️ button
4. **✅ Watch it run**: See tasks turn green!
5. **✅ Check MLflow**: View logged metrics
6. **🎉 Celebrate**: You just automated ML ops!

---

## Common Questions

**Q: What if a task fails?**
A: Airflow will retry (configured in DAG), then send failure alert if all retries fail.

**Q: Can I skip a task?**
A: Yes! Mark it as "skipped" in the UI, or use branching logic.

**Q: Can I run tasks in parallel?**
A: Yes! Tasks without dependencies run in parallel automatically.

**Q: How do I change the schedule?**
A: Edit `schedule_interval` in `housing_ml_pipeline.py`.

**Q: Can I run just one task?**
A: Yes! Click the task → "Clear" → "Downstream" → Run.

**Q: Where are logs stored?**
A: `airflow/logs/` directory, organized by DAG/task/run.

---

## Congratulations! 🎉

You now understand:
- ✅ What Airflow is and why it's used
- ✅ How DAGs represent pipelines
- ✅ How to schedule ML training automatically
- ✅ Why modularization matters
- ✅ How your specific pipeline works
- ✅ How to use the Airflow UI

**You're ready to automate your ML pipelines like a pro!** 🚀
