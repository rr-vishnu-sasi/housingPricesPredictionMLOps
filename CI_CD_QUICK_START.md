# 🚀 CI/CD Quick Start Guide

## ✅ What Was Created

### **GitHub Actions Workflows:**

```
.github/workflows/
├── ml-pipeline-ci.yml      # CI/CD on push/PR
└── scheduled-retrain.yml   # Daily automated retraining
```

### **What They Do:**

**Pipeline 1 (ml-pipeline-ci.yml):**
```
Code Push → Data Validation → Model Training → Quality Gates → Push to Registry
```

**Pipeline 2 (scheduled-retrain.yml):**
```
Midnight UTC → Full Pipeline → Validate → Deploy → Notify
```

---

## 🎬 How It Works (Simple!)

### **Developer Workflow:**

```
1. You change code:
   └─ Edit config/config.yaml (e.g., n_estimators: 300)

2. You commit & push:
   └─ git add config/config.yaml
   └─ git commit -m "Tune model parameters"
   └─ git push origin main

3. GitHub Actions triggers automatically:
   ├─ 🔍 Validates data
   ├─ 🤖 Trains model with new config
   ├─ ✅ Checks quality (R² ≥ 0.75, RMSE ≤ $50k)
   └─ 📤 Pushes to MLflow registry (if passed)

4. You get notified:
   └─ GitHub commit comment with results

5. Model is deployed!
   └─ Available in MLflow registry
```

---

## 🚀 Setup (3 Steps)

### **Step 1: Push to GitHub**

```bash
# If not already on GitHub:
git init
git add .
git commit -m "Add CI/CD pipelines"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### **Step 2: Verify Workflows Are Active**

1. Go to your GitHub repo
2. Click **"Actions"** tab
3. You'll see 2 workflows:
   - ✅ ML Pipeline CI/CD
   - ✅ Scheduled Model Retraining

### **Step 3: Test It!**

**Option A: Manual Trigger**
1. Go to Actions tab
2. Select "ML Pipeline CI/CD"
3. Click "Run workflow"
4. Watch it execute!

**Option B: Create a PR**
1. Create a new branch:
   ```bash
   git checkout -b test-ci-cd
   ```

2. Make a change:
   ```bash
   echo "# Test CI/CD" >> README.md
   git add README.md
   git commit -m "Test CI/CD"
   git push origin test-ci-cd
   ```

3. Create PR on GitHub
4. Watch automated validation run!
5. See PR comments with results!

---

## 📊 What You Get

### **On Every Pull Request:**

Automated comment on PR:
```
## 🔍 Data Validation Results
Status: ✅ Passed
Dataset: 20,640 rows, 9 features

## 🤖 Model Training Results
Status: ✅ Passed Quality Gates
R² Score: 0.8192 (81.92%)
RMSE: $48,475
✅ All quality gates passed
```

### **On Every Push to Main:**

1. ✅ Model trained automatically
2. ✅ Pushed to MLflow registry
3. ✅ GitHub release created: `model-v1.0_20251105`
4. ✅ Commit comment with deployment info

### **Every Day at Midnight:**

1. ⏰ Workflow triggers automatically
2. 🤖 Trains fresh model with latest data
3. ✅ Validates quality gates
4. 📤 Deploys if passed
5. 📋 Creates GitHub issue:
   - ✅ Success notification
   - ❌ Failure alert (if problems)

---

## 🎯 Comparison: CI/CD vs Airflow vs DVC

### **What You Have Now:**

| Tool | When It Runs | What It Does |
|------|-------------|--------------|
| **GitHub Actions** | On git push/PR + daily | CI/CD + automated testing |
| **Airflow** | Daily at midnight | Production orchestration |
| **DVC** | Manual (you run it) | Development + caching |

### **They Work Together!**

```
Development (Local):
├── You: Edit code/config
├── DVC: dvc repro (with caching!)
└── MLflow: Track experiments

Pull Request:
├── Push code to branch
├── Create PR on GitHub
├── GitHub Actions: Validate automatically
├── See results in PR comments
└── Merge if approved

Production (Main Branch):
├── Merge to main
├── GitHub Actions: Deploy automatically
└── OR
└── Airflow: Scheduled runs

All track to MLflow! 📊
```

---

## 🔥 Real-World Example

### **Scenario: You want to improve your model**

**Step 1: Make changes locally**
```bash
# Edit config
vim config/config.yaml
# Change: n_estimators: 275 → 300

# Test locally with DVC (fast with caching!)
dvc repro

# Check MLflow
# R² improved from 0.82 to 0.83!
```

**Step 2: Create PR**
```bash
git checkout -b improve-model
git add config/config.yaml
git commit -m "Increase n_estimators to 300"
git push origin improve-model

