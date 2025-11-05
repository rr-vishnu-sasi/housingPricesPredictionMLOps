"""
Apache Airflow DAG for Housing Price Prediction ML Pipeline

This is a production-ready Airflow DAG that orchestrates your complete
ML pipeline with monitoring, retries, and alerts.

When to use Airflow:
- Scheduled retraining (daily, weekly, monthly)
- Complex dependencies between tasks
- Need monitoring and alerts
- Multi-step ML pipelines
- Production environments
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.email import EmailOperator
import sys
import os
import json

# Project root directory
PROJECT_ROOT = '/Users/vishnu.sasi/Downloads/Vishnu-Personal/housingPricesPredictionProject'

# ========================================================================
# STEP 1: Default Arguments (Settings for all tasks)
# ========================================================================
default_args = {
    # Who owns this DAG
    'owner': 'mlops-team',

    # Email settings
    'email': ['your.email@example.com'],
    'email_on_failure': True,     # Email if task fails
    'email_on_retry': False,      # Don't email on retry
    'email_on_success': False,    # Don't email on success (too many emails!)

    # Retry settings
    'retries': 2,                 # Retry failed tasks twice
    'retry_delay': timedelta(minutes=5),  # Wait 5 minutes between retries

    # Execution settings
    'depends_on_past': False,     # Don't wait for previous run to succeed
    'start_date': datetime(2025, 10, 1),  # When DAG becomes active
    'execution_timeout': timedelta(hours=2),  # Kill task after 2 hours
}

# ========================================================================
# STEP 2: Create the DAG
# ========================================================================
dag = DAG(
    # DAG identification
    dag_id='housing_price_ml_pipeline',

    # Settings
    default_args=default_args,
    description='End-to-end ML pipeline for housing price prediction with MLflow',

    # Schedule
    schedule_interval='@daily',   # Run every day at midnight
    # Alternative schedules:
    # schedule_interval='0 3 * * *'  # 3 AM daily (cron)
    # schedule_interval='@weekly'    # Every week
    # schedule_interval='@hourly'    # Every hour
    # schedule_interval=None         # Manual trigger only

    # Backfill settings
    catchup=False,  # Don't run for past dates

    # Organization
    tags=['ml', 'housing-prediction', 'production', 'mlflow'],

    # Documentation (shows in Airflow UI)
    doc_md="""
    # Housing Price Prediction ML Pipeline

    This DAG orchestrates the complete ML workflow:
    1. Data ingestion with quality validation
    2. Feature engineering with artifact persistence
    3. Model training with MLflow tracking
    4. Performance validation (quality gates)
    5. Model promotion to staging if validation passes

    **Schedule:** Daily at midnight
    **Owner:** MLOps Team
    **Alerts:** Sent to team email on failure
    """
)

# ========================================================================
# STEP 3: Define Tasks
# ========================================================================

# ──────────────────────────────────────────────────────────────────────
# Task 1: Data Ingestion
# ──────────────────────────────────────────────────────────────────────
task_ingest_data = BashOperator(
    task_id='ingest_data',
    bash_command=f'cd {PROJECT_ROOT} && python pipeline/stage_01_ingest_data.py',

    # Task-specific settings
    retries=3,  # Data fetching might be flaky, retry more

    # Documentation
    doc_md="""
    ## Data Ingestion Task

    Fetches California Housing dataset and validates quality.

    **What it does:**
    - Fetches 20,640 housing records
    - Checks for missing values, duplicates, outliers
    - Saves to: data/raw/ and data/processed/

    **Outputs:**
    - data/raw/housing_data.csv
    - data/processed/housing_processed.csv
    - logs/data_quality_report.json

    **Expected Duration:** 5 seconds
    """,

    dag=dag,
)

# ──────────────────────────────────────────────────────────────────────
# Task 2: Feature Engineering
# ──────────────────────────────────────────────────────────────────────
task_feature_engineering = BashOperator(
    task_id='feature_engineering',
    bash_command=f'cd {PROJECT_ROOT} && python pipeline/stage_02_feature_engineering.py',

    doc_md="""
    ## Feature Engineering Task

    Transforms raw data into ML-ready features.

    **What it does:**
    - Creates derived features (rooms_per_household, etc.)
    - Encodes categorical features (one-hot encoding)
    - Scales numerical features (StandardScaler)
    - Saves transformation artifacts

    **Outputs:**
    - data/features/housing_features.csv
    - models/saved_models/scaler.joblib
    - models/saved_models/encoder.joblib

    **Expected Duration:** 3 seconds
    """,

    dag=dag,
)

# ──────────────────────────────────────────────────────────────────────
# Task 3: Model Training with MLflow
# ──────────────────────────────────────────────────────────────────────
task_train_model = BashOperator(
    task_id='train_model',
    bash_command=f'cd {PROJECT_ROOT} && python pipeline/stage_03_train_model_mlflow.py',

    doc_md="""
    ## Model Training Task

    Trains Random Forest model with MLflow tracking.

    **What it does:**
    - Trains model on 80% of data
    - Evaluates on 20% validation set
    - Logs to MLflow (params, metrics, model)
    - Registers model in MLflow Model Registry

    **Outputs:**
    - models/saved_models/model_*.joblib
    - logs/evaluation_report.json
    - MLflow run with all tracking data

    **Expected Duration:** 30-60 seconds
    """,

    dag=dag,
)

# ──────────────────────────────────────────────────────────────────────
# Task 4: Model Validation (Quality Gate)
# ──────────────────────────────────────────────────────────────────────
def validate_model_performance(**context):
    """
    Validates model meets quality thresholds.

    Raises exception if model is too poor.
    This stops the pipeline from deploying bad models!
    """
    report_path = f'{PROJECT_ROOT}/logs/evaluation_report.json'

    with open(report_path, 'r') as f:
        report = json.load(f)

    metrics = report['metrics']
    r2_score = metrics['r2_score']
    rmse = metrics['rmse']

    print("=" * 60)
    print("MODEL VALIDATION")
    print("=" * 60)
    print(f"\nModel Performance:")
    print(f"  R² Score: {r2_score:.4f}")
    print(f"  RMSE: ${rmse:,.2f}")

    # Define thresholds
    MIN_R2 = 0.75
    MAX_RMSE = 50000

    # Check thresholds
    if r2_score < MIN_R2:
        raise ValueError(
            f"Model R² too low: {r2_score:.4f} < {MIN_R2}\n"
            f"Model quality unacceptable. Pipeline stopped."
        )

    if rmse > MAX_RMSE:
        raise ValueError(
            f"Model RMSE too high: ${rmse:,.2f} > ${MAX_RMSE:,.2f}\n"
            f"Model quality unacceptable. Pipeline stopped."
        )

    print(f"\n✓ Model validation PASSED!")
    print(f"  R² {r2_score:.4f} >= {MIN_R2} ✓")
    print(f"  RMSE ${rmse:,.2f} <= ${MAX_RMSE:,.2f} ✓")

    # Return metrics to Airflow (can be viewed in UI)
    context['task_instance'].xcom_push(key='r2_score', value=r2_score)
    context['task_instance'].xcom_push(key='rmse', value=rmse)

    return 'promote_to_staging'  # Next task to run


task_validate_model = BranchPythonOperator(
    task_id='validate_model',
    python_callable=validate_model_performance,
    provide_context=True,  # Pass context to function

    doc_md="""
    ## Model Validation Task (Quality Gate)

    Critical checkpoint that prevents bad models from reaching staging/production.

    **Checks:**
    - R² Score >= 0.75
    - RMSE <= $50,000

    **If PASS:** Pipeline continues to promotion
    **If FAIL:** Pipeline stops, alert sent

    **This is a critical MLOps pattern:** Automated quality gates
    """,

    dag=dag,
)

# ──────────────────────────────────────────────────────────────────────
# Task 5: Promote to Staging (Conditional)
# ──────────────────────────────────────────────────────────────────────
def promote_model_to_staging(**context):
    """
    Promotes validated model to staging.
    """
    sys.path.insert(0, PROJECT_ROOT)
    from src.utils import load_config
    from src.models.registry import ModelRegistry

    config = load_config()
    registry = ModelRegistry(config)

    # Get latest model
    latest_model = registry.get_latest_model()

    if latest_model:
        version_id = latest_model['version_id']

        # Promote to staging
        success = registry.transition_model_stage(
            version_id=version_id,
            new_stage='staging',
            comment='Auto-promoted by Airflow after passing validation'
        )

        if success:
            print(f"✓ Model {version_id} promoted to STAGING")

            # Push to Airflow XCom (cross-communication)
            context['task_instance'].xcom_push(key='promoted_version', value=version_id)

            return version_id
        else:
            raise ValueError("Failed to promote model")
    else:
        raise ValueError("No model found to promote")


task_promote_staging = PythonOperator(
    task_id='promote_to_staging',
    python_callable=promote_model_to_staging,
    provide_context=True,

    doc_md="""
    ## Model Promotion Task

    Promotes validated model to staging environment.

    **What it does:**
    - Gets latest trained model
    - Updates stage: development → staging
    - Records promotion in model registry

    **Only runs if:** Validation passed
    """,

    dag=dag,
)

# ──────────────────────────────────────────────────────────────────────
# Task 6: Send Success Notification (Optional)
# ──────────────────────────────────────────────────────────────────────
def send_success_notification(**context):
    """
    Sends notification that pipeline completed successfully.
    """
    # Get metrics from validation task
    ti = context['task_instance']
    r2_score = ti.xcom_pull(task_ids='validate_model', key='r2_score')
    rmse = ti.xcom_pull(task_ids='validate_model', key='rmse')
    version_id = ti.xcom_pull(task_ids='promote_to_staging', key='promoted_version')

    message = f"""
    ✅ ML Pipeline Completed Successfully!

    Model Version: {version_id}
    Performance:
      • R² Score: {r2_score:.4f}
      • RMSE: ${rmse:,.2f}

    Model promoted to: STAGING

    Next steps:
    1. Test model in staging
    2. If passes, promote to production
    3. Deploy to serving infrastructure
    """

    print(message)

    # In production, you'd send to Slack/Email/PagerDuty
    # For now, just log it
    return message


task_notify_success = PythonOperator(
    task_id='notify_success',
    python_callable=send_success_notification,
    provide_context=True,
    dag=dag,
)

# ========================================================================
# STEP 4: Define Task Dependencies (Workflow)
# ========================================================================

# Linear flow: Each task depends on previous one
task_ingest_data >> task_feature_engineering >> task_train_model >> task_validate_model

# Conditional: Only promote if validation passed
task_validate_model >> task_promote_staging >> task_notify_success

# ========================================================================
# How This Works in Production
# ========================================================================
"""
EXAMPLE: Daily Retraining Workflow

