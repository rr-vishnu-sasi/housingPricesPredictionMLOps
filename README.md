# Housing Price Prediction - End-to-End MLOps Project

A comprehensive MLOps project demonstrating best practices for building, deploying, and maintaining machine learning systems in production. This project predicts housing prices using the California Housing dataset and implements the complete ML lifecycle.

## 🎯 Project Goal

This project is designed for **MLOps beginners transitioning to an MLOps career**. It demonstrates practical implementation of MLOps principles including:
- Data versioning and validation
- Reproducible experiments
- Model versioning and registry
- Automated pipelines
- Model monitoring and evaluation
- Production-ready code structure

---

## 📁 Project Structure

```
housingPricesPredictionProject/
│
├── config/                      # Configuration files
│   └── config.yaml             # Central configuration (hyperparameters, paths, etc.)
│
├── src/                        # Source code
│   ├── data/                   # Data processing modules
│   │   ├── __init__.py
│   │   └── ingest.py          # Data ingestion and quality checks
│   │
│   ├── features/               # Feature engineering
│   │   ├── __init__.py
│   │   └── engineer.py        # Feature transformation and engineering
│   │
│   ├── models/                 # Model training and registry
│   │   ├── __init__.py
│   │   ├── train.py           # Model training logic
│   │   └── registry.py        # Model versioning and metadata
│   │
│   ├── evaluation/             # Model evaluation
│   │   ├── __init__.py
│   │   └── evaluate.py        # Metrics and performance analysis
│   │
│   ├── serving/                # Model serving/inference
│   │   ├── __init__.py
│   │   └── predict.py         # Prediction and serving logic
│   │
│   └── utils.py               # Utility functions
│
├── data/                       # Data storage (versioned with DVC in production)
│   ├── raw/                   # Raw, immutable data
│   ├── processed/             # Cleaned data
│   └── features/              # Engineered features
│
├── models/                     # Model artifacts
│   ├── saved_models/          # Trained models and artifacts
│   └── model_registry/        # Model metadata and registry
│
├── logs/                       # Logs and experiment tracking
│   └── pipeline.log
│
├── notebooks/                  # Jupyter notebooks for exploration
│
├── examples/                   # Example scripts
│   └── inference_example.py   # How to use trained models
│
├── tests/                      # Unit and integration tests
│
├── main_pipeline.py           # Main training pipeline
├── requirements.txt           # Python dependencies
├── setup.py                   # Package setup
└── README.md                  # This file
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd housingPricesPredictionProject

# Create virtual environment (if not already created)
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### 2. Run the Training Pipeline

```bash
python main_pipeline.py
```

This will:
1. ✅ Fetch and validate data
2. ✅ Engineer features
3. ✅ Train a model
4. ✅ Evaluate performance
5. ✅ Save and register the model

### 3. Make Predictions

```bash
python examples/inference_example.py
```

---

## 📚 MLOps Concepts Explained

This project demonstrates key MLOps principles that are essential for production ML systems:

### 1. **Configuration Management** 📝

**Location:** `config/config.yaml`

**Why it matters:**
- Enables **reproducibility** - same config = same results
- Facilitates **experimentation** - change parameters without code changes
- Supports **environment management** - dev, staging, production configs
- Enables **version control** - track what parameters were used for each model

**Example:**
```yaml
model:
  type: "random_forest"
  hyperparameters:
    random_forest:
      n_estimators: 100
      max_depth: 20
```

### 2. **Data Quality Checks** ✅

**Location:** `src/data/ingest.py`

**Why it matters:**
- Poor data quality is the #1 cause of ML failures
- Catches issues **before** they affect training
- Detects **data drift** in production
- Maintains **data integrity**

**Checks implemented:**
- Missing values detection
- Duplicate detection
- Outlier detection
- Schema validation

### 3. **Feature Engineering Pipeline** 🔧

**Location:** `src/features/engineer.py`

**Why it matters:**
- **Training/Serving consistency** - same transformations in prod
- **Artifact persistence** - save scalers/encoders for inference
- **Feature versioning** - track which features are used
- **Modularity** - easy to add/remove features

**Critical MLOps pattern:**
```python
# Training: fit_transform
scaler.fit_transform(X_train)

