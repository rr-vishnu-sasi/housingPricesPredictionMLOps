"""
Pipeline Stage 3: Model Training with MLflow Tracking

This version includes MLflow for experiment tracking.

MLflow Benefits:
- Track ALL experiments in one place
- Compare models visually
- Easy model versioning
- One-click model serving
"""

import sys
import pandas as pd
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import load_config
from src.models.train import ModelTrainer
from src.evaluation.evaluate import ModelEvaluator
from src.models.registry import ModelRegistry
from src.pipeline_logger import PipelineLogger
from src.mlflow_tracker import MLflowTracker


def run_model_training_with_mlflow():
    """
    Run model training with MLflow tracking.

    What's different from regular training:
    - Logs parameters to MLflow
    - Logs metrics to MLflow
    - Registers model in MLflow Model Registry
    - Allows comparison in MLflow UI
    """
    logger = PipelineLogger(name="stage_03_train_mlflow")
    logger.stage_start("Model Training (with MLflow)")

    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = load_config()

        # Check if MLflow is enabled
        if not config['training'].get('enable_mlflow', False):
            logger.warning("MLflow not enabled in config. Set enable_mlflow: true")
            logger.info("Running without MLflow tracking...")
            # Fall back to regular training
            from pipeline.stage_03_train_model import run_model_training
            return run_model_training()

        # Initialize MLflow tracker
        logger.info("Initializing MLflow tracker...")
        mlflow_tracker = MLflowTracker(config)

        # Start MLflow run
        run_name = f"{config['model']['type']}_{config['model']['hyperparameters'][config['model']['type']]['n_estimators']}_trees"
        mlflow_tracker.start_run(run_name=run_name)
        logger.info(f"MLflow run started: {run_name}")

        # Load featured data
        logger.info("Loading featured data...")
        features_path = config['data']['features_data_path']
        df_features = pd.read_csv(features_path)
        logger.data_info("Rows loaded", len(df_features))

        # Initialize trainer
        logger.info("Initializing Model Trainer...")
        trainer = ModelTrainer(config)

        # Split data
        logger.info("Splitting data...")
        X_train, X_val, y_train, y_val = trainer.split_data(df_features)
        logger.data_info("Training samples", len(X_train))
        logger.data_info("Validation samples", len(X_val))

        # Log dataset info to MLflow
        mlflow_tracker.log_params({
            'train_samples': len(X_train),
            'val_samples': len(X_val),
            'total_features': X_train.shape[1]
        })

        # Log hyperparameters to MLflow
        logger.info("Logging hyperparameters to MLflow...")
        model_type = config['model']['type']
        hyperparameters = config['model']['hyperparameters'][model_type]

        mlflow_tracker.log_params({
            'model_type': model_type,
            **hyperparameters
        })

        # Train model
        logger.info(f"Training {model_type} model...")
        trainer.train(X_train, y_train)
        logger.info("Model training completed")

        # Get feature importance
        feature_importance = trainer.get_feature_importance(X_train)
        if feature_importance:
            top_feature = list(feature_importance.items())[0]
            logger.info(f"Top feature: {top_feature[0]} ({top_feature[1]:.4f})")

            # Log top 5 features to MLflow
            top_5_features = dict(list(feature_importance.items())[:5])
            mlflow_tracker.log_params({
                f'top_feature_{i+1}': f"{feat} ({imp:.4f})"
                for i, (feat, imp) in enumerate(top_5_features.items())
            })

        # Evaluate model
        logger.info("Evaluating model...")
        evaluator = ModelEvaluator(config)
        y_pred_val = trainer.predict(X_val)
        evaluation_report = evaluator.evaluate(y_val, y_pred_val, feature_importance)

        # Log metrics to MLflow
        logger.info("Logging metrics to MLflow...")
        mlflow_tracker.log_metrics(evaluation_report['metrics'])

        # Log evaluation report
        mlflow_tracker.log_dict(evaluation_report, 'evaluation_report.json')

        # Log model to MLflow
        logger.info("Logging model to MLflow Model Registry...")
        model_name = config['serving']['model_name']
        mlflow_tracker.log_model(
            model=trainer.model,
            artifact_path="model",
            registered_model_name=model_name  # Registers in MLflow Model Registry
        )

        # Set tags
        mlflow_tracker.set_tags({
            'stage': 'staging' if evaluation_report['all_checks_passed'] else 'development',
            'passed_thresholds': str(evaluation_report['all_checks_passed']),
            'model_type': model_type
        })

        # Log metrics
        logger.metric("RMSE", evaluation_report['metrics']['rmse'])
        logger.metric("MAE", evaluation_report['metrics']['mae'])
        logger.metric("R2_Score", evaluation_report['metrics']['r2_score'])
        logger.metric("MAPE", evaluation_report['metrics']['mape'])

        # Save model locally (for backward compatibility)
        logger.info("Saving model locally...")
        model_path = trainer.save_model()

        # Save evaluation report
        evaluator.save_evaluation_report(evaluation_report)

        # Register in local registry too
        logger.info("Registering in local model registry...")
        registry = ModelRegistry(config)
        stage = "staging" if evaluation_report['all_checks_passed'] else "development"

        model_metadata = {
            'model_type': model_type,
            'hyperparameters': hyperparameters,
            'training_samples': len(X_train),
            'validation_samples': len(X_val),
            'feature_count': X_train.shape[1],
            'training_duration_seconds': trainer.training_history.get('training_duration_seconds', 0),
            'mlflow_run_id': mlflow_tracker.get_run_id()
        }

        version_id = registry.register_model(
            model_path=model_path,
            model_metadata=model_metadata,
            evaluation_report=evaluation_report,
            stage=stage
        )

        logger.info(f"Model registered: {version_id} (stage: {stage})")

        # End MLflow run
        mlflow_tracker.end_run()

        logger.info("\n📊 MLflow Summary:")
        logger.info(f"  • Experiment: {config['training']['experiment_name']}")
        logger.info(f"  • Run: {run_name}")
        logger.info(f"  • Metrics logged: RMSE, MAE, R², MAPE")
        logger.info(f"  • Model registered: {model_name}")
        logger.info(f"\n🌐 View in MLflow UI:")
        logger.info(f"  Run: mlflow ui")
        logger.info(f"  Then open: http://localhost:5000")

        logger.stage_end("Model Training (with MLflow)", success=True)
        return True

    except Exception as e:
        logger.error(f"Model training failed: {str(e)}")
        # End MLflow run on error
        try:
            mlflow.end_run()
        except:
            pass
        logger.stage_end("Model Training (with MLflow)", success=False)
        return False


if __name__ == "__main__":
    success = run_model_training_with_mlflow()
    sys.exit(0 if success else 1)
