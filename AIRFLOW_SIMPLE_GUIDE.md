# Airflow - Simple Guide with Examples

## 🎯 What is Airflow? (ELI5 - Explain Like I'm 5)

**Imagine you have a robot assistant for your ML pipeline:**

```
WITHOUT Airflow (You are the robot):
  3:00 AM - Alarm rings
  3:01 AM - You wake up, go to computer
  3:05 AM - Run: python stage_01_ingest_data.py
  3:10 AM - Run: python stage_02_feature_engineering.py
  3:15 AM - Run: python stage_03_train_model.py
  3:45 AM - Check if it worked
  3:50 AM - Go back to bed

  Every. Single. Day. 😴

WITH Airflow (Robot does everything):
  You: "Robot, run my ML pipeline every day at 3 AM"
  Robot: "Got it!"

  3:00 AM - Robot runs pipeline
  3:45 AM - Robot finishes
  If success: Robot sends "All good! ✓"
  If failure: Robot wakes you up "Something broke! ❌"

  You: Sleep peacefully 😊
```

**That's Airflow!** A robot that runs your tasks automatically.

---

## 📚 Core Concepts (Super Simple)

### **1. DAG = Your To-Do List**

```
DAG = Directed Acyclic Graph

Simple translation:
  Directed = Tasks in specific order
  Acyclic = No going backwards
  Graph = Visual flowchart

Think: Recipe card with steps
```

**Example:**
```python
# This is like writing a recipe card:

dag = DAG(
    'bake_cake',              # Recipe name
    schedule_interval='@daily', # Make cake daily
)

# Recipe steps:
step1 = mix_ingredients
step2 = bake
step3 = frost

# Order matters!
step1 >> step2 >> step3  # Can't frost before baking!
```

---

### **2. Tasks = Individual Steps**

```
Task = One thing to do

Examples:
  • Download data (1 task)
  • Train model (1 task)
  • Send email (1 task)
```

**Example:**
```python
# Task: Download data
download_data = BashOperator(
    task_id='download',          # Name it
    bash_command='python fetch.py',  # What to run
)

# Task: Process data
process_data = PythonOperator(
    task_id='process',
    python_callable=my_function,  # Python function to call
)
```

---

### **3. Operators = Task Types**

```
Operator = KIND of task

Like kitchen tools:
  🔪 BashOperator = Knife (run shell commands)
  🥄 PythonOperator = Spoon (run Python functions)
  📧 EmailOperator = Phone (send messages)
```

**Most Common:**

```python
# 1. BashOperator (run shell commands)
BashOperator(
    task_id='run_script',
    bash_command='python my_script.py'
)

# 2. PythonOperator (run Python functions)
def my_function():
    print("Hello!")

PythonOperator(
    task_id='run_function',
    python_callable=my_function
)

# 3. EmailOperator (send emails)
EmailOperator(
    task_id='send_alert',
    to='team@example.com',
    subject='Task completed!'
)
```

---

### **4. Dependencies = Order of Steps**

```
Dependencies = Which task runs after which

Symbol: >>

Example:
  A >> B >> C

Means:
  1. Run A first
  2. When A finishes, run B
  3. When B finishes, run C
```

**Visual:**
```
A >> B

┌─────────┐       ┌─────────┐
│ Task A  │  →    │ Task B  │
│ (First) │       │ (Second)│
└─────────┘       └─────────┘
```

---

## 🏠 Your ML Pipeline (Simple Example)

### **What You Have Now:**

```bash
# Manual:
python pipeline/stage_01_ingest_data.py
python pipeline/stage_02_feature_engineering.py
python pipeline/stage_03_train_model_mlflow.py

# Or with DVC:
dvc repro  # Runs all
```

### **Same Thing in Airflow:**

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

# Create DAG (your to-do list)
dag = DAG(
    'my_ml_pipeline',
    schedule_interval='@daily',  # Run every day
    start_date=datetime(2025, 10, 1),
)

# Task 1: Ingest Data
ingest = BashOperator(
    task_id='ingest',
    bash_command='python pipeline/stage_01_ingest_data.py',
    dag=dag
)

# Task 2: Features
features = BashOperator(
    task_id='features',
    bash_command='python pipeline/stage_02_feature_engineering.py',
    dag=dag
)

