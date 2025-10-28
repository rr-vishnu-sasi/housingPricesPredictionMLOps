# Quick Start Guide

Get up and running with the Housing Price Prediction MLOps project in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Step-by-Step Setup

### 1. Set Up Environment

```bash
# Navigate to project directory
cd housingPricesPredictionProject

# Activate your virtual environment (if not already activated)
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Training Pipeline

```bash
python main_pipeline.py
```

**What happens:**
- ✅ Fetches California Housing dataset
- ✅ Performs data quality checks
- ✅ Engineers features (derived features, encoding, scaling)
- ✅ Trains a Random Forest model
- ✅ Evaluates on validation set
- ✅ Saves model and registers in model registry

**Expected output:**
```
============================================================
HOUSING PRICE PREDICTION - MLOPS PIPELINE
============================================================
...
✓ Pipeline completed successfully!

Pipeline Summary:
  ✓ Data samples processed: 20,640
  ✓ Features engineered: 12
  ✓ Model trained: random_forest
  ✓ Validation RMSE: $47,234.56
  ✓ Validation R²: 0.8234
  ✓ Model version: v_20241025_120000
  ✓ Model stage: staging
```

### 3. Make Predictions

```bash
python examples/inference_example.py
```

**What happens:**
- ✅ Loads latest trained model from registry
- ✅ Makes single prediction on example house
- ✅ Makes batch predictions on multiple houses
- ✅ Shows prediction statistics and latency

**Expected output:**
```
============================================================
MODEL INFERENCE EXAMPLE
============================================================
Using model version: v_20241025_120000

Input data:
  median_income: 8.3252
  housing_median_age: 41.0
  ...

Predicted house value: $452,600.00

✓ Inference examples completed successfully!
```

### 4. Compare Models (Optional)

```bash
python examples/model_comparison_example.py
```

Shows comparison of all models in the registry with metrics and recommendations.

## What Gets Created

After running the pipeline, you'll have:

```
📁 data/
  ├── raw/housing_data.csv          # Original data
  ├── processed/                    # Cleaned data
  └── features/                     # Engineered features

📁 models/
  ├── saved_models/                 # Model files (.joblib)
  │   ├── model_random_forest_*.joblib
  │   ├── scaler.joblib
  │   └── encoder.joblib
  └── model_registry/
      └── registry.json             # Model metadata

📁 logs/
  ├── pipeline.log                  # Execution logs
  ├── data_quality_report.json      # Data validation results
  └── evaluation_report.json        # Model metrics
```

## Understanding the Configuration

Open `config/config.yaml` to see all configurable parameters:

```yaml
# Change model type
model:
  type: "random_forest"  # Try: linear_regression, gradient_boosting

# Adjust hyperparameters
hyperparameters:
  random_forest:
    n_estimators: 100    # Try: 50, 200, 500
    max_depth: 20        # Try: 10, 30, null (unlimited)
```

## Experiment: Train a Different Model

1. Edit `config/config.yaml`
2. Change `model.type` to `"gradient_boosting"`
3. Run `python main_pipeline.py` again
4. Compare models with `python examples/model_comparison_example.py`

## Troubleshooting

### Import Errors
```bash
# Make sure you're in the project root directory
pwd  # Should show: .../housingPricesPredictionProject

# Verify Python can find the modules
python -c "import src.utils; print('OK')"
```

### Missing Dependencies
```bash
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

### Permission Errors
```bash
# Make sure directories are writable
chmod -R u+w data/ models/ logs/
```

## Next Steps

1. **Explore the code:**
   - Start with `main_pipeline.py` to see the full workflow
   - Look at `src/data/ingest.py` for data processing
   - Check `src/models/train.py` for model training

2. **Read the documentation:**
   - `README.md` for detailed MLOps concepts
   - Code comments explain the "why" behind each component

3. **Experiment:**
   - Try different models and hyperparameters
   - Add new features in `src/features/engineer.py`
   - Modify evaluation metrics in `config/config.yaml`

4. **Extend the project:**
   - Add MLflow for experiment tracking
   - Implement a REST API with FastAPI
   - Add data versioning with DVC
   - Create a Docker container

## Common Commands Reference

```bash
# Training
python main_pipeline.py

# Inference (single/batch)
python examples/inference_example.py

# Model comparison
python examples/model_comparison_example.py

# View logs
cat logs/pipeline.log
cat logs/evaluation_report.json

# List saved models
ls -lh models/saved_models/

# View registry
cat models/model_registry/registry.json | python -m json.tool
```

## Getting Help

- Check the logs: `logs/pipeline.log`
- Review data quality: `logs/data_quality_report.json`
- Check model metrics: `logs/evaluation_report.json`
- Read the detailed README: `README.md`

---

**You're all set! 🚀**

This project demonstrates production-ready MLOps practices. Explore, experiment, and learn!
