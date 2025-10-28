"""
Model Registry Module

MLOps Importance:
A Model Registry is the central hub for managing ML models in production.
It provides:
- Single source of truth for all models
- Model versioning and lineage tracking
- Metadata and performance tracking
- Stage transitions (dev -> staging -> production)
- Rollback capabilities

This is a simplified version. Production systems use tools like:
- MLflow Model Registry
- AWS SageMaker Model Registry
- Azure ML Model Registry
- Custom solutions built on top of databases
"""

import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import shutil


class ModelRegistry:
    """
    Manages model versioning, metadata, and lifecycle.

    MLOps Principle: Model Governance
    Track everything about your models:
    - Who trained it
    - When it was trained
    - What data was used
    - What parameters were used
    - How it performed
    - Where it's deployed
    - Its current stage (staging/production)
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize ModelRegistry with configuration.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.registry_config = config['model_registry']
        self.registry_path = self.registry_config['registry_path']
        self.save_path = self.registry_config['save_path']
        self.logger = logging.getLogger(__name__)

        # Initialize registry
        self._initialize_registry()

    def _initialize_registry(self) -> None:
        """
        Initialize or load existing registry.
        """
        Path(self.registry_path).parent.mkdir(parents=True, exist_ok=True)

        if Path(self.registry_path).exists():
            with open(self.registry_path, 'r') as f:
                self.registry = json.load(f)
            self.logger.info(f"Loaded existing registry with {len(self.registry['models'])} models")
        else:
            self.registry = {
                'models': [],
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
            self._save_registry()
            self.logger.info("Initialized new model registry")

    def _save_registry(self) -> None:
        """
        Save registry to disk.
        """
        self.registry['last_updated'] = datetime.now().isoformat()

        with open(self.registry_path, 'w') as f:
            json.dump(self.registry, f, indent=4)

        self.logger.info(f"Registry saved to {self.registry_path}")

    def register_model(
        self,
        model_path: str,
        model_metadata: Dict[str, Any],
        evaluation_report: Dict[str, Any],
        stage: str = "development"
    ) -> str:
        """
        Register a new model in the registry.

        MLOps Critical:
        Every model that goes to production should be registered.
        This creates an audit trail and enables governance.

        Args:
            model_path: Path to the saved model file
            model_metadata: Metadata about the model (training info, hyperparameters, etc.)
            evaluation_report: Model evaluation results
            stage: Model stage (development, staging, production, archived)

        Returns:
            Model version ID
        """
        self.logger.info("Registering new model...")

        # Generate version ID
        version_strategy = self.registry_config['versioning_strategy']
        version_id = self._generate_version_id(version_strategy)

        # Create model entry
        model_entry = {
            'version_id': version_id,
            'model_path': model_path,
            'registered_at': datetime.now().isoformat(),
            'stage': stage,
            'metadata': model_metadata,
            'evaluation': evaluation_report,
            'tags': [],
            'deployments': [],
            'stage_history': [
                {
                    'stage': stage,
                    'timestamp': datetime.now().isoformat()
                }
            ]
        }

        # Add to registry
        self.registry['models'].append(model_entry)

        # Save registry
        self._save_registry()

        self.logger.info(f"Model registered with version ID: {version_id}")
        self.logger.info(f"Stage: {stage}")
        self.logger.info(f"Metrics: {evaluation_report.get('metrics', {})}")

        return version_id

    def _generate_version_id(self, strategy: str) -> str:
        """
        Generate version ID based on strategy.

        Args:
            strategy: Versioning strategy

        Returns:
            Version ID string
        """
        if strategy == "timestamp":
            return f"v_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        elif strategy == "semantic":
            # Get latest semantic version and increment
            existing_versions = [
                m['version_id'] for m in self.registry['models']
                if m['version_id'].startswith('v')
            ]

            if not existing_versions:
                return "v1.0.0"

            # Simple increment (in production, use proper semantic versioning)
            return f"v{len(existing_versions) + 1}.0.0"

        elif strategy == "auto_increment":
            return f"v{len(self.registry['models']) + 1}"

        else:
            return f"v_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def get_model(self, version_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve model entry by version ID.

        Args:
            version_id: Model version ID

        Returns:
            Model entry dictionary or None if not found
        """
        for model in self.registry['models']:
            if model['version_id'] == version_id:
                return model

        self.logger.warning(f"Model version {version_id} not found in registry")
        return None

    def get_latest_model(self, stage: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get the latest model, optionally filtered by stage.

        MLOps Use:
        In production, you typically want to get:
        - Latest production model for inference
        - Latest staging model for validation
        - Latest development model for comparison

        Args:
            stage: Filter by model stage (optional)

        Returns:
            Latest model entry or None
        """
        models = self.registry['models']

        if stage:
            models = [m for m in models if m['stage'] == stage]

        if not models:
            self.logger.warning(f"No models found{' in stage ' + stage if stage else ''}")
            return None

        # Get latest by registered_at timestamp
        latest_model = max(models, key=lambda m: m['registered_at'])

        self.logger.info(f"Retrieved latest model: {latest_model['version_id']} (stage: {latest_model['stage']})")

        return latest_model

    def transition_model_stage(
        self,
        version_id: str,
        new_stage: str,
        comment: str = ""
    ) -> bool:
        """
        Transition a model to a new stage.

        MLOps Workflow:
        Typical model lifecycle:
        1. development - Model is being developed/experimented with
        2. staging - Model passed validation, ready for testing
        3. production - Model is actively serving predictions
        4. archived - Model is retired but kept for reference

        Args:
            version_id: Model version ID
            new_stage: New stage to transition to
            comment: Optional comment about the transition

        Returns:
            True if successful, False otherwise
        """
        model = self.get_model(version_id)

        if not model:
            return False

        old_stage = model['stage']
        model['stage'] = new_stage

        # Add to stage history
        model['stage_history'].append({
            'stage': new_stage,
            'timestamp': datetime.now().isoformat(),
            'comment': comment,
            'previous_stage': old_stage
        })

        self._save_registry()

        self.logger.info(f"Model {version_id} transitioned: {old_stage} -> {new_stage}")

        return True

    def add_model_tag(self, version_id: str, tag: str) -> bool:
        """
        Add a tag to a model.

        MLOps Use:
        Tags help organize and search models:
        - "baseline", "champion", "challenger"
        - "high-accuracy", "low-latency"
        - "production-candidate"

        Args:
            version_id: Model version ID
            tag: Tag to add

        Returns:
            True if successful, False otherwise
        """
        model = self.get_model(version_id)

        if not model:
            return False

        if 'tags' not in model:
            model['tags'] = []

        if tag not in model['tags']:
            model['tags'].append(tag)
            self._save_registry()
            self.logger.info(f"Added tag '{tag}' to model {version_id}")

        return True

    def record_deployment(
        self,
        version_id: str,
        deployment_info: Dict[str, Any]
    ) -> bool:
        """
        Record a model deployment.

        MLOps Tracking:
        Track where and when models are deployed:
        - Deployment timestamp
        - Environment (dev, staging, prod)
        - Endpoint URL
        - Deployment config

        Args:
            version_id: Model version ID
            deployment_info: Deployment information

        Returns:
            True if successful, False otherwise
        """
        model = self.get_model(version_id)

        if not model:
            return False

        if 'deployments' not in model:
            model['deployments'] = []

        deployment_entry = {
            'timestamp': datetime.now().isoformat(),
            **deployment_info
        }

        model['deployments'].append(deployment_entry)
        self._save_registry()

        self.logger.info(f"Recorded deployment for model {version_id}")

        return True

    def compare_models(
        self,
        version_ids: List[str],
        metric: str = 'rmse'
    ) -> Dict[str, Any]:
        """
        Compare multiple models on a specific metric.

        Args:
            version_ids: List of model version IDs to compare
            metric: Metric to compare on

        Returns:
            Comparison results dictionary
        """
        comparison = {}

        for version_id in version_ids:
            model = self.get_model(version_id)

            if model and 'evaluation' in model:
                metrics = model['evaluation'].get('metrics', {})
                comparison[version_id] = {
                    'metric_value': metrics.get(metric, None),
                    'stage': model['stage'],
                    'registered_at': model['registered_at']
                }

        self.logger.info(f"Compared {len(comparison)} models on metric: {metric}")

        return comparison

    def list_models(
        self,
        stage: Optional[str] = None,
        tag: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List models with optional filtering.

        Args:
            stage: Filter by stage (optional)
            tag: Filter by tag (optional)

        Returns:
            List of model entries
        """
        models = self.registry['models']

        if stage:
            models = [m for m in models if m['stage'] == stage]

        if tag:
            models = [m for m in models if tag in m.get('tags', [])]

        return models

    def get_registry_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of the registry.

        Returns:
            Summary dictionary
        """
        models = self.registry['models']

        summary = {
            'total_models': len(models),
            'models_by_stage': {},
            'latest_registration': None
        }

        # Count by stage
        for model in models:
            stage = model['stage']
            summary['models_by_stage'][stage] = summary['models_by_stage'].get(stage, 0) + 1

        # Get latest registration
        if models:
            latest = max(models, key=lambda m: m['registered_at'])
            summary['latest_registration'] = {
                'version_id': latest['version_id'],
                'registered_at': latest['registered_at'],
                'stage': latest['stage']
            }

        return summary
