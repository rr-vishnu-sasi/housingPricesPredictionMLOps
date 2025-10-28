# Data-Triggered Pipelines - Complete Guide

## 🎯 Question: Can we trigger the pipeline when data changes?

## ✅ Answer: YES! Three Ways to Do It

---

## Why This Matters (MLOps Concept)

**Problem:** Running pipeline every hour wastes resources if data hasn't changed

**Solution:** Event-driven pipelines (only run when data actually changes)

```
❌ Bad: Run every hour (720 runs/month, even if data unchanged)
✅ Good: Run only when data changes (maybe 30 runs/month)

Savings: 96% fewer runs = 96% cost reduction!
```

---

## 🔧 Solution 1: File Watcher (Real-Time)

**When to use:**
- Development/testing
- Real-time data updates
- Need immediate response to changes

**How it works:**
1. Continuously watches data files
2. Detects changes instantly (file hash comparison)
3. Triggers pipeline automatically

### **Setup:**

```bash
# Run the watcher (stays running)
python watch_data_changes.py
```

### **What happens:**

```
👀 Watching for changes...

[11:00:00] No changes detected (check #1)
[11:00:30] No changes detected (check #2)
[11:01:00] No changes detected (check #3)
[11:01:30] 🔔 CHANGE DETECTED: data/raw/housing_data.csv
           Old hash: 5d41402a...
           New hash: 7c6a180b...
[11:01:31] 🚀 TRIGGERING PIPELINE

>>> Stage 1/3: Data Ingestion
    ✓ Completed
>>> Stage 2/3: Feature Engineering
    ✓ Completed
>>> Stage 3/3: Model Training
    ✓ Completed

[11:03:45] ✓ Pipeline completed successfully
[11:04:00] No changes detected (check #4)
...
```

### **How it detects changes:**

```python
# Simple concept: File Hash (Fingerprint)

# Original file
hash("Hello") = "8b1a9953c4611296a827abf8c47804d7"

# Change 1 character
hash("Hallo") = "4e56c2d4a86c9b72e1f19d55f5c1c8c8"  # Completely different!

# So we can detect ANY change:
if current_hash != old_hash:
    trigger_pipeline()  # Data changed!
else:
    skip()  # Data same, save resources
```

### **Test it:**

```bash
# Terminal 1: Start watcher
python watch_data_changes.py

# Terminal 2: Modify data
echo "test" >> data/raw/housing_data.csv

# Terminal 1: See it trigger!
# 🔔 CHANGE DETECTED!
# 🚀 TRIGGERING PIPELINE
```

### **Pros & Cons:**

✅ **Pros:**
- Instant detection (real-time)
- Simple to understand
- No external dependencies

❌ **Cons:**
- Process must stay running
- Not ideal for production (what if it crashes?)
- Uses resources even when idle

---

## 🔧 Solution 2: DVC-Based (Smart & Efficient)

**When to use:**
- Production environments
- Git-tracked projects
- Want smart caching (only rerun changed stages)

**How it works:**
1. DVC tracks file checksums
2. Knows dependencies between stages
3. Only reruns stages whose inputs changed

### **Setup:**

```bash
# One-time setup
pip install dvc
dvc init

# Then use DVC commands instead of manual scripts
dvc repro
```

### **What happens (DVC Magic):**

```bash
# First run
$ dvc repro

Stage 'ingest_data' is running...
Stage 'feature_engineering' is running...
Stage 'train_model' is running...
Pipeline completed in 40 seconds

# Second run (nothing changed)
$ dvc repro

Stage 'ingest_data' didn't change, skipping  ⚡
Stage 'feature_engineering' didn't change, skipping  ⚡
Stage 'train_model' didn't change, skipping  ⚡
Pipeline completed in 1 second!  🎉

# Third run (only data changed)
$ dvc repro

Stage 'ingest_data' is running...  ← Reruns
Stage 'feature_engineering' is running...  ← Reruns (depends on data)
Stage 'train_model' is running...  ← Reruns (depends on features)
Pipeline completed in 40 seconds

# Fourth run (only config changed)
$ dvc repro

Stage 'ingest_data' didn't change, skipping  ⚡
Stage 'feature_engineering' didn't change, skipping  ⚡
Stage 'train_model' is running...  ← Only this reruns!
Pipeline completed in 30 seconds
```

### **Smart Dependency Tracking:**

