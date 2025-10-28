"""
Main ML Pipeline

This script orchestrates the entire ML workflow:
1. Data Ingestion
2. Feature Engineering
3. Model Training
4. Model Evaluation
5. Model Registration

MLOps Principle: Pipeline Orchestration
In production, this would be:
- Scheduled (e.g., daily/weekly retraining)
- Triggered by events (e.g., new data arrival, performance drop)
- Orchestrated by tools like Airflow, Kubeflow, or AWS Step Functions
- Containerized (Docker) for reproducibility
- Version controlled (Git) for traceability
"""

import logging
from pathlib import Path

# Import project modules
from src.utils import load_config, setup_logging, save_json
from src.data.ingest import DataIngestor
from src.features.engineer import FeatureEngineer
from src.models.train import ModelTrainer
from src.evaluation.evaluate import ModelEvaluator
from src.models.registry import ModelRegistry


def main():
    """
    Main training pipeline.

    MLOps Pattern: Modular Pipeline
    Each step is independent and can be:
    - Run separately for debugging
    - Tested independently
    - Replaced with improved versions
    - Cached to avoid recomputation
    """

    # ========== Setup ==========
    print("=" * 60)
    print("HOUSING PRICE PREDICTION - MLOPS PIPELINE")
    print("=" * 60)

    # Load configuration
    config = load_config()

    # Setup logging
    setup_logging(config)
    logger = logging.getLogger(__name__)

    logger.info("Starting ML pipeline...")

    try:
        # ========== Step 1: Data Ingestion ==========
        logger.info("\n" + "=" * 60)
        logger.info("STEP 1: DATA INGESTION")
        logger.info("=" * 60)

        data_ingestor = DataIngestor(config)
        df_processed, quality_report = data_ingestor.ingest()

        logger.info(f"Data ingestion completed. Processed {len(df_processed)} samples")

        # Save quality report
        save_json(quality_report, "logs/data_quality_report.json")

        # ========== Step 2: Feature Engineering ==========
        logger.info("\n" + "=" * 60)
        logger.info("STEP 2: FEATURE ENGINEERING")
        logger.info("=" * 60)

        feature_engineer = FeatureEngineer(config)
        df_features = feature_engineer.engineer_features(df_processed, is_training=True)

        # Save feature engineering artifacts
        feature_engineer.save_artifacts()

        # Save featured data
        df_features.to_csv(config['data']['features_data_path'], index=False)

        logger.info(f"Feature engineering completed. Feature count: {len(df_features.columns) - 1}")

        # ========== Step 3: Model Training ==========
        logger.info("\n" + "=" * 60)
        logger.info("STEP 3: MODEL TRAINING")
        logger.info("=" * 60)

        model_trainer = ModelTrainer(config)

        # Split data
        X_train, X_val, y_train, y_val = model_trainer.split_data(df_features)

        # Train model
        model_trainer.train(X_train, y_train)

        # Get feature importance
        feature_importance = model_trainer.get_feature_importance(X_train)

        logger.info("Model training completed")

        # ========== Step 4: Model Evaluation ==========
        logger.info("\n" + "=" * 60)
        logger.info("STEP 4: MODEL EVALUATION")
        logger.info("=" * 60)

        model_evaluator = ModelEvaluator(config)

        # Make predictions on validation set
        y_pred_val = model_trainer.predict(X_val)

        # Evaluate
        evaluation_report = model_evaluator.evaluate(
            y_val,
            y_pred_val,
            feature_importance
        )

        # Save evaluation report
        model_evaluator.save_evaluation_report(evaluation_report)

        # Print summary
        logger.info("\nEvaluation Summary:")
        for metric, value in evaluation_report['metrics'].items():
            logger.info(f"  {metric.upper()}: {value:,.4f}")

        # Check if model passed thresholds
        if evaluation_report['all_checks_passed']:
            logger.info("\n✓ Model passed all performance thresholds!")
        else:
            logger.warning("\n✗ Model failed some performance thresholds")
            for check, passed in evaluation_report['threshold_checks'].items():
                status = "✓" if passed else "✗"
                logger.info(f"  {status} {check}: {'PASSED' if passed else 'FAILED'}")

        # ========== Step 5: Model Saving ==========
        logger.info("\n" + "=" * 60)
        logger.info("STEP 5: MODEL SAVING")
        logger.info("=" * 60)

        # Save model
        model_path = model_trainer.save_model()

        logger.info(f"Model saved to: {model_path}")

        # ========== Step 6: Model Registration ==========
        logger.info("\n" + "=" * 60)
        logger.info("STEP 6: MODEL REGISTRATION")
        logger.info("=" * 60)

        model_registry = ModelRegistry(config)

        # Prepare model metadata
        model_metadata = {
            'model_type': config['model']['type'],
            'hyperparameters': config['model']['hyperparameters'][config['model']['type']],
            'training_samples': len(X_train),
            'validation_samples': len(X_val),
            'feature_count': X_train.shape[1],
            'training_duration_seconds': model_trainer.training_history.get('training_duration_seconds', 0),
            'data_quality_report': quality_report
        }

        # Determine stage based on performance
        if evaluation_report['all_checks_passed']:
            stage = "staging"  # Ready for further testing
            logger.info("Model meets quality thresholds - registering in STAGING")
        else:
            stage = "development"
            logger.info("Model does not meet quality thresholds - registering in DEVELOPMENT")

        # Register model
        version_id = model_registry.register_model(
            model_path=model_path,
            model_metadata=model_metadata,
            evaluation_report=evaluation_report,
            stage=stage
        )

        logger.info(f"Model registered with version ID: {version_id}")

        # Get registry summary
        registry_summary = model_registry.get_registry_summary()
        logger.info(f"\nRegistry Summary:")
        logger.info(f"  Total models: {registry_summary['total_models']}")
        logger.info(f"  Models by stage: {registry_summary['models_by_stage']}")

        # ========== Pipeline Completion ==========
        logger.info("\n" + "=" * 60)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)

        logger.info("\nPipeline Summary:")
        logger.info(f"  ✓ Data samples processed: {len(df_processed)}")
        logger.info(f"  ✓ Features engineered: {len(df_features.columns) - 1}")
        logger.info(f"  ✓ Model trained: {config['model']['type']}")
        logger.info(f"  ✓ Validation RMSE: ${evaluation_report['metrics']['rmse']:,.2f}")
        logger.info(f"  ✓ Validation R²: {evaluation_report['metrics']['r2_score']:.4f}")
        logger.info(f"  ✓ Model version: {version_id}")
        logger.info(f"  ✓ Model stage: {stage}")

        logger.info("\nNext Steps:")
        logger.info("  1. Review evaluation report: logs/evaluation_report.json")
        logger.info("  2. Test model inference: python examples/inference_example.py")
        logger.info("  3. If satisfied, promote model to production")
        logger.info("  4. Deploy model to serving infrastructure")

        return {
            'success': True,
            'version_id': version_id,
            'metrics': evaluation_report['metrics']
        }

    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }


if __name__ == "__main__":
    result = main()

    if result['success']:
        print("\n✓ Pipeline completed successfully!")
    else:
        print(f"\n✗ Pipeline failed: {result['error']}")