# Inference: transform only (using fitted scaler)
scaler.transform(X_new)
```

### 4. **Experiment Tracking** 📊

**Location:** `src/models/train.py`

**Why it matters:**
- Compare different models and hyperparameters
- Track what worked and what didn't
- Enable **reproducibility**
- Support **model selection**

**Tracked information:**
- Hyperparameters
- Training time
- Dataset size
- Model architecture
- Random seeds

### 5. **Model Evaluation & Validation** 📈

**Location:** `src/evaluation/evaluate.py`

**Why it matters:**
- Multiple metrics tell the full story
- **Threshold checks** prevent bad models reaching production
- **Residual analysis** identifies model biases
- Enables **automated validation** in CI/CD

**Metrics implemented:**
- RMSE (Root Mean Squared Error)
- MAE (Mean Absolute Error)
- R² Score
- MAPE (Mean Absolute Percentage Error)

### 6. **Model Registry** 📦

**Location:** `src/models/registry.py`

**Why it matters:**
- **Single source of truth** for all models
- Track **model lineage** (data, code, parameters)
- Enable **rollback** to previous versions
- Manage **model lifecycle** (dev → staging → production)
- Support **A/B testing**

**Model lifecycle stages:**
1. **Development** - Experimental models
2. **Staging** - Models ready for testing
3. **Production** - Active serving models
4. **Archived** - Retired models

### 7. **Model Serving/Inference** 🎯

**Location:** `src/serving/predict.py`

**Why it matters:**
- Consistent preprocessing (avoids training/serving skew)
- **Latency monitoring**
- **Prediction logging** for auditing
- **Batch and real-time** prediction support

**Production considerations:**
- Input validation
- Error handling
- Performance monitoring
- Scalability

### 8. **Logging & Monitoring** 📝

**Location:** `src/utils.py`, `logs/`

**Why it matters:**
- **Debugging** production issues
- **Auditing** for compliance
- **Performance monitoring**
- **Alert triggering**

**What to log:**
- Data quality metrics
- Model performance
- Prediction latency
- Errors and exceptions

---

## 🔄 ML Pipeline Workflow

```
┌─────────────────┐
│  Data Ingestion │  ← Fetch data, validate quality
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Feature Engineer │  ← Transform data, create features
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Model Training  │  ← Train model, track experiments
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Evaluation    │  ← Calculate metrics, validate
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Model Registry  │  ← Version, tag, promote model
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Serving      │  ← Deploy, monitor, predict
└─────────────────┘
```

---

## 🛠️ Key Files Explained

### `main_pipeline.py`
**Purpose:** Orchestrates the entire training pipeline
**MLOps Concept:** Pipeline automation
**Production equivalent:** Airflow DAG, Kubeflow Pipeline, AWS Step Functions

### `config/config.yaml`
**Purpose:** Centralized configuration
**MLOps Concept:** Configuration management
**Benefits:** Reproducibility, experimentation, version control

### `src/models/registry.py`
**Purpose:** Model versioning and metadata tracking
**MLOps Concept:** Model registry
**Production equivalent:** MLflow Registry, SageMaker Registry

### `src/serving/predict.py`
**Purpose:** Production inference
**MLOps Concept:** Model serving
**Production equivalent:** FastAPI service, SageMaker endpoint

---

## 📊 Model Performance Tracking

After running the pipeline, check:

1. **Data Quality Report:** `logs/data_quality_report.json`
   - Missing values
   - Duplicates
   - Outliers

2. **Evaluation Report:** `logs/evaluation_report.json`
   - Performance metrics
   - Threshold checks
   - Residual analysis

3. **Model Registry:** `models/model_registry/registry.json`
   - All registered models
   - Versions and metadata
   - Stage transitions

4. **Training Logs:** `logs/pipeline.log`
   - Detailed execution logs
   - Errors and warnings
   - Timing information

---

## 🎓 MLOps Career Skills Demonstrated

This project showcases skills essential for MLOps roles:

### Core MLOps Skills
- ✅ **Pipeline Automation** - End-to-end automated workflow
- ✅ **Model Versioning** - Track and manage model versions
- ✅ **Experiment Tracking** - Compare different models
- ✅ **Data Validation** - Ensure data quality
- ✅ **Model Registry** - Centralized model management
- ✅ **Model Serving** - Production inference patterns
- ✅ **Monitoring & Logging** - Observability

### Software Engineering Skills
- ✅ **Modular Code** - Separation of concerns
- ✅ **Configuration Management** - Externalized config
- ✅ **Error Handling** - Robust error management
- ✅ **Documentation** - Clear code and API docs
- ✅ **Version Control Ready** - Git-friendly structure

### Production-Ready Patterns
- ✅ **Training/Serving Consistency** - Same preprocessing
- ✅ **Artifact Persistence** - Save all necessary artifacts
- ✅ **Input Validation** - Validate before prediction
- ✅ **Performance Monitoring** - Track latency and quality

---

## 🚀 Next Steps: Taking It Further

To make this more production-ready, consider adding:

### 1. **MLflow Integration**
```python
# Install MLflow
pip install mlflow

