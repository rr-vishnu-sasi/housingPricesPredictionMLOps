"""
Pipeline Stage 3: Model Training

This script trains and evaluates the ML model.

MLOps Key Concepts:
- Reproducible training (same data + config = same model)
- Metric tracking (know if model is improving)
- Model versioning (track different experiments)
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


def run_model_training():
    """
    Run model training stage.

    What it does:
    1. Loads featured data from stage 2
    2. Splits into train/validation sets
    3. Trains model
    4. Evaluates performance
    5. Registers model if it passes quality checks

    Returns:
        bool: True if successful, False otherwise
    """
    # Initialize logger
    logger = PipelineLogger(name="stage_03_train")
    logger.stage_start("Model Training")

    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = load_config()

        # Load featured data from stage 2
        logger.info("Loading featured data...")
        features_path = config['data']['features_data_path']
        df_features = pd.read_csv(features_path)
        logger.data_info("Rows loaded", len(df_features))

        # Initialize trainer
        logger.info("Initializing Model Trainer...")
        trainer = ModelTrainer(config)

        # Split data
        logger.info("Splitting data into train/validation sets...")
        X_train, X_val, y_train, y_val = trainer.split_data(df_features)
        logger.data_info("Training samples", len(X_train))
        logger.data_info("Validation samples", len(X_val))

        # Train model
        logger.info(f"Training {config['model']['type']} model...")
        trainer.train(X_train, y_train)
        logger.info("Model training completed")

        # Get feature importance
        feature_importance = trainer.get_feature_importance(X_train)
        if feature_importance:
            top_feature = list(feature_importance.items())[0]
            logger.info(f"Top feature: {top_feature[0]} ({top_feature[1]:.4f})")

        # Evaluate model
        logger.info("Evaluating model...")
        evaluator = ModelEvaluator(config)
        y_pred_val = trainer.predict(X_val)
        evaluation_report = evaluator.evaluate(y_val, y_pred_val, feature_importance)

        # Log metrics
        logger.metric("RMSE", evaluation_report['metrics']['rmse'])
        logger.metric("MAE", evaluation_report['metrics']['mae'])
        logger.metric("R2_Score", evaluation_report['metrics']['r2_score'])
        logger.metric("MAPE", evaluation_report['metrics']['mape'])

        # Check if passed thresholds
        if evaluation_report['all_checks_passed']:
            logger.info("✓ Model passed all quality thresholds")
        else:
            logger.warning("✗ Model failed some quality thresholds")

        # Save model
        logger.info("Saving model...")
        model_path = trainer.save_model()
        logger.info(f"Model saved to: {model_path}")

        # Save evaluation report
        evaluator.save_evaluation_report(evaluation_report)

        # Register model
        logger.info("Registering model...")
        registry = ModelRegistry(config)
        stage = "staging" if evaluation_report['all_checks_passed'] else "development"

        model_metadata = {
            'model_type': config['model']['type'],
            'hyperparameters': config['model']['hyperparameters'][config['model']['type']],
            'training_samples': len(X_train),
            'validation_samples': len(X_val),
            'feature_count': X_train.shape[1],
            'training_duration_seconds': trainer.training_history.get('training_duration_seconds', 0)
        }

        version_id = registry.register_model(
            model_path=model_path,
            model_metadata=model_metadata,
            evaluation_report=evaluation_report,
            stage=stage
        )

        logger.info(f"Model registered: {version_id} (stage: {stage})")

        logger.stage_end("Model Training", success=True)
        return True

    except Exception as e:
        logger.error(f"Model training failed: {str(e)}")
        logger.stage_end("Model Training", success=False)
        return False


if __name__ == "__main__":
    success = run_model_training()
    sys.exit(0 if success else 1)