```yaml
# dvc.yaml (already in your project!)

stages:
  ingest_data:
    cmd: python pipeline/stage_01_ingest_data.py
    deps:
      - config/config.yaml  ← If this changes, rerun
    outs:
      - data/raw/housing_data.csv  ← Output

  feature_engineering:
    deps:
      - data/raw/housing_data.csv  ← If THIS changes, rerun
    outs:
      - data/features/housing_features.csv

  train_model:
    deps:
      - data/features/housing_features.csv  ← If THIS changes, rerun
      - config/config.yaml  ← Or this
```

### **Scheduled with DVC:**

```bash
#!/bin/bash
# cron_with_dvc.sh

cd /path/to/project

# DVC only reruns what changed
dvc repro

# Log result
if [ $? -eq 0 ]; then
    echo "$(date): Pipeline success" >> logs/cron.log
else
    echo "$(date): Pipeline failed" >> logs/cron.log
fi
```

**Add to crontab:**
```bash
# Check every hour (but only runs if data changed)
0 * * * * /path/to/project/cron_with_dvc.sh
```

### **Pros & Cons:**

✅ **Pros:**
- Extremely efficient (smart caching)
- Production-ready
- Integrates with Git
- Only reruns necessary stages
- No continuous process needed

❌ **Cons:**
- Need to learn DVC
- Additional tool/dependency

---

## 🔧 Solution 3: Scheduled Check (Production-Ready)

**When to use:**
- Production without DVC
- Scheduled retraining (hourly, daily)
- Integration with cron/Airflow/etc.

**How it works:**
1. Runs on schedule (e.g., every hour via cron)
2. Checks if data hash changed since last run
3. Only runs pipeline if actually changed
4. Saves state to avoid reruns

### **Setup:**

```bash
# Run manually (checks and runs if needed)
python check_and_run.py

# Or schedule with cron
0 * * * * cd /path/to/project && python check_and_run.py
```

### **What happens:**

```
Hour 1:
==============================================
SCHEDULED DATA CHECK
==============================================
Check time: 2025-10-28 01:00:00
Last pipeline run: Never
Current data hash: 5d41402abc4b2a76...
🔔 DATA CHANGED - triggering pipeline!
>>> Running pipeline...
✓ Pipeline completed successfully

Hour 2:
==============================================
SCHEDULED DATA CHECK
==============================================
Check time: 2025-10-28 02:00:00
Last pipeline run: 2025-10-28 01:00:00
Current data hash: 5d41402abc4b2a76...
✓ Data unchanged - skipping pipeline (saves time!)
   Last hash: 5d41402a...
   Current:   5d41402a...  (same!)

Hour 3:
(same - skipped)

Hour 4:
==============================================
SCHEDULED DATA CHECK
==============================================
Check time: 2025-10-28 04:00:00
Last pipeline run: 2025-10-28 01:00:00
Current data hash: 7c6a180b52d68223...
🔔 DATA CHANGED - triggering pipeline!
>>> Running pipeline...
✓ Pipeline completed successfully
```

### **State Management:**

```json
// logs/pipeline_state.json (automatically managed)
{
    "data_hash": "5d41402abc4b2a76b9719d911017c592",
    "last_run": "2025-10-28T01:00:00",
    "last_check": "2025-10-28T04:00:00",
    "status": "success"
}
```

### **Cron Setup:**

```bash
# Edit crontab
crontab -e

# Add these lines:

# Check every hour
0 * * * * cd /path/to/project && python check_and_run.py >> logs/cron.log 2>&1

# Or check every 30 minutes
*/30 * * * * cd /path/to/project && python check_and_run.py >> logs/cron.log 2>&1

# Or check daily at 3 AM
0 3 * * * cd /path/to/project && python check_and_run.py >> logs/cron.log 2>&1
```

### **Pros & Cons:**

✅ **Pros:**
- Production-ready
- No continuous process needed
- Simple state management
- Works with any scheduler (cron, Airflow, etc.)
- Resource efficient

❌ **Cons:**
- Not real-time (runs on schedule)
- Can't detect changes between scheduled runs

---

## 📊 Comparison Table

| Feature | File Watcher | DVC | Scheduled Check |
|---------|-------------|-----|-----------------|
| **Real-time detection** | ✅ Yes | ❌ No | ❌ No |
| **Smart caching** | ❌ No | ✅ Yes | ❌ No |
| **Production-ready** | ⚠️ Partial | ✅ Yes | ✅ Yes |
| **Needs to stay running** | ✅ Yes | ❌ No | ❌ No |
| **Extra dependencies** | ❌ No | ✅ DVC | ❌ No |
| **Resource usage (idle)** | Medium | Low | Lowest |
| **Setup complexity** | Easy | Medium | Easy |
| **Best for** | Development | Production (Git) | Production (simple) |

