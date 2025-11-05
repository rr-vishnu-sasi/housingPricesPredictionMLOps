# 🚀 GitHub Actions CI/CD Guide

## 📋 Table of Contents
1. [What We Created](#what-we-created)
2. [How It Works](#how-it-works)
3. [Setup Instructions](#setup-instructions)
4. [Workflows Explained](#workflows-explained)
5. [Testing Locally](#testing-locally)
6. [Monitoring & Troubleshooting](#monitoring--troubleshooting)

---

## ✅ What We Created

### **Files Added:**

```
.github/
└── workflows/
    ├── ml-pipeline-ci.yml        # Main CI/CD pipeline
    └── scheduled-retrain.yml     # Daily automated retraining
```

### **What They Do:**

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **ml-pipeline-ci.yml** | Push to main, PR | Full CI/CD: validation → training → registry |
| **scheduled-retrain.yml** | Daily at midnight | Automated retraining (like Airflow) |

---

## 🎬 How It Works

### **Visual Flow:**

```
Developer pushes code
        ↓
GitHub Actions triggers
        ↓
┌─────────────────────────────────────┐
│  JOB 1: Data Validation             │
│  • Fetch data                       │
│  • Run quality checks               │
│  • Upload report                    │
└────────────┬────────────────────────┘
             │ (if success)
             ↓
┌─────────────────────────────────────┐
│  JOB 2: Train Model                 │
│  • Feature engineering              │
│  • Train with MLflow                │
│  • Validate quality gates           │
│  • Upload artifacts                 │
└────────────┬────────────────────────┘
             │ (if success + main branch)
             ↓
┌─────────────────────────────────────┐
│  JOB 3: Push to Registry            │
│  • Push to MLflow registry          │
│  • Create GitHub release            │
│  • Notify team                      │
└─────────────────────────────────────┘
```

---

## 🛠️ Setup Instructions

### **Step 1: Initialize Git Repository (if not done)**

```bash
# Check if Git is initialized
git status

# If not, initialize
git init
git add .
git commit -m "Initial commit with CI/CD pipelines"
```

### **Step 2: Push to GitHub**

```bash
# Create a repo on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### **Step 3: GitHub Actions Activates Automatically!**

Once pushed, GitHub Actions will:
- ✅ Detect `.github/workflows/*.yml` files
- ✅ Enable the workflows
- ✅ Start running on next push/PR

### **Step 4: View Workflows**

On GitHub:
1. Go to your repository
2. Click **"Actions"** tab
3. See workflows running!

---

## 📊 Workflows Explained

### **Workflow 1: ML Pipeline CI/CD**

**File:** `.github/workflows/ml-pipeline-ci.yml`

**Triggers:**
- ✅ Push to `main` branch
- ✅ Pull requests to `main`
- ✅ Manual trigger (workflow_dispatch)

**What It Does:**

#### **On Pull Request:**
```
1. 🔍 Data Validation
   └─ Checks data quality
   └─ Comments results on PR

2. 🤖 Model Training
   └─ Trains model
   └─ Validates quality gates
   └─ Comments metrics on PR

3. ❌ Does NOT push to registry
   └─ Only validates, doesn't deploy

4. 🔒 Code Quality Checks
   └─ Runs in parallel
   └─ Black, Flake8, Bandit
```

**Example PR Comment:**
```
## 🔍 Data Validation Results
Status: ✅ Passed
Total rows: 20,640
Quality checks: ✅ All passed

## 🤖 Model Training Results
Status: ✅ Passed Quality Gates
R² Score: 0.8192 (81.92%)
RMSE: $48,475
✅ R² ≥ 0.75
✅ RMSE ≤ $50,000
```

#### **On Push to Main:**
```
1. 🔍 Data Validation
2. 🤖 Model Training
3. ✅ Quality Gates Check
4. 📤 Push to MLflow Registry
5. 🏷️ Create GitHub Release
6. 💬 Notify via commit comment
```

**Quality Gates:**
- R² Score must be ≥ 0.75
- RMSE must be ≤ $50,000
- Pipeline fails if not met!

---

### **Workflow 2: Scheduled Retraining**

**File:** `.github/workflows/scheduled-retrain.yml`

**Triggers:**
- ⏰ Daily at midnight UTC
- 🔧 Manual trigger

**What It Does:**

```
Every Day at 00:00 UTC:
    ↓
1. Fetch latest code
2. Install dependencies
3. Run complete pipeline:
   • Data ingestion
   • Feature engineering
   • Model training
4. Validate quality gates
5. Push to registry (if passed)
6. Create GitHub issue:
   • ✅ Success notification
   • ❌ Failure alert
```

**GitHub Issue Created:**

On success:
```
Title: ✅ Daily Retraining Successful - 2025-11-05

Body:
## ✅ Scheduled Retraining Complete
Date: 2025-11-05T00:15:32Z
R² Score: 0.8206
RMSE: $48,475
Status: Model trained, validated, and deployed
```

On failure:
```
Title: ❌ Daily Retraining FAILED - 2025-11-05

Body:
## ❌ Scheduled Retraining Failed
Action Required:
1. Check workflow logs
2. Investigate failure
3. Manual rerun needed
```

---

## 🧪 Testing Locally

### **Test Before Pushing to GitHub:**

#### **Option 1: Act (Run GitHub Actions Locally)**

Install `act`:
```bash
# macOS
brew install act

# Or use Docker
```

Run workflows locally:
```bash
# Test the CI pipeline
act push

# Test pull request workflow
act pull_request

# Test scheduled workflow
act schedule
```

#### **Option 2: Manual Testing**

Run the same commands GitHub Actions runs:

```bash
# What GitHub Actions does:
python pipeline/stage_01_ingest_data.py
python pipeline/stage_02_feature_engineering.py
python pipeline/stage_03_train_model_mlflow.py

# Check quality gates
R2=$(jq -r '.metrics.r2_score' logs/evaluation_report.json)
RMSE=$(jq -r '.metrics.rmse' logs/evaluation_report.json)

echo "R²: $R2"
echo "RMSE: $RMSE"

# Validate
if (( $(echo "$R2 >= 0.75" | bc -l) )) && (( $(echo "$RMSE <= 50000" | bc -l) )); then
    echo "✅ Would pass quality gates"
else
    echo "❌ Would fail quality gates"
fi
```

---

## 📊 Monitoring & Troubleshooting

### **View Workflow Runs**

On GitHub:
1. Click **"Actions"** tab
2. Select a workflow
3. Click a specific run
4. See detailed logs for each job/step

### **Common Issues & Solutions**

#### **Issue 1: Workflow Not Triggering**

**Check:**
```yaml
# In .github/workflows/ml-pipeline-ci.yml
on:
  push:
    branches:
      - main  # Make sure this matches your branch name
```

**Solution:**
- Ensure you're pushing to correct branch
- Check workflow file syntax
- Verify `.github/workflows/` directory structure

---

#### **Issue 2: Quality Gates Failing**

**Error:**
```
❌ Model R² (0.72) below threshold (0.75)
```

**Solutions:**
1. **Adjust thresholds** (if model is actually good):
   ```yaml
   # In workflow file, change:
   R2_THRESHOLD=0.70  # Lower threshold
   ```

2. **Improve model** (if model is actually bad):
   - Tune hyperparameters in `config/config.yaml`
   - Add more features
   - Try different algorithms

---

#### **Issue 3: Dependencies Not Installing**

**Error:**
```
ERROR: Could not find a version that satisfies requirement...
```

**Solution:**
```yaml
# In workflow file, ensure correct Python version:
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'  # Match your project
```

---

#### **Issue 4: Artifacts Not Found**

**Error:**
```
No artifacts found
```

**Solution:**
Verify paths in workflow:
```yaml
- uses: actions/upload-artifact@v4
  with:
    path: logs/evaluation_report.json  # Ensure this file exists!
```

---

## 🎯 Workflow Comparison

### **GitHub Actions vs. Airflow vs. DVC**

| Feature | GitHub Actions | Airflow | DVC |
|---------|---------------|---------|-----|
| **Trigger** | Git events, schedule | Schedule only | Manual |
| **Best For** | CI/CD automation | Production scheduling | Dev reproducibility |
| **Monitoring** | GitHub UI | Airflow UI | CLI |
| **Cost** | Free (2000 min/month) | Self-hosted | Free |
| **Setup** | Easy (.yml file) | Complex | Easy |
| **Notifications** | PR comments, issues | Email, Slack | None |
| **Caching** | Built-in | No | Yes (smart!) |

### **When to Use Each:**

```
GitHub Actions:
✅ Code changes trigger retraining
✅ Pull request validation
✅ Automated testing
✅ Cloud-native CI/CD

Airflow:
✅ Production scheduling (daily/weekly)
✅ Complex workflows
✅ On-premise infrastructure
✅ Advanced monitoring

DVC:
✅ Development experimentation
✅ Data versioning
✅ Pipeline caching
✅ Reproducibility

Ideal Setup: Use ALL THREE!
├── GitHub Actions: CI/CD on code changes
├── Airflow: Scheduled production runs
└── DVC: Local dev + reproducibility
```

---

## 🚀 Advanced Features

### **1. Matrix Builds (Test Multiple Configs)**

```yaml
strategy:
  matrix:
    python-version: [3.10, 3.11, 3.12]
    model-type: [random_forest, gradient_boosting]

steps:
  - name: Test with ${{ matrix.model-type }}
    run: |
      # Change config
      yq eval ".model.type = \"${{ matrix.model-type }}\"" -i config/config.yaml
      # Run pipeline
      python pipeline/stage_03_train_model_mlflow.py
```

### **2. Deploy to Cloud**

```yaml
- name: Deploy to AWS
  if: github.ref == 'refs/heads/main'
  run: |
    aws s3 cp models/saved_models/ s3://my-models/ --recursive
    aws lambda update-function-code --function-name ml-predictor
```

### **3. Slack Notifications**

```yaml
- name: Notify Slack
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "Model trained! R²: ${{ steps.train.outputs.r2 }}"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

### **4. Performance Comparison**

```yaml
- name: Compare with baseline
  run: |
    CURRENT_R2=${{ steps.train.outputs.r2 }}
    BASELINE_R2=0.80

    if (( $(echo "$CURRENT_R2 < $BASELINE_R2" | bc -l) )); then
      echo "⚠️ Performance degradation detected!"
    fi
```

---

## ✅ Checklist: Setting Up CI/CD

- [ ] GitHub repository created
- [ ] Workflow files in `.github/workflows/`
- [ ] Code pushed to main branch
- [ ] GitHub Actions tab shows workflows
- [ ] Manual trigger test passed
- [ ] Pull request test passed
- [ ] Quality gates configured
- [ ] Notifications set up
- [ ] Team informed about CI/CD

---

## 📚 Resources

**Official Docs:**
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

**Examples:**
- [ML with GitHub Actions](https://github.blog/2020-06-17-using-github-actions-for-mlops-data-science/)
- [MLOps Template](https://github.com/github/mlops-template)

**Your Workflows:**
- `.github/workflows/ml-pipeline-ci.yml` - Main CI/CD
- `.github/workflows/scheduled-retrain.yml` - Daily retraining

---

## 🎉 Summary

You now have:

✅ **Automated CI/CD** on every code push
✅ **PR validation** with automatic comments
✅ **Quality gates** preventing bad models
✅ **Daily retraining** at midnight
✅ **MLflow integration** for tracking
✅ **GitHub releases** for model versions
✅ **Notifications** via issues/comments

**Your ML pipeline is now production-ready!** 🚀

---

**Next Steps:**
1. Push to GitHub
2. Watch Actions tab
3. Create a test PR
4. See automated validation!