# Set enable_mlflow: true in config.yaml
# MLflow will track experiments automatically
```

### 2. **Data Version Control (DVC)**
```bash
# Install DVC
pip install dvc

# Initialize DVC
dvc init

# Track data
dvc add data/raw/housing_data.csv
git add data/raw/housing_data.csv.dvc
git commit -m "Track data with DVC"
```

### 3. **API Serving with FastAPI**
```python
# Install FastAPI
pip install fastapi uvicorn

# Create API endpoint (examples coming in v2)
```

### 4. **Containerization with Docker**
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "main_pipeline.py"]
```

### 5. **CI/CD Pipeline**
- Automated testing on commit
- Model training on schedule
- Automatic deployment if metrics pass

### 6. **Monitoring & Alerting**
- Prometheus for metrics
- Grafana for dashboards
- Alertmanager for notifications

### 7. **A/B Testing**
- Deploy multiple model versions
- Route traffic between versions
- Compare performance

---

## 📖 Learning Resources

To deepen your MLOps knowledge:

### Books
- "Designing Machine Learning Systems" by Chip Huyen
- "Machine Learning Engineering" by Andriy Burkov
- "Building Machine Learning Powered Applications" by Emmanuel Ameisen

### Online Courses
- MLOps Specialization (Coursera)
- Full Stack Deep Learning
- Made With ML (MLOps course)

### Tools to Learn
- **MLflow** - Experiment tracking & model registry
- **DVC** - Data version control
- **Kubeflow** - ML on Kubernetes
- **Apache Airflow** - Pipeline orchestration
- **FastAPI** - API serving
- **Docker** - Containerization
- **Kubernetes** - Container orchestration

---

## 🤝 Contributing

This is a learning project. Feel free to:
- Add new features
- Improve documentation
- Fix bugs
- Share your improvements

---

## 📝 License

MIT License - Feel free to use this project for learning and portfolio purposes.

---

## 💡 Key Takeaways for MLOps Career

1. **MLOps is about reliability:** Production ML is more about infrastructure than algorithms

2. **Reproducibility is critical:** If you can't reproduce it, you can't trust it

3. **Monitor everything:** What you don't measure, you can't improve

4. **Automation is key:** Manual processes don't scale

5. **Start simple, iterate:** Don't over-engineer initially, add complexity as needed

6. **Documentation matters:** Your future self (and colleagues) will thank you

7. **Think production-first:** Consider serving, monitoring, and maintenance from day one

---

## 🎯 Interview Talking Points

When discussing this project in interviews, highlight:

1. **End-to-end pipeline:** "I built a complete ML pipeline from data ingestion to serving"

2. **MLOps best practices:** "I implemented model registry, experiment tracking, and monitoring"

3. **Production readiness:** "The code follows production patterns like configuration management and artifact versioning"

4. **Reproducibility:** "Every experiment can be reproduced using configuration and logging"

5. **Scalability:** "The modular design allows easy scaling and component replacement"

---

## 📧 Contact

For questions or feedback about this project, feel free to reach out!

---

**Happy Learning! 🚀**

Remember: MLOps is a journey, not a destination. Start simple, learn continuously, and build incrementally.
