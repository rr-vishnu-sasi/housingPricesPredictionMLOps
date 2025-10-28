"""
Model Training Module

MLOps Importance:
Model training is where your ML code meets MLOps practices:
- Experiment tracking (compare different models/hyperparameters)
- Reproducibility (same code + data + config = same model)
- Model versioning (track model lineage)
- Automated retraining (when data drift is detected)
"""

import pandas as pd
import numpy as np
import logging
import joblib
from typing import Dict, Any, Tuple
from pathlib import Path
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


class ModelTrainer:
    """
    Handles model training with experiment tracking capabilities.

    MLOps Principle: Experiment Tracking
    Track every experiment with:
    - Parameters used
    - Metrics achieved
    - Model artifacts
    - Training time
    - Data version
    This enables reproducibility and helps identify the best models.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize ModelTrainer with configuration.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.model_config = config['model']
        self.training_config = config['training']
        self.data_config = config['data']
        self.logger = logging.getLogger(__name__)

        self.model = None
        self.training_history = {}

    def get_model(self) -> Any:
        """
        Initialize model based on configuration.

        MLOps Note:
        Configuration-driven model selection allows:
        - Easy A/B testing of different algorithms
        - Hyperparameter tuning without code changes
        - Reproducible model training

        Returns:
            Initialized model object
        """
        model_type = self.model_config['type']
        hyperparameters = self.model_config['hyperparameters']

        self.logger.info(f"Initializing {model_type} model...")

        if model_type == 'linear_regression':
            model = LinearRegression(**hyperparameters['linear_regression'])

        elif model_type == 'random_forest':
            model = RandomForestRegressor(**hyperparameters['random_forest'])

        elif model_type == 'gradient_boosting':
            model = GradientBoostingRegressor(**hyperparameters['gradient_boosting'])

        else:
            raise ValueError(f"Unknown model type: {model_type}")

        self.logger.info(f"Model initialized: {model_type}")
        return model

    def split_data(
        self,
        df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """
        Split data into training and validation sets.

        MLOps Principle: Data Splits
        Consistent data splitting strategy is crucial for:
        - Fair model comparison
        - Preventing data leakage
        - Reproducible experiments

        Args:
            df: Input DataFrame with features and target

        Returns:
            Tuple of (X_train, X_val, y_train, y_val)
        """
        self.logger.info("Splitting data into train and validation sets...")

        # Separate features and target
        target_column = 'median_house_value'

        if target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found in DataFrame")

        X = df.drop(target_column, axis=1)
        y = df[target_column]

        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y,
            test_size=self.data_config['validation_split'],
            random_state=self.data_config['random_state']
        )

        self.logger.info(f"Data split completed:")
        self.logger.info(f"  Training samples: {len(X_train)}")
        self.logger.info(f"  Validation samples: {len(X_val)}")
        self.logger.info(f"  Number of features: {X_train.shape[1]}")

        return X_train, X_val, y_train, y_val

    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series
    ) -> None:
        """
        Train the model.

        MLOps Note:
        Training time and resource usage should be monitored in production:
        - Long training times may indicate need for optimization
        - Memory issues need to be caught early
        - Training can be distributed for large datasets

        Args:
            X_train: Training features
            y_train: Training target
        """
        self.logger.info("Starting model training...")

        # Record training start time
        start_time = datetime.now()

        # Initialize model
        self.model = self.get_model()

        # Train model
        self.model.fit(X_train, y_train)

        # Record training end time
        end_time = datetime.now()
        training_duration = (end_time - start_time).total_seconds()

        self.logger.info(f"Model training completed in {training_duration:.2f} seconds")

        # Store training metadata
        self.training_history['training_duration_seconds'] = training_duration
        self.training_history['training_samples'] = len(X_train)
        self.training_history['feature_count'] = X_train.shape[1]
        self.training_history['model_type'] = self.model_config['type']
        self.training_history['hyperparameters'] = self.model_config['hyperparameters'][self.model_config['type']]
        self.training_history['training_timestamp'] = start_time.isoformat()

    def get_feature_importance(self, X_train: pd.DataFrame) -> Dict[str, float]:
        """
        Get feature importance from the trained model.

        MLOps Insight:
        Feature importance helps with:
        - Model interpretability (explain predictions to stakeholders)
        - Feature selection (remove unimportant features)
        - Debugging (identify unexpected patterns)
        - Compliance (some industries require explainable models)

        Args:
            X_train: Training features (for column names)

        Returns:
            Dictionary mapping feature names to importance scores
        """
        if self.model is None:
            raise ValueError("Model not trained yet")

        # Check if model has feature_importances_ attribute
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            feature_importance = dict(zip(X_train.columns, importances))

            # Sort by importance
            feature_importance = dict(
                sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            )

            self.logger.info("Feature importance calculated")

            # Log top 5 features
            top_features = list(feature_importance.items())[:5]
            self.logger.info("Top 5 most important features:")
            for feature, importance in top_features:
                self.logger.info(f"  {feature}: {importance:.4f}")

            return feature_importance

        else:
            self.logger.info("Model does not support feature importance")
            return {}

    def save_model(self, output_dir: str = "models/saved_models") -> str:
        """
        Save the trained model.

        MLOps Critical:
        Model persistence is essential for:
        - Deploying models to production
        - Rolling back to previous versions if needed
        - A/B testing different model versions
        - Auditing and compliance

        Args:
            output_dir: Directory to save the model

        Returns:
            Path where model was saved
        """
        if self.model is None:
            raise ValueError("No model to save. Train a model first.")

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Generate model filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_filename = f"model_{self.model_config['type']}_{timestamp}.joblib"
        model_path = Path(output_dir) / model_filename

        # Save model
        joblib.dump(self.model, model_path)
        self.logger.info(f"Model saved to {model_path}")

        # Save training history
        history_filename = f"training_history_{timestamp}.joblib"
        history_path = Path(output_dir) / history_filename
        joblib.dump(self.training_history, history_path)
        self.logger.info(f"Training history saved to {history_path}")

        return str(model_path)

    def load_model(self, model_path: str) -> None:
        """
        Load a trained model.

        Args:
            model_path: Path to the saved model
        """
        self.model = joblib.load(model_path)
        self.logger.info(f"Model loaded from {model_path}")

        # Try to load training history if available
        history_path = model_path.replace('model_', 'training_history_')
        if Path(history_path).exists():
            self.training_history = joblib.load(history_path)
            self.logger.info(f"Training history loaded from {history_path}")

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Make predictions using the trained model.

        Args:
            X: Features to predict on

        Returns:
            Array of predictions
        """
        if self.model is None:
            raise ValueError("Model not trained or loaded. Cannot make predictions.")

        predictions = self.model.predict(X)
        return predictions
