# Automation Quick Start Guide

## 🚀 Run Your Automated Pipeline in 30 Seconds

### **Option 1: Run Everything Automatically** (Recommended)
```bash
python run_automated_pipeline.py
```

That's it! This runs all 3 stages:
1. Data Ingestion (fetches 20,640 houses)
2. Feature Engineering (creates 15 features)
3. Model Training (trains & registers model)

---

### **Option 2: Run Individual Stages** (For Testing)
```bash
# Just data ingestion
python pipeline/stage_01_ingest_data.py

# Just feature engineering
python pipeline/stage_02_feature_engineering.py

# Just model training
python pipeline/stage_03_train_model.py
```

---

## 📊 What Gets Created

After running, you'll have:

```
data/
  ├── raw/housing_data.csv              ← Raw data (20,640 houses)
  ├── processed/housing_processed.csv   ← Cleaned data
  └── features/housing_features.csv     ← Featured data (ready for ML)

models/saved_models/
  ├── model_random_forest_*.joblib      ← Trained model
  ├── scaler.joblib                     ← Scaling artifact
  ├── encoder.joblib                    ← Encoding artifact
  └── feature_names.joblib              ← Feature names

logs/
  ├── automated_pipeline_*.log          ← Full pipeline log
  ├── stage_01_ingest_*.log            ← Stage 1 log
  ├── stage_02_features_*.log          ← Stage 2 log
  ├── stage_03_train_*.log             ← Stage 3 log
  └── evaluation_report.json           ← Model metrics
```

---

## 🔍 Check the Results

### View Pipeline Log:
```bash
# Find the latest log
ls -lt logs/automated_pipeline_*.log | head -1

# View it
cat logs/automated_pipeline_*.log
```

### Check Model Performance:
```bash
cat logs/evaluation_report.json | python -m json.tool
```

### Compare Models:
```bash
python examples/model_comparison_example.py
```

---

## 🎯 Common Commands

### Clean and Start Fresh:
```bash
# Remove all generated data/models
rm -rf data/raw/*.csv data/processed/*.csv data/features/*.csv
rm -rf models/saved_models/*.joblib
rm -rf logs/*.log logs/*.json

# Run pipeline from scratch
python run_automated_pipeline.py
```

### Run with DVC (Smart Caching):
```bash
# First time: install DVC
pip install dvc

# Initialize DVC
dvc init

# Run pipeline (with caching)
dvc repro

# Only rerun what changed
dvc repro  # Second time is much faster!
```

### Schedule Daily Runs:
```bash
# Edit crontab
crontab -e

# Add this line (runs every day at 3 AM)
0 3 * * * cd /path/to/project && python run_automated_pipeline.py
```

---

## ⚡ Quick Tips

### 1. Experiment with Different Models:
```bash
# Edit config/config.yaml
# Change: model.type: "random_forest"
# To:     model.type: "gradient_boosting"

# Rerun
python run_automated_pipeline.py

# Compare
python examples/model_comparison_example.py
```

### 2. Change Hyperparameters:
```bash
# Edit config/config.yaml
# Change: n_estimators: 100
# To:     n_estimators: 200

python run_automated_pipeline.py
```

### 3. Check Logs for Errors:
```bash
# View errors only
grep "ERROR" logs/automated_pipeline_*.log

# View metrics
grep "METRIC" logs/stage_03_train_*.log
```

---

## 🎓 What Each Stage Does

### Stage 1: Data Ingestion
```
Input:  None (fetches from scikit-learn)
Does:   - Fetch 20,640 houses
        - Check for missing values
        - Remove duplicates
        - Detect outliers
Output: data/raw/housing_data.csv
        data/processed/housing_processed.csv
Time:   ~5 seconds
```

### Stage 2: Feature Engineering
```
Input:  data/processed/housing_processed.csv
Does:   - Create derived features (rooms_per_household, etc.)
        - Encode categories (ocean_proximity)
        - Scale numbers (StandardScaler)
        - Save artifacts for inference
Output: data/features/housing_features.csv
        models/saved_models/scaler.joblib
        models/saved_models/encoder.joblib
Time:   ~3 seconds
```

### Stage 3: Model Training
```
Input:  data/features/housing_features.csv
Does:   - Split train/validation (80/20)
        - Train model (Random Forest, 100 trees)
        - Evaluate (RMSE, R², MAE, MAPE)
        - Register model if passes thresholds
Output: models/saved_models/model_*.joblib
        logs/evaluation_report.json
        models/model_registry/registry.json
Time:   ~30 seconds
```

---

## 🐛 Troubleshooting

### Pipeline Failed?
```bash
# Check which stage failed
grep "FAILED" logs/automated_pipeline_*.log

# View detailed error
cat logs/stage_0X_*.log | grep -A 5 "ERROR"
```

### Want More Debug Info?
```bash
# View detailed stage log
cat logs/stage_01_ingest_*.log    # Stage 1
cat logs/stage_02_features_*.log  # Stage 2
cat logs/stage_03_train_*.log     # Stage 3
```

### Model Performance Low?
```bash
# Check metrics
cat logs/evaluation_report.json

# If R² < 0.75 or RMSE > $50,000:
# 1. Try different model type in config/config.yaml
# 2. Adjust hyperparameters
# 3. Add more features in src/features/engineer.py
```

---

## 📚 Learn More

- **Full Guide:** Read `AUTOMATION_GUIDE.md` for detailed explanations
- **MLOps Concepts:** Read `MLOPS_CONCEPTS.md` for theory
- **Project Overview:** Read `README.md` for complete project info

---

## ✅ Success Checklist

After running the pipeline, you should see:

- [ ] Pipeline completed successfully (no errors)
- [ ] Log files created in `logs/`
- [ ] Model registered in `models/model_registry/registry.json`
- [ ] Model R² > 0.75 (75% accurate)
- [ ] Model RMSE < $50,000

**All checked?** Congratulations! Your automated pipeline is working! 🎉

---

## 🎯 Next Steps

1. **Try it:** `python run_automated_pipeline.py`
2. **Check logs:** `cat logs/automated_pipeline_*.log`
3. **View metrics:** `cat logs/evaluation_report.json`
4. **Experiment:** Change settings in `config/config.yaml`
5. **Compare:** `python examples/model_comparison_example.py`

**Ready to deploy?** Your pipeline is production-ready!
