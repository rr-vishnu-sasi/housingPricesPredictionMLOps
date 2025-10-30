"""
MLflow Tracking Module

MLOps Importance:
MLflow is the industry-standard tool for:
- Experiment tracking (compare models)
- Model registry (version management)
- Model serving (deploy as API)

Think of MLflow as:
- Google Docs version history (for ML experiments)
- App Store (for ML models)
- API server (for serving predictions)
"""

import mlflow
import mlflow.sklearn
import logging
from typing import Dict, Any, Optional
from pathlib import Path


class MLflowTracker:
    """
    Handles MLflow experiment tracking and model registry.

    Simple Explanation:
    - Tracks every experiment you run
    - Saves parameters, metrics, and models
    - Allows comparison in visual UI
    - Manages model versions
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize MLflow tracker.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.training_config = config['training']
        self.logger = logging.getLogger(__name__)

        # Set up MLflow
        self._setup_mlflow()

    def _setup_mlflow(self):
        """
        Setup MLflow tracking.

        What this does:
        - Sets where MLflow saves experiments (tracking URI)
        - Creates/sets experiment name
        """
        # Set tracking URI (where MLflow stores data)
        tracking_uri = self.training_config.get('tracking_uri', 'file:./mlruns')
        mlflow.set_tracking_uri(tracking_uri)
        self.logger.info(f"MLflow tracking URI: {tracking_uri}")

        # Set experiment name
        experiment_name = self.training_config.get('experiment_name', 'housing_price_prediction')
        mlflow.set_experiment(experiment_name)
        self.logger.info(f"MLflow experiment: {experiment_name}")

    def start_run(self, run_name: Optional[str] = None):
        """
        Start an MLflow run (one experiment).

        Simple: Like opening a new notebook page to record an experiment

        Args:
            run_name: Name for this run (e.g., "baseline_model", "experiment_1")
        """
        if run_name is None:
            run_name = self.training_config.get('run_name', 'default_run')

        mlflow.start_run(run_name=run_name)
        self.logger.info(f"Started MLflow run: {run_name}")

    def log_params(self, params: Dict[str, Any]):
        """
        Log parameters (hyperparameters, settings).

        Simple: Record the "settings" you used

        Example:
            log_params({
                'n_estimators': 100,
                'max_depth': 20,
                'model_type': 'random_forest'
            })

        Args:
            params: Dictionary of parameters
        """
        for key, value in params.items():
            mlflow.log_param(key, value)

        self.logger.info(f"Logged {len(params)} parameters to MLflow")

    def log_metrics(self, metrics: Dict[str, float]):
        """
        Log metrics (RMSE, R², etc.).

        Simple: Record the "results" you got

        Example:
            log_metrics({
                'rmse': 48726.11,
                'r2_score': 0.82,
                'mae': 31238.86
            })

        Args:
            metrics: Dictionary of metrics
        """
        for key, value in metrics.items():
            mlflow.log_metric(key, value)

        self.logger.info(f"Logged {len(metrics)} metrics to MLflow")

    def log_model(
        self,
        model,
        artifact_path: str = "model",
        registered_model_name: Optional[str] = None
    ):
        """
        Log model to MLflow.

        Simple: Save your trained model so MLflow can:
        - Track it
        - Version it
        - Serve it as API

        Args:
            model: Trained sklearn model
            artifact_path: Where to save in MLflow
            registered_model_name: Name for model registry (enables versioning)
        """
        mlflow.sklearn.log_model(
            model,
            artifact_path=artifact_path,
            registered_model_name=registered_model_name
        )

        self.logger.info(f"Model logged to MLflow (artifact_path: {artifact_path})")

        if registered_model_name:
            self.logger.info(f"Model registered as: {registered_model_name}")

    def log_artifact(self, file_path: str):
        """
        Log a file (plot, report, etc.) to MLflow.

        Args:
            file_path: Path to file to log
        """
        mlflow.log_artifact(file_path)
        self.logger.info(f"Artifact logged: {file_path}")

    def log_dict(self, dictionary: Dict, filename: str):
        """
        Log a dictionary as JSON file.

        Example:
            log_dict({'accuracy': 0.85, 'f1': 0.82}, 'metrics.json')

        Args:
            dictionary: Dictionary to save
            filename: Filename to save as
        """
        mlflow.log_dict(dictionary, filename)
        self.logger.info(f"Dictionary logged as: {filename}")

    def set_tags(self, tags: Dict[str, str]):
        """
        Set tags for organization.

        Simple: Like adding labels to organize experiments

        Example:
            set_tags({
                'team': 'data-science',
                'project': 'housing-prediction',
                'stage': 'development'
            })

        Args:
            tags: Dictionary of tags
        """
        for key, value in tags.items():
            mlflow.set_tag(key, value)

        self.logger.info(f"Set {len(tags)} tags")

    def end_run(self):
        """
        End current MLflow run.

        Simple: Close the notebook page (finish recording experiment)
        """
        mlflow.end_run()
        self.logger.info("MLflow run ended")

    def get_run_id(self) -> Optional[str]:
        """
        Get current run ID.

        Returns:
            Run ID string or None
        """
        active_run = mlflow.active_run()
        return active_run.info.run_id if active_run else None


# Simple example usage
if __name__ == "__main__":
    # Example configuration
    config = {
        'training': {
            'tracking_uri': 'file:./mlruns',
            'experiment_name': 'test_experiment',
            'run_name': 'example_run'
        }
    }

    # Create tracker
    tracker = MLflowTracker(config)

    # Start tracking
    tracker.start_run(run_name="example_run")

    # Log parameters
    tracker.log_params({
        'n_estimators': 100,
        'max_depth': 20
    })

    # Log metrics
    tracker.log_metrics({
        'rmse': 48726.11,
        'r2_score': 0.82
    })

    # Set tags
    tracker.set_tags({
        'model_type': 'random_forest',
        'stage': 'development'
    })

    # End run
    tracker.end_run()

    print("✓ MLflow example completed!")
    print("  View in UI: mlflow ui")
