# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an end-to-end MLOps project for housing price prediction using the California Housing dataset. The project demonstrates production-ready ML practices including data versioning (DVC), experiment tracking (MLflow), automated pipelines, and model serving.

**Tech Stack:** Python, scikit-learn, MLflow, DVC, Apache Airflow, pandas, numpy

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Running Pipelines

**DVC Pipeline (Recommended - with caching):**
```bash
# Run full pipeline with smart caching
dvc repro

# Force re-run all stages (ignore cache)
dvc repro -f

# Run specific stage only
dvc repro stage_01_ingest_data
dvc repro stage_02_feature_engineering
dvc repro stage_03_train_model
```

**Manual Pipeline:**
```bash
# Run the full pipeline without DVC
python main_pipeline.py

# Run individual stages
python pipeline/stage_01_ingest_data.py
python pipeline/stage_02_feature_engineering.py
python pipeline/stage_03_train_model_mlflow.py
```

### MLflow Operations

**Start MLflow UI:**
```bash
mlflow ui
# Access at http://localhost:5000
```

**Serve Model as API:**
```bash
# Serve the pipeline model (accepts raw data)
python serve_model_api.py

# API endpoint: http://localhost:5001/invocations
# Health check: http://localhost:5001/ping

# View API usage examples
python serve_model_api.py --examples
```

**Test API:**
```bash
# Using provided test scripts
python test_api.py          # Comprehensive API tests
python test_api_client.py   # Client usage examples
```

### Airflow Operations (if configured)

```bash
# Initialize Airflow database (first time only)
airflow db init

# Start Airflow webserver (port 8080)
airflow webserver --port 8080

# Start Airflow scheduler (in separate terminal)
airflow scheduler

# Access UI at http://localhost:8080
```

### Data and Model Inspection

```bash
# Preview dataset
python preview_dataset.py

# Make predictions with trained model
python predict_simple.py

# Train multiple models for comparison
bash train_multiple_models.sh
```

## Architecture Overview

### Pipeline Flow

The ML pipeline follows this sequential workflow:

```
Data Ingestion → Feature Engineering → Model Training → Evaluation → Registry → Serving
```

**Key insight:** Each stage is independent and cached by DVC - if inputs haven't changed, the stage is skipped.

### Project Structure

```
src/
├── data/ingest.py           # Data loading, validation, quality checks
├── features/engineer.py     # Feature creation, encoding, scaling
├── models/
│   ├── train.py            # Model training logic (multi-algorithm)
│   └── registry.py         # Model versioning and lifecycle management
├── evaluation/evaluate.py   # Metrics calculation, threshold validation
├── serving/predict.py       # Inference with preprocessing consistency
├── mlflow_tracker.py        # MLflow experiment tracking wrapper
└── mlflow_pipeline_model.py # Custom MLflow model with preprocessing

pipeline/                    # DVC pipeline stages (individual scripts)
config/config.yaml           # Central configuration (SINGLE SOURCE OF TRUTH)
dvc.yaml                     # DVC pipeline definition
airflow/dags/               # Airflow DAG definitions (if using Airflow)
```

### Configuration Management

**IMPORTANT:** All hyperparameters, paths, and settings are in `config/config.yaml`. Never hardcode values in code.

**To experiment with different models:**
1. Edit `config/config.yaml` - change `model.type` or hyperparameters
2. Run `dvc repro` to train with new settings
3. Compare in MLflow UI

**Available model types:**
- `linear_regression`
- `random_forest` (default)
- `gradient_boosting`

### MLflow Integration

**Two model types are registered:**

1. **`housing_price_predictor`** - Raw scikit-learn model (requires preprocessed data)
2. **`housing_price_predictor_pipeline`** - Full pipeline model that accepts RAW data with preprocessing

**For serving:** Always use the `_pipeline` model as it handles all preprocessing automatically.

**Experiment tracking:** Every training run logs:
- Hyperparameters
- Metrics (RMSE, MAE, R², MAPE)
- Model artifacts
- Feature importance
- Dataset info

### DVC Pipeline Stages

