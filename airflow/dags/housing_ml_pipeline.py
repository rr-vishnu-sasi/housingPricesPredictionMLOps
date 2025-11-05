"""
Apache Airflow DAG for Housing Price Prediction ML Pipeline

Production-Ready DAG for automated ML retraining

To use this DAG:
1. Install Airflow (Python 3.8-3.12)
2. Set AIRFLOW_HOME environment variable
3. Copy this file to: $AIRFLOW_HOME/dags/
4. Start Airflow: airflow scheduler & airflow webserver
5. Access UI: http://localhost:8080
6. Enable DAG in UI
7. Watch it run!

MLOps Pattern: Scheduled Retraining
This is how companies retrain models automatically in production.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.utils.dates import days_ago
import os
import json
import sys

# ========================================================================
# CONFIGURATION
# ========================================================================

# IMPORTANT: Update this to your project path!
PROJECT_ROOT = os.getenv(
    'HOUSING_PIPELINE_ROOT',
    '/Users/vishnu.sasi/Downloads/Vishnu-Personal/housingPricesPredictionProject'
)

# Email for alerts (update this!)
ALERT_EMAIL = 'your.email@example.com'

# Quality thresholds
MIN_R2_SCORE = 0.75
MAX_RMSE = 50000

# ========================================================================
# DEFAULT ARGUMENTS (Applied to all tasks)
# ========================================================================
default_args = {
    # Ownership
    'owner': 'mlops-team',

    # Email settings
    'email': [ALERT_EMAIL],
    'email_on_failure': True,    # Alert if task fails
    'email_on_retry': False,     # Don't spam on retries
    'email_on_success': False,   # Don't spam on success

    # Retry settings
    'retries': 2,                # Retry failed tasks twice
    'retry_delay': timedelta(minutes=5),  # Wait 5 min between retries
    'execution_timeout': timedelta(hours=1),  # Kill if takes > 1 hour

    # Execution
    'depends_on_past': False,    # Each run is independent
}

# ========================================================================
# CREATE DAG
# ========================================================================
with DAG(
    # DAG Identification
    dag_id='housing_price_ml_pipeline',

    # Settings
    default_args=default_args,
    description='Automated ML pipeline for housing price prediction with MLflow tracking',

    # Schedule: When to run
    schedule_interval='@daily',  # Every day at midnight

    # Alternatives:
    # schedule_interval='0 3 * * *',    # Every day at 3 AM
    # schedule_interval='@weekly',      # Every Sunday
    # schedule_interval='0 */6 * * *',  # Every 6 hours
    # schedule_interval=None,           # Manual trigger only

    # Start date
    start_date=days_ago(1),  # Start from yesterday

    # Backfill
    catchup=False,  # Don't run for historical dates

    # Organization
    tags=['ml-pipeline', 'housing-prediction', 'production', 'mlflow', 'dvc'],

    # Documentation (shows in Airflow UI)
    doc_md="""
    # Housing Price Prediction ML Pipeline

    ## Overview
    Automated daily retraining pipeline for housing price prediction model.

    ## Pipeline Stages:
    1. **Data Ingestion** - Fetch and validate housing data
    2. **Feature Engineering** - Transform data into ML features
    3. **Model Training** - Train Random Forest with MLflow tracking
    4. **Model Validation** - Quality gates (R² >= 0.75, RMSE <= $50k)
    5. **Staging Promotion** - Promote validated models
    6. **Success Notification** - Alert team of completion

    ## Schedule
    **Runs:** Daily at midnight (00:00)
    **Duration:** ~1 minute
    **Next Run:** Check DAG dashboard

    ## Monitoring
    - **Success:** Model trained and promoted to staging
    - **Failure:** Email alert sent to team
    - **Metrics:** Tracked in MLflow UI

    ## Owner
    MLOps Team
    """,

) as dag:

    # ====================================================================
    # TASK 1: Data Ingestion
    # ====================================================================
    task_ingest_data = BashOperator(
        task_id='ingest_data',
        bash_command=f'cd {PROJECT_ROOT} && python pipeline/stage_01_ingest_data.py',

        # Task-specific overrides
        retries=3,  # Data fetching can be flaky, retry more
        retry_delay=timedelta(minutes=2),

        doc_md="""
        ### Data Ingestion Task

        Fetches California Housing dataset and performs quality validation.

        **Duration:** ~5 seconds
        **Output:** data/raw/housing_data.csv, data/processed/housing_processed.csv
        **Checks:** Missing values, duplicates, outliers
        """,
    )

    # ====================================================================
    # TASK 2: Feature Engineering
    # ====================================================================
    task_feature_engineering = BashOperator(
        task_id='feature_engineering',
        bash_command=f'cd {PROJECT_ROOT} && python pipeline/stage_02_feature_engineering.py',

        doc_md="""
        ### Feature Engineering Task

        Transforms raw data into ML-ready features.

        **Duration:** ~3 seconds
        **Creates:** Derived features (rooms_per_household, etc.)
        **Output:** data/features/housing_features.csv, transformation artifacts
        """,
    )

    # ====================================================================
    # TASK 3: Model Training with MLflow
    # ====================================================================
    task_train_model = BashOperator(
        task_id='train_model',
        bash_command=f'cd {PROJECT_ROOT} && python pipeline/stage_03_train_model_mlflow.py',

        doc_md="""
        ### Model Training Task

        Trains Random Forest model with MLflow experiment tracking.

        **Duration:** ~30 seconds
        **Tracks:** Parameters, metrics, model artifacts in MLflow
        **Registers:** Model in MLflow Model Registry
        **Expected:** R² ~82%, RMSE ~$48,500
        """,
    )

    # ====================================================================
    # TASK 4: Model Validation (Quality Gate)
    # ====================================================================
    def validate_model_performance(**context):
        """
        Validates model meets quality thresholds.

        This is a CRITICAL checkpoint (quality gate).
        Bad models don't make it to production!

        Returns:
            'promote_to_staging' if model is good
            'send_failure_alert' if model is poor
        """
        report_path = os.path.join(PROJECT_ROOT, 'logs/evaluation_report.json')

        # Load evaluation report
        with open(report_path, 'r') as f:
            report = json.load(f)

        metrics = report['metrics']
        r2_score = metrics['r2_score']
        rmse = metrics['rmse']

        print("=" * 70)
        print("MODEL VALIDATION - QUALITY GATE")
        print("=" * 70)
        print(f"\n📊 Model Performance:")
        print(f"   R² Score: {r2_score:.4f}")
        print(f"   RMSE: ${rmse:,.2f}")
        print(f"\n🎯 Thresholds:")
        print(f"   R² >= {MIN_R2_SCORE}")
        print(f"   RMSE <= ${MAX_RMSE:,.0f}")

        # Push metrics to XCom (for other tasks to access)
        ti = context['task_instance']
        ti.xcom_push(key='r2_score', value=r2_score)
        ti.xcom_push(key='rmse', value=rmse)

        # Validate thresholds
        if r2_score < MIN_R2_SCORE:
            print(f"\n❌ VALIDATION FAILED: R² {r2_score:.4f} < {MIN_R2_SCORE}")
            return 'send_failure_alert'  # Branch to failure path

        if rmse > MAX_RMSE:
            print(f"\n❌ VALIDATION FAILED: RMSE ${rmse:,.0f} > ${MAX_RMSE:,.0f}")
            return 'send_failure_alert'  # Branch to failure path

        print(f"\n✅ VALIDATION PASSED!")
        print(f"   ✓ R² {r2_score:.4f} >= {MIN_R2_SCORE}")
        print(f"   ✓ RMSE ${rmse:,.2f} <= ${MAX_RMSE:,.0f}")

        return 'promote_to_staging'  # Branch to success path


    task_validate_model = BranchPythonOperator(
        task_id='validate_model',
        python_callable=validate_model_performance,
        provide_context=True,

        doc_md="""
        ### Model Validation Task (Quality Gate)

        **Critical checkpoint** that prevents poor models from reaching production.

        **Checks:**
        - R² Score >= 0.75
        - RMSE <= $50,000

        **If PASS:** Continue to staging promotion
        **If FAIL:** Stop pipeline, send alert

        This implements the MLOps pattern of "quality gates"
        """,
    )

    # ====================================================================
    # TASK 5: Promote to Staging (If Validation Passed)
    # ====================================================================
    def promote_model_to_staging(**context):
        """
        Promotes validated model to staging environment.
        """
        sys.path.insert(0, PROJECT_ROOT)
        from src.utils import load_config
        from src.models.registry import ModelRegistry

        config = load_config()
        registry = ModelRegistry(config)

        # Get latest model
        latest_model = registry.get_latest_model()

        if not latest_model:
            raise ValueError("No model found to promote!")

        version_id = latest_model['version_id']

        print(f"Promoting model {version_id} to staging...")

        # Transition to staging
        success = registry.transition_model_stage(
            version_id=version_id,
            new_stage='staging',
            comment='Auto-promoted by Airflow after passing validation gates'
        )

        if success:
            print(f"✅ Model {version_id} promoted to STAGING")

            # Share version ID with downstream tasks
            ti = context['task_instance']
            ti.xcom_push(key='promoted_version', value=version_id)

            return version_id
        else:
            raise ValueError("Model promotion failed")


    task_promote_staging = PythonOperator(
        task_id='promote_to_staging',
        python_callable=promote_model_to_staging,
        provide_context=True,

        doc_md="""
        ### Model Promotion Task

        Promotes validated model from development to staging.

        **Actions:**
        - Updates model stage in registry
        - Records promotion timestamp
        - Prepares for production deployment

        **Runs only if:** Model validation passed
        """,
    )

    # ====================================================================
    # TASK 6: Send Success Notification
    # ====================================================================
    def send_success_notification(**context):
        """
        Sends success notification with model details.
        """
        ti = context['task_instance']

        # Get data from previous tasks
        r2_score = ti.xcom_pull(task_ids='validate_model', key='r2_score')
        rmse = ti.xcom_pull(task_ids='validate_model', key='rmse')
        version_id = ti.xcom_pull(task_ids='promote_to_staging', key='promoted_version')

        message = f"""
        ═══════════════════════════════════════════════════════════
        ✅ ML PIPELINE COMPLETED SUCCESSFULLY
        ═══════════════════════════════════════════════════════════

        Model Version: {version_id}
        Promoted to: STAGING

        Performance Metrics:
          • R² Score: {r2_score:.4f} ({r2_score*100:.2f}%)
          • RMSE: ${rmse:,.2f}

        Next Steps:
          1. Test model in staging environment
          2. Review model in MLflow UI
          3. If satisfied, promote to production
          4. Deploy to serving infrastructure

        ═══════════════════════════════════════════════════════════
        """

        print(message)

        # In production, send to Slack/Email/PagerDuty:
        # requests.post('slack_webhook_url', json={'text': message})

        return message


    task_notify_success = PythonOperator(
        task_id='send_success_notification',
        python_callable=send_success_notification,
        provide_context=True,

        doc_md="""
        ### Success Notification Task

        Sends notification that pipeline completed successfully.

        **In Production:**
        - Send to Slack channel
        - Email team
        - Update dashboard
        """,
    )

    # ====================================================================
    # TASK 7: Send Failure Alert (If Validation Failed)
    # ====================================================================
    def send_failure_alert(**context):
        """
        Sends alert that model failed validation.
        """
        ti = context['task_instance']
        r2_score = ti.xcom_pull(task_ids='validate_model', key='r2_score')
        rmse = ti.xcom_pull(task_ids='validate_model', key='rmse')

        message = f"""
        ═══════════════════════════════════════════════════════════
        ❌ MODEL VALIDATION FAILED
        ═══════════════════════════════════════════════════════════

        Model did NOT meet quality thresholds!

        Performance:
          • R² Score: {r2_score:.4f} (Required: >= {MIN_R2_SCORE})
          • RMSE: ${rmse:,.2f} (Required: <= ${MAX_RMSE:,.0f})

        Action Required:
          1. Investigate why model performance dropped
          2. Check data quality
          3. Review feature engineering
          4. Consider algorithm changes
          5. Manual intervention needed

        Pipeline stopped to prevent deploying poor model.
        ═══════════════════════════════════════════════════════════
        """

        print(message)

        # In production: Send urgent alert!
        # pagerduty.alert(severity='high', message=message)

        raise ValueError("Model validation failed - see logs")


    task_send_failure_alert = PythonOperator(
        task_id='send_failure_alert',
        python_callable=send_failure_alert,
        provide_context=True,

        doc_md="""
        ### Failure Alert Task

        Sends urgent alert that model quality is unacceptable.

        **Triggered when:** Model fails quality gates
        **Action:** Immediate team notification
        """,
    )

    # ====================================================================
    # DEFINE WORKFLOW (Task Dependencies)
    # ====================================================================

    # Main pipeline flow
    task_ingest_data >> task_feature_engineering >> task_train_model >> task_validate_model

    # Conditional branching after validation
    task_validate_model >> task_promote_staging >> task_notify_success  # Success path
    task_validate_model >> task_send_failure_alert                       # Failure path


# ========================================================================
# HOW THIS WORKS IN PRODUCTION
# ========================================================================
"""
SCENARIO: Production Deployment