Day 1:
  00:00 - Airflow scheduler wakes up
  00:01 - Checks schedule: @daily → Time to run!
  00:02 - Creates DAG Run instance
  00:03 - Starts task: ingest_data
  00:08 - ✓ Data ingested (20,640 rows)
  00:09 - Starts task: feature_engineering
  00:12 - ✓ Features engineered (15 features)
  00:13 - Starts task: train_model
  00:45 - ✓ Model trained (R²=82.1%, RMSE=$48,500)
  00:46 - Starts task: validate_model
  00:47 - ✓ Validation passed (R² >= 0.75, RMSE <= $50k)
  00:48 - Starts task: promote_to_staging
  00:49 - ✓ Model v_20251101_0048 promoted to staging
  00:50 - Starts task: notify_success
  00:51 - ✓ Notification sent
  00:52 - DAG Run complete ✅

Day 2:
  (Same workflow, automatic!)

Day 3:
  00:00 - Pipeline starts
  00:13 - Starts task: train_model
  00:45 - ✗ Model trained but R²=74% (below threshold!)
  00:46 - Starts task: validate_model
  00:47 - ✗ Validation FAILED (R² < 0.75)
  00:48 - Pipeline stopped ❌
  00:49 - Alert email sent: "Model quality too low!"
  00:50 - DAG Run marked as FAILED

  → You receive email, investigate, fix issue
  → Next day: Pipeline tries again
"""

# ========================================================================
# Advanced Features (Examples)
# ========================================================================

# Parallel Tasks (run simultaneously)
"""
task_a >> [task_b, task_c] >> task_d

Visual:
       ┌─ task_b ─┐
task_a ┤          ├─ task_d
       └─ task_c ─┘

Both task_b and task_c run at the same time (parallel)
"""

# Conditional Branching
"""
                    ┌─ good_model → deploy_prod
task_validate ──────┤
                    └─ bad_model → alert_team
"""

# Dynamic Task Generation
"""
for i in range(5):
    task = BashOperator(task_id=f'train_model_{i}', ...)
    # Creates 5 tasks dynamically
"""

# Task Groups (organize related tasks)
"""
with TaskGroup('preprocessing'):
    clean_data >> validate_data >> transform_data
"""