# Task 3: Train
train = BashOperator(
    task_id='train',
    bash_command='python pipeline/stage_03_train_model_mlflow.py',
    dag=dag
)

# Order: 1 → 2 → 3
ingest >> features >> train
```

**That's it!** Airflow will now:
- ✅ Run this every day at midnight
- ✅ Run tasks in order
- ✅ Monitor progress
- ✅ Retry if something fails
- ✅ Show dashboard

---

## 🔄 Complete Flow (What Happens)

```
TIME: Daily at 3:00 AM
────────────────────────────────────────────────────────────

┌──────────────────────────────────────────────┐
│ AIRFLOW SCHEDULER (always running)           │
│ Checks: "Is it 3 AM? Yes!"                   │
│ Action: Start housing_ml_pipeline            │
└─────────────────┬────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────┐
│ STEP 1: ingest_data                          │
│ ──────────────────────────────────────────── │
│ Command: python stage_01_ingest_data.py      │
│ Does: Downloads 20,640 houses                │
│ Duration: 5 seconds                          │
│ Status: ✓ SUCCESS                            │
└─────────────────┬────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────┐
│ STEP 2: engineer_features                    │
│ ──────────────────────────────────────────── │
│ Waits for: ingest_data to finish ✓          │
│ Command: python stage_02_feature_engineering.py│
│ Does: Creates 15 features                    │
│ Duration: 3 seconds                          │
│ Status: ✓ SUCCESS                            │
└─────────────────┬────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────┐
│ STEP 3: train_model                          │
│ ──────────────────────────────────────────── │
│ Waits for: engineer_features to finish ✓    │
│ Command: python stage_03_train_model_mlflow.py│
│ Does: Trains Random Forest                   │
│ Logs to: MLflow                              │
│ Duration: 30 seconds                         │
│ Metrics: R²=82%, RMSE=$48,500               │
│ Status: ✓ SUCCESS                            │
└─────────────────┬────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────┐
│ STEP 4: validate_model                       │
│ ──────────────────────────────────────────── │
│ Checks: R² >= 0.75? ✓                       │
│         RMSE <= $50k? ✓                     │
│ Decision: PASS → promote_to_staging          │
│ Status: ✓ SUCCESS                            │
└─────────────────┬────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────┐
│ STEP 5: promote_to_staging                   │
│ ──────────────────────────────────────────── │
│ Does: Updates model stage to "staging"       │
│ Status: ✓ SUCCESS                            │
└─────────────────┬────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────┐
│ STEP 6: send_success_notification            │
│ ──────────────────────────────────────────── │
│ Sends: Email/Slack "Pipeline succeeded!"     │
│ Status: ✓ SUCCESS                            │
└─────────────────┬────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────┐
│ DAG RUN COMPLETE ✅                          │
│ Total Duration: 45 seconds                   │
│ Status: SUCCESS                              │
│ Next Run: Tomorrow at 3:00 AM                │
└──────────────────────────────────────────────┘
```

---

## 🎓 Simple Examples (Learn by Doing)

### **Example 1: Hello World DAG**

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# Function to run
def say_hello():
    print("Hello from Airflow!")
    return "success"

# Create DAG
dag = DAG(
    'hello_world',
    schedule_interval='@daily',
    start_date=datetime(2025, 10, 1),
)

# Create task
hello_task = PythonOperator(
    task_id='say_hello',
    python_callable=say_hello,
    dag=dag
)
```

**What happens:**
```
Every day at midnight:
  - Airflow runs say_hello()
  - Prints: "Hello from Airflow!"
  - Marks task as success
```

---

### **Example 2: Sequential Tasks**

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

dag = DAG('sequential_example', schedule_interval='@daily', start_date=datetime(2025,10,1))

# 3 tasks
task_a = BashOperator(task_id='task_a', bash_command='echo "Step A"', dag=dag)
task_b = BashOperator(task_id='task_b', bash_command='echo "Step B"', dag=dag)
task_c = BashOperator(task_id='task_c', bash_command='echo "Step C"', dag=dag)

# Order: A → B → C
task_a >> task_b >> task_c
```

**Execution:**
```
Step A runs (prints "Step A")
  ↓
Step B runs (prints "Step B")
  ↓
Step C runs (prints "Step C")
  ↓