**Stage 1: Data Ingestion** (`pipeline/stage_01_ingest_data.py`)
- Fetches California Housing dataset
- Performs quality checks (missing values, duplicates, outliers)
- Outputs: `data/raw/`, `data/processed/`, quality report

**Stage 2: Feature Engineering** (`pipeline/stage_02_feature_engineering.py`)
- Creates derived features (rooms_per_household, etc.)
- Encodes categorical variables (one-hot encoding)
- Scales numerical features (StandardScaler)
- Outputs: `data/features/`, scaler/encoder artifacts

**Stage 3: Model Training** (`pipeline/stage_03_train_model_mlflow.py`)
- Trains model based on config
- Tracks experiment in MLflow
- Evaluates performance
- Registers model in MLflow registry
- Outputs: Model artifacts, evaluation metrics, registry entry

**DVC Benefits:**
- Only reruns stages when dependencies change
- Caches intermediate results
- Enables reproducibility

### Critical File Artifacts

**Model Artifacts (saved during training):**
- `models/saved_models/scaler.joblib` - Fitted StandardScaler
- `models/saved_models/encoder.joblib` - Fitted OneHotEncoder
- `models/saved_models/feature_names.joblib` - Feature name mapping
- `models/saved_models/model_*.joblib` - Trained model

**IMPORTANT:** For inference, you MUST load the scaler and encoder from training to ensure consistency. The `_pipeline` model handles this automatically.

### Model Registry and Versioning

Models are tracked in two places:
1. **Local registry:** `models/model_registry/registry.json`
2. **MLflow registry:** Accessible via MLflow UI

**Model lifecycle stages:**
- `None` / `Development` - Experimental
- `Staging` - Ready for testing
- `Production` - Active serving
- `Archived` - Retired

**Version strategy:** Configured in `config.yaml` (`versioning_strategy`)
- `timestamp` - Uses timestamp as version
- `auto_increment` - Sequential numbering
- `semantic` - Manual semantic versioning

## Common Development Workflows

### Adding a New Feature

1. Edit `src/features/engineer.py` to add feature creation logic
2. Update `config/config.yaml` to include the new feature name
3. Run `dvc repro -f` to regenerate features and retrain
4. Compare metrics in MLflow UI

### Experimenting with Hyperparameters

1. Edit `config/config.yaml` hyperparameters section
2. Run `dvc repro` (only training stage will rerun)
3. View results in MLflow UI at http://localhost:5000

### Training Multiple Models for Comparison

```bash
bash train_multiple_models.sh
# Trains 3 models with different settings
# Compare side-by-side in MLflow UI
```

### Deploying Model Updates

1. Train new model: `dvc repro`
2. Verify metrics in MLflow UI
3. Promote to Production stage in MLflow UI
4. Restart model serving: `python serve_model_api.py`

### Testing Changes

Currently no automated tests (tests/ directory is empty). When adding tests:
```bash
pytest tests/
pytest tests/test_features.py -v  # Single file
pytest tests/ --cov=src           # With coverage
```

## Data Pipeline Details

### Data Quality Checks (src/data/ingest.py)

Automatically validates:
- Missing values detection and handling
- Duplicate row detection
- Outlier detection using IQR method
- Data type validation

Reports saved to: `logs/data_quality_report.json`

### Feature Engineering (src/features/engineer.py)

**Derived features created:**
- `rooms_per_household` = total_rooms / households
- `bedrooms_per_room` = total_bedrooms / total_rooms
- `population_per_household` = population / households

**Transformations:**
- Categorical encoding: One-hot encoding for `ocean_proximity`
- Numerical scaling: StandardScaler on all numerical features

**CRITICAL:** Artifacts (scaler, encoder) MUST be saved during training and loaded during inference to prevent training/serving skew.

## MLflow Model Serving

### Serving Format

The API expects data in `dataframe_split` format:

```json
{
  "dataframe_split": {
    "columns": ["median_income", "housing_median_age", "total_rooms",
                "total_bedrooms", "population", "households",
                "latitude", "longitude", "ocean_proximity"],
    "data": [[8.3252, 41.0, 880, 129, 322, 126, 37.88, -122.23, "NEAR BAY"]]
  }
}
```