# Create PR on GitHub
```

**Step 3: Automated validation**
```
GitHub Actions runs automatically:
├── 🔍 Data validation: ✅ Passed
├── 🤖 Model training: ✅ Passed
│   └── R²: 0.8301 (83.01%)
│   └── RMSE: $47,123
├── ✅ Quality gates: ✅ Passed
└── 💬 Comments results on PR
```

**Step 4: Review and merge**
```
You see PR comment:
"✅ Model improved! R² +1.09%, RMSE -$1,352"

Team reviews: "Looks good!"
Click "Merge pull request"
```

**Step 5: Automatic deployment**
```
Merge triggers GitHub Actions:
├── ✅ Runs full pipeline
├── ✅ Passes quality gates
├── 📤 Pushes to MLflow registry
├── 🏷️ Creates release: model-v1.1_20251105
└── 💬 Comments: "Model deployed!"

Model is now in production! 🎉
```

**Step 6: Daily retraining continues**
```
Next day (and every day):
└── Scheduled workflow runs at midnight
    └── Trains with config.yaml (n_estimators: 300)
    └── Keeps models fresh!
```

---

## 📋 Quick Commands

### **Check Workflow Status**
```bash
# View on GitHub
# Go to: https://github.com/YOUR_USERNAME/YOUR_REPO/actions
```

### **Test Locally Before Pushing**
```bash
# Run what GitHub Actions will run:
python pipeline/stage_01_ingest_data.py
python pipeline/stage_02_feature_engineering.py
python pipeline/stage_03_train_model_mlflow.py

# Check if would pass quality gates:
R2=$(jq -r '.metrics.r2_score' logs/evaluation_report.json)
echo "R²: $R2 (needs ≥ 0.75)"
```

### **Manual Trigger from CLI**
```bash
# Using GitHub CLI (install: brew install gh)
gh workflow run "ML Pipeline CI/CD"
gh workflow run "Scheduled Model Retraining"
```

---

## 🎯 Quality Gates

Your pipeline enforces these automatically:

| Metric | Threshold | Action if Failed |
|--------|-----------|------------------|
| R² Score | ≥ 0.75 | ❌ Fail pipeline, don't deploy |
| RMSE | ≤ $50,000 | ❌ Fail pipeline, don't deploy |
| Data validation | Must pass | ❌ Stop early, don't train |

**Edit thresholds in:** `.github/workflows/ml-pipeline-ci.yml`

```yaml
# Line ~XX
R2_THRESHOLD=0.75
RMSE_THRESHOLD=50000
```

---

## 🚨 Troubleshooting

### **Workflow Not Running?**

**Check:**
1. Workflows directory: `.github/workflows/` (note the `.`)
2. File syntax: Valid YAML
3. Branch name: Matches workflow trigger

**Debug:**
```bash
# Validate YAML syntax
yamllint .github/workflows/ml-pipeline-ci.yml

# Check Git branch
git branch
```

### **Quality Gates Failing?**

**Check metrics:**
```bash
cat logs/evaluation_report.json | jq '.metrics'
```

**Options:**
1. Improve model (tune hyperparameters)
2. Lower thresholds (if too strict)

### **Artifacts Not Uploading?**

**Verify paths exist:**
```bash
ls -la logs/evaluation_report.json
ls -la models/saved_models/
```

---

## 📊 Monitoring

### **Where to See Results:**

1. **GitHub Actions tab**
   - Workflow runs
   - Detailed logs
   - Artifacts

2. **Pull Requests**
   - Automated comments
   - Check status

3. **GitHub Issues** (for scheduled runs)
   - Success notifications
   - Failure alerts

4. **MLflow UI** (locally)
   - http://localhost:5000
   - Experiment tracking
   - Model registry

---

## 🎓 What You Learned

✅ **CI/CD Automation**: Every push triggers validation
✅ **Quality Gates**: Bad models blocked automatically
✅ **Scheduled Retraining**: Daily automatic updates
✅ **Pull Request Validation**: Test before merge
✅ **MLflow Integration**: All experiments tracked
✅ **GitHub Releases**: Model versions tagged

---

## 🎉 You Now Have

A **production-ready ML CI/CD pipeline** that:

1. ✅ Validates data on every change
2. ✅ Trains models automatically
3. ✅ Enforces quality gates
4. ✅ Deploys to registry
5. ✅ Creates versioned releases
6. ✅ Runs daily retraining
7. ✅ Notifies team of results

**All automated! All tracked! All production-ready!** 🚀

---

## 📚 Learn More

- **Full Guide**: Read `GITHUB_ACTIONS_GUIDE.md`
- **Workflow Files**: See `.github/workflows/`
- **GitHub Actions Docs**: https://docs.github.com/actions

---

## 🚀 Next Steps

1. **Push to GitHub** (if not done)
2. **Create a test PR** to see validation
3. **Watch Actions tab** for workflow runs
4. **Check MLflow** for tracked experiments
5. **Merge PR** and see automatic deployment!

**Your ML pipeline is now enterprise-grade!** 🎊