Setup (One time):
  $ export AIRFLOW_HOME=~/airflow
  $ airflow db init
  $ airflow users create --username admin --password admin --role Admin
  $ airflow scheduler &     # Start scheduler (background)
  $ airflow webserver &     # Start UI (background)
  $ cp housing_ml_pipeline.py $AIRFLOW_HOME/dags/
  $ Open: http://localhost:8080
  $ Enable DAG in UI

Day 1 (Automatic):
  00:00 - Airflow wakes up
  00:01 - Runs housing_ml_pipeline
  00:45 - All tasks succeed
  01:00 - Model in staging, team notified

Day 2 (Automatic):
  00:00 - Airflow wakes up
  00:01 - Runs housing_ml_pipeline
  00:45 - Model fails validation (R²=0.72)
  00:46 - Alert sent: "Model quality too low!"
  00:47 - Pipeline stopped (no bad model deployed!)

You (Next morning):
  08:00 - Check email: "Pipeline failed"
  08:15 - Check Airflow UI: See validation failed
  08:30 - Check MLflow UI: Model metrics dropped
  09:00 - Investigate data quality
  10:00 - Fix issue, trigger manual rerun
  10:45 - Success! Model back to R²=0.82

Day 3 (Automatic):
  00:00 - Runs again with fixed code
  00:45 - Success! R²=0.82
  01:00 - Model promoted, all good!
"""

# ========================================================================
# ADVANCED FEATURES (Examples for learning)
# ========================================================================
"""
# Parallel Tasks (Fan-out)
task_a >> [task_b, task_c, task_d] >> task_e

# TaskGroup (Organize related tasks)
from airflow.utils.task_group import TaskGroup

with TaskGroup('data_processing', dag=dag) as group:
    clean >> validate >> transform

# Dynamic Tasks (Generate tasks programmatically)
for i in range(5):
    task = BashOperator(
        task_id=f'train_model_{i}',
        bash_command=f'python train.py --fold {i}',
        dag=dag
    )

# Sensors (Wait for conditions)
from airflow.sensors.filesystem import FileSensor

wait_for_file = FileSensor(
    task_id='wait_for_data',
    filepath='/data/new_data.csv',
    poke_interval=60,  # Check every 60 seconds
    timeout=3600,      # Give up after 1 hour
    dag=dag
)

# External Task Dependencies (Wait for another DAG)
from airflow.sensors.external_task import ExternalTaskSensor

wait_for_other_dag = ExternalTaskSensor(
    task_id='wait_for_etl',
    external_dag_id='daily_etl_pipeline',
    external_task_id='final_task',
    dag=dag
)
"""