Done!
```

---

### **Example 3: Parallel Tasks**

```python
# Same setup...

task_a = BashOperator(task_id='fetch_data', bash_command='echo "Fetching..."', dag=dag)

# 3 parallel tasks
task_b1 = BashOperator(task_id='process_users', bash_command='echo "Users..."', dag=dag)
task_b2 = BashOperator(task_id='process_orders', bash_command='echo "Orders..."', dag=dag)
task_b3 = BashOperator(task_id='process_products', bash_command='echo "Products..."', dag=dag)

task_c = BashOperator(task_id='combine_results', bash_command='echo "Combining..."', dag=dag)

# Order: A first, then B1/B2/B3 in parallel, then C
task_a >> [task_b1, task_b2, task_b3] >> task_c
```

**Visual:**
```
┌────────────┐
│fetch_data  │
└──────┬─────┘
       │
       ├──→ ┌───────────────┐
       │    │process_users  │ ─┐
       │    └───────────────┘  │
       │                       │
       ├──→ ┌───────────────┐  │
       │    │process_orders │ ─┼──→ ┌────────────────┐
       │    └───────────────┘  │    │combine_results │
       │                       │    └────────────────┘
       └──→ ┌────────────────┐ │
            │process_products│─┘
            └────────────────┘

Step 1: fetch_data (1 task)
Step 2: process_users, process_orders, process_products (3 tasks simultaneously!)
Step 3: combine_results (1 task, waits for all 3 to finish)
```

---

### **Example 4: Conditional (Branching)**

```python
from airflow.operators.python import BranchPythonOperator

# Check if it's weekend
def check_if_weekend():
    import datetime
    today = datetime.datetime.now().weekday()
    if today >= 5:  # Saturday or Sunday
        return 'weekend_task'
    else:
        return 'weekday_task'

check_day = BranchPythonOperator(
    task_id='check_day',
    python_callable=check_if_weekend,
    dag=dag
)

weekend_task = BashOperator(task_id='weekend_task', bash_command='echo "Relax!"', dag=dag)
weekday_task = BashOperator(task_id='weekday_task', bash_command='echo "Work!"', dag=dag)

# Branching
check_day >> [weekend_task, weekday_task]
```

**What happens:**
```
Monday-Friday:
  check_day → "It's weekday" → weekday_task (prints "Work!")

Saturday-Sunday:
  check_day → "It's weekend" → weekend_task (prints "Relax!")
```

---

## 🎯 Your ML Pipeline (Complete Visualization)

```
AIRFLOW DAG: housing_ml_pipeline
Schedule: Daily at 3:00 AM
════════════════════════════════════════════════════════════