---

## 🎯 Which Solution Should You Use?

### **Development/Testing:**
```bash
# Use File Watcher (real-time feedback)
python watch_data_changes.py
```

### **Production with Git:**
```bash
# Use DVC (smart caching)
pip install dvc
dvc init
dvc repro

# Schedule it
0 * * * * cd /project && dvc repro
```

### **Production without DVC:**
```bash
# Use Scheduled Check (simple & reliable)
python check_and_run.py

# Schedule it
0 * * * * cd /project && python check_and_run.py
```

---

## 🔥 Real-World Example

**Scenario:** You work at a real estate company. New housing data arrives daily at 3 AM.

### **Setup:**

```bash
# Method 1: Simple scheduled check
# Add to crontab
0 3 * * * cd /path/to/project && python check_and_run.py

# What happens:
# 3:00 AM Day 1: Data changed → Pipeline runs (trains new model)
# 3:00 AM Day 2: Data changed → Pipeline runs
# 3:00 AM Day 3: No new data → Pipeline skipped (saves 2 min + compute)
# 3:00 AM Day 4: Data changed → Pipeline runs

# Result: Only 3 pipeline runs instead of 4!
```

### **With notifications:**

```bash
#!/bin/bash
# scheduled_with_alert.sh

cd /path/to/project
python check_and_run.py

if [ $? -eq 0 ]; then
    # Success
    curl -X POST https://slack.com/api/your-webhook \
      -d "text=✓ ML Pipeline completed at $(date)"
else
    # Failure
    curl -X POST https://slack.com/api/your-webhook \
      -d "text=✗ ML Pipeline FAILED at $(date)"
fi
```

---

## 🧪 Try It Now!

### **Test File Watcher:**

```bash
# Terminal 1: Start watcher
python watch_data_changes.py

# Terminal 2: Simulate data change
# Edit data file
echo "# Test change" >> data/raw/housing_data.csv

# Terminal 1: Watch it trigger!
```

### **Test Scheduled Check:**

```bash
# First run (should run pipeline)
python check_and_run.py

# Second run immediately (should skip)
python check_and_run.py
# Output: "✓ Data unchanged - skipping pipeline"

# Modify data
echo "test" >> data/raw/housing_data.csv

# Third run (should run again)
python check_and_run.py
# Output: "🔔 DATA CHANGED - triggering pipeline!"
```

### **Test DVC:**

```bash
# Install DVC
pip install dvc

# Initialize
dvc init

# First run
dvc repro  # Runs all stages

# Second run
dvc repro  # Skips everything (no changes)

# Change config
# Edit config/config.yaml (change n_estimators)

# Third run
dvc repro  # Only reruns training!
```

---

## 💡 MLOps Interview Answer

**Question:** "How would you trigger your pipeline when data changes?"

**Your Answer:**

> "I implemented three approaches for data-triggered pipelines. For development, I use a file watcher that continuously monitors data files using hash comparisons and triggers the pipeline in real-time when changes are detected. For production, I prefer DVC which provides smart caching - it only reruns stages whose dependencies actually changed, significantly reducing computational costs. For simpler production environments, I use a scheduled checker that runs on cron but maintains state to skip reruns when data hasn't changed. All three approaches prevent unnecessary pipeline executions, which is critical for cost optimization in production MLOps."

**Key terms:**
- Event-driven pipelines
- File hash comparison for change detection
- Smart caching (DVC)
- State management
- Resource optimization
- Scheduled orchestration

---

## ✅ Summary

### **What You Built:**
- ✅ Real-time file watcher
- ✅ DVC smart caching integration
- ✅ Scheduled checker with state management
- ✅ All 3 solutions working and documented

### **MLOps Skills Demonstrated:**
- Event-driven architecture
- Change detection mechanisms
- Resource optimization
- Production-ready patterns
- Scheduled orchestration

### **Cost Savings Example:**
```
Without smart detection:
- Run every hour: 720 runs/month
- Cost: 720 × $1 = $720/month

With smart detection:
- Only run when data changes: ~30 runs/month
- Cost: 30 × $1 = $30/month

Savings: $690/month (96% reduction!) 🎉
```

---

**You now have production-ready data-triggered pipelines!** 🚀