### Making Predictions

```python
import requests

response = requests.post(
    'http://localhost:5001/invocations',
    json={'dataframe_split': {
        'columns': list(house_data.keys()),
        'data': [list(house_data.values())]
    }}
)
prediction = response.json()['predictions'][0]
```

## Logging and Monitoring

**Pipeline logs:** `logs/pipeline.log` (configured in config.yaml)
**MLflow runs:** `logs/mlruns/` or configured tracking URI
**Evaluation reports:** `logs/evaluation_report.json`
**Data quality reports:** `logs/data_quality_report.json`

**Log level:** Set in `config/config.yaml` under `logging.level`

## Important Implementation Notes

### Training/Serving Consistency

The project ensures consistency through:
1. **Config-driven:** All parameters from config.yaml
2. **Artifact persistence:** Scaler/encoder saved during training
3. **MLflow pipeline model:** Bundles preprocessing + model together
4. **DVC caching:** Guarantees reproducible data processing

**When serving:** Use `housing_price_predictor_pipeline` model which includes all preprocessing.

### Model Selection Logic

Model type is selected via `config/config.yaml`:
```yaml
model:
  type: "random_forest"  # Change to: linear_regression, gradient_boosting
  hyperparameters:
    random_forest:
      n_estimators: 275
      max_depth: 20
      # ... other params
```

Training code (`src/models/train.py`) dynamically instantiates the correct model class.

### DVC Dependencies

DVC tracks file dependencies and only reruns stages when:
- Source code changes (e.g., `src/features/engineer.py`)
- Configuration changes (`config/config.yaml`)
- Input data changes (upstream outputs)

**To force rerun:** Use `dvc repro -f`

### Airflow DAGs (Optional)

If Airflow is configured, the DAG (`airflow/dags/housing_ml_pipeline.py`) orchestrates:
- Data ingestion task
- Feature engineering task
- Model training task
- Model evaluation task

**DAG schedule:** Configurable in the DAG file (default: manual trigger)

## Troubleshooting

**MLflow UI not starting:**
- Check if port 5000 is available
- Set custom port: `mlflow ui --port 5001`

**DVC pipeline fails:**
- Check `logs/pipeline.log` for detailed errors
- Ensure all dependencies in `requirements.txt` are installed
- Verify `config/config.yaml` syntax is valid YAML

**Model serving errors:**
- Ensure model is registered in MLflow: check `mlflow ui`
- Verify tracking URI in config.yaml matches where models are stored
- Use `--examples` flag to see correct API format

**Import errors:**
- Run `pip install -e .` to install project as package
- Ensure you're in the virtual environment

**Data not found:**
- First run will fetch data automatically
- If manual fetch needed, run `python pipeline/stage_01_ingest_data.py`

## Git Workflow

The repository uses DVC for data versioning:
- **Commit to Git:** Code files, config, `dvc.yaml`, `dvc.lock`, `.dvc` files
- **Don't commit:** `data/`, `models/saved_models/`, `logs/mlruns/`, `.venv/`
- **DVC tracks:** Large data files and model artifacts

When making changes:
1. Modify code/config
2. Run `dvc repro` to update pipeline
3. Commit code changes AND `dvc.lock` together
4. `dvc.lock` records exact data/model versions used

## Performance Metrics

**Current baseline (Random Forest, n_estimators=275):**
- RMSE: ~$48,000-50,000
- R²: ~0.80-0.82
- MAE: ~$32,000-35,000

Thresholds are configurable in `config/config.yaml`:
```yaml
evaluation:
  threshold_rmse: 50000
  threshold_r2: 0.75
```

## Key Design Patterns

1. **Configuration Management:** Single source of truth in config.yaml
2. **Modular Pipeline:** Each stage is independently testable
3. **Artifact Versioning:** All artifacts tracked and versioned
4. **Experiment Tracking:** Every run logged to MLflow
5. **Training/Serving Parity:** Same preprocessing in training and inference
6. **Smart Caching:** DVC avoids redundant computation