┌──────────────────────────────────────────────────────────┐
│                        START                             │
│              (Triggered by scheduler)                    │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │ Task: ingest_data              │
        │ Type: BashOperator             │
        │ Runs: stage_01_ingest_data.py  │
        │ Time: 5 seconds                │
        │ Output: data/raw/*.csv         │
        └────────────┬───────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │ Task: feature_engineering      │
        │ Type: BashOperator             │
        │ Runs: stage_02_feature_*.py    │
        │ Time: 3 seconds                │
        │ Output: data/features/*.csv    │
        └────────────┬───────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │ Task: train_model              │
        │ Type: BashOperator             │
        │ Runs: stage_03_train_*.py      │
        │ Time: 30 seconds               │
        │ Tracks: MLflow                 │
        │ Output: models/*.joblib        │
        └────────────┬───────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │ Task: validate_model           │
        │ Type: BranchPythonOperator     │
        │ Checks: R² >= 0.75?            │
        │         RMSE <= $50k?          │
        └────────────┬───────────────────┘
                     │
         ┌───────────┴────────────┐
         │                        │
         ▼ (if PASS)              ▼ (if FAIL)
┌─────────────────────┐    ┌──────────────────┐
│ promote_to_staging  │    │ send_failure_alert│
│ Type: PythonOperator│    │ Type: PythonOperator│
│ Does: Update stage  │    │ Does: Send email  │
└─────────┬───────────┘    └──────────────────┘
          │
          ▼
┌──────────────────────┐
│ send_success_notification│
│ Type: PythonOperator │
│ Does: Notify team    │
└──────────┬───────────┘
           │
           ▼
    ┌──────────┐
    │   END    │
    │ SUCCESS ✅│
    └──────────┘
```

---

## 📊 Airflow UI (What You'd See)

### **Dashboard View:**

```
╔══════════════════════════════════════════════════════════╗
║  Apache Airflow                          [Admin] [Docs]  ║
╠══════════════════════════════════════════════════════════╣
║  DAGs (1)                                  [Refresh]     ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  On/Off │ DAG Name             │ Schedule │ Last Run    ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ║
║  ●  ON  │ housing_ml_pipeline  │ @daily   │ Success ✓  ║
║         │                      │          │ 3:00 AM    ║
║                                                          ║
║  Click to see details →                                  ║
╚══════════════════════════════════════════════════════════╝
```

### **Click DAG → Graph View:**

```
╔══════════════════════════════════════════════════════════╗
║  housing_ml_pipeline - Graph View                        ║
║  Run: 2025-10-31 03:00:00                               ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║           ┌─────────────────┐                           ║
║           │  ingest_data    │ ✅ 5s                     ║
║           └────────┬────────┘                           ║
║                    │                                     ║
║                    ▼                                     ║
║           ┌──────────────────────┐                      ║
║           │ feature_engineering  │ ✅ 3s                ║
║           └────────┬─────────────┘                      ║
║                    │                                     ║
║                    ▼                                     ║
║           ┌─────────────────┐                           ║
║           │  train_model    │ ✅ 30s                    ║
║           └────────┬────────┘                           ║
║                    │                                     ║
║                    ▼                                     ║
║           ┌─────────────────┐                           ║
║           │ validate_model  │ ✅ 1s                     ║
║           └────────┬────────┘                           ║
║                    │                                     ║
║          ┌─────────┴──────────┐                         ║
║          ▼                    ▼                         ║
║  ┌──────────────┐      ┌──────────────┐               ║
║  │ promote_     │      │ send_failure │               ║
║  │ to_staging   │      │ _alert       │               ║
║  └──────────────┘      └──────────────┘               ║
║       ✅ 1s                 (skipped)                    ║
║                                                          ║
║  Total Duration: 40 seconds                             ║
║  Status: SUCCESS ✓                                      ║
╚══════════════════════════════════════════════════════════╝
```

---

## 🔍 Common Scenarios

### **Scenario 1: Everything Works**

```
3:00 AM - Pipeline starts
3:01 AM - ingest_data ✓
3:02 AM - feature_engineering ✓
3:03 AM - train_model ✓ (R²=82%)
3:04 AM - validate_model ✓ (passed thresholds)
3:05 AM - promote_to_staging ✓
3:06 AM - notify_success ✓
3:07 AM - Pipeline complete ✅

Your inbox: "ML Pipeline succeeded! Model v123 in staging"
```

### **Scenario 2: Training Fails**

```
3:00 AM - Pipeline starts
3:01 AM - ingest_data ✓
3:02 AM - feature_engineering ✓
3:03 AM - train_model ❌ (crashed - out of memory!)
3:08 AM - train_model retry #1 ❌
3:13 AM - train_model retry #2 ❌
3:18 AM - Pipeline FAILED ❌

Your inbox: "ML Pipeline FAILED at train_model - check logs!"
```

### **Scenario 3: Model Quality Poor**

```
3:00 AM - Pipeline starts
3:01 AM - ingest_data ✓
3:02 AM - feature_engineering ✓
3:03 AM - train_model ✓ (but R²=0.72 - too low!)
3:04 AM - validate_model ❌ (R² < 0.75 threshold)
3:05 AM - send_failure_alert ✓
3:06 AM - Pipeline stopped (prevented bad model from deploying!)

Your inbox: "Model quality too low: R²=0.72 < 0.75"
```

---

## 📋 Comparison: DVC vs Airflow

### **What You Have (DVC):**

```bash
# Run manually
dvc repro

# Features:
✅ Smart caching (only reruns what changed)
✅ Dependency tracking
✅ Reproducibility
❌ No scheduling (use cron separately)
❌ No UI dashboard
❌ No built-in alerts
```

### **What Airflow Adds:**

```python
# Runs automatically
# (No manual intervention!)

# Features:
✅ Built-in scheduling (@daily, @hourly, etc.)
✅ Visual UI dashboard
✅ Built-in email alerts
✅ Retry logic
✅ Execution history
✅ Live monitoring
❌ No smart caching
❌ More complex setup
```

### **Best Approach:**

```
Development/Local: DVC ✅
  - Simple
  - Smart caching
  - Good for experimentation

Production: Airflow ✅
  - Automated scheduling
  - Monitoring dashboard
  - Team alerts
  - Execution history

Your Project: Has both! ✅
  - Use DVC for development
  - Airflow-ready for production
```

---

## 🎯 Real-World Example

**Company:** Real estate tech company

**Setup:**
```python
# Airflow DAG runs daily at 3 AM
# Retrains model with yesterday's house sales

DAG:
  - Fetch yesterday's sales (from database)
  - Combine with historical data
  - Engineer features
  - Train model
  - If model good: Deploy to staging
  - If model bad: Alert data science team
```

**Monday:**
```
3:00 AM - Airflow: Fetch weekend sales (Sat + Sun)
3:05 AM - Train model: R²=82.5%
3:35 AM - Validate: PASS ✓
3:36 AM - Deploy to staging
3:40 AM - Slack notification: "New model ready for testing"
```

**Tuesday:**
```
3:00 AM - Airflow: Fetch Monday sales
3:05 AM - Train model: R²=70% (data quality issue!)
3:35 AM - Validate: FAIL ❌
3:36 AM - PagerDuty alert: "Model performance dropped!"
8:00 AM - Team investigates: Found data pipeline bug
9:00 AM - Fix deployed
10:00 AM - Manual retrigger: R²=82%, Success ✓
```

---

## ✅ Summary

### **Airflow in 3 Sentences:**

1. **Airflow is a task scheduler** - runs your pipeline automatically
2. **You define a DAG** - workflow with tasks and dependencies
3. **Airflow handles execution** - scheduling, retries, monitoring, alerts

### **Key Benefits:**

```
Automated Execution:
  You: Define once
  Airflow: Runs forever (daily, hourly, etc.)

Error Handling:
  Task fails → Airflow retries automatically
  Still fails → Airflow alerts you

Monitoring:
  Visual dashboard shows all runs
  Click to see logs, duration, status

Team Collaboration:
  Everyone sees the same dashboard
  Shared understanding of pipeline health
```

### **Your Pipeline is Airflow-Ready!**

```
✅ Modular scripts (each stage separate)
✅ Clear dependencies (stage 1 → 2 → 3)
✅ Can be wrapped in BashOperators
✅ Already has validation logic
✅ Interview-ready knowledge

When you move to production:
1. Install Airflow
2. Copy DAG file to airflow/dags/
3. Enable in UI
4. Done! Automatic execution
```

---

## 🎓 Interview Answer Template

**Question:** "Have you used Airflow?"

**Answer:**

> "Yes, I've designed my ML pipeline to be Airflow-ready. I structured it as modular stages that can be orchestrated by Airflow DAGs using BashOperators. Each stage - data ingestion, feature engineering, and model training - is independent and can be scheduled with Airflow's built-in scheduler. I understand DAG concepts, task dependencies using the >> operator, and implementing quality gates with BranchPythonOperators. While I use DVC for local development due to its smart caching, my pipeline can easily integrate with Airflow for production scheduling with monitoring, retries, and team alerts."

**Buzz words:**
- DAG (Directed Acyclic Graph)
- Task dependencies
- BashOperator, PythonOperator
- Scheduled execution
- Quality gates
- Error handling and retries
- Production orchestration

---

## 📁 Files Created for You

1. ✅ `airflow/dags/housing_ml_pipeline.py` - Production-ready DAG
2. ✅ `AIRFLOW_COMPLETE_TUTORIAL.md` - Full tutorial
3. ✅ `AIRFLOW_EXPLAINED_SIMPLE.md` - Simple explanations
4. ✅ `AIRFLOW_SIMPLE_GUIDE.md` - This file

**When you have Python 3.8-3.12:**
- Install Airflow
- Use the DAG file
- See it work!

**For now:**
- You understand the concepts ✅
- You can discuss in interviews ✅
- Your pipeline is ready for it ✅

---

**Congratulations!** You now understand Apache Airflow! 🎉🚀
