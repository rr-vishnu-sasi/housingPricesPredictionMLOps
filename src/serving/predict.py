"""
Model Serving/Inference Module

MLOps Importance:
Serving is where your ML model creates business value.
Key MLOps principles for serving:
- Low latency (predictions must be fast)
- High availability (system must be reliable)
- Versioning (serve specific model versions)
- Monitoring (track prediction quality, drift, latency)
- A/B testing (compare model versions in production)
- Batch vs real-time (different use cases need different approaches)
"""

import pandas as pd
import numpy as np
import logging
import joblib
from typing import Dict, Any, List, Union
from pathlib import Path
import json
from datetime import datetime


class ModelPredictor:
    """
    Handles model inference with preprocessing and validation.

    MLOps Principle: Consistent Pipeline
    Inference must use the EXACT same preprocessing as training:
    - Same feature engineering
    - Same scaling/encoding
    - Same feature order
    Otherwise you get training/serving skew - a major source of ML bugs!
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize ModelPredictor with configuration.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.serving_config = config['serving']
        self.feature_config = config['features']
        self.logger = logging.getLogger(__name__)

        # Model and preprocessing artifacts
        self.model = None
        self.scaler = None
        self.encoder = None
        self.feature_names = None

        # Prediction logs for monitoring
        self.prediction_logs = []

    def load_model_and_artifacts(
        self,
        model_path: str,
        artifacts_dir: str = "models/saved_models"
    ) -> None:
        """
        Load model and all preprocessing artifacts.

        MLOps Critical:
        All artifacts trained during model training must be loaded:
        - Model itself
        - Feature scaler
        - Categorical encoder
        - Feature names (for validation)

        Args:
            model_path: Path to the saved model
            artifacts_dir: Directory containing preprocessing artifacts
        """
        self.logger.info("Loading model and artifacts...")

        # Load model
        self.model = joblib.load(model_path)
        self.logger.info(f"Model loaded from {model_path}")

        # Load scaler
        scaler_path = Path(artifacts_dir) / "scaler.joblib"
        if scaler_path.exists():
            self.scaler = joblib.load(scaler_path)
            self.logger.info("Scaler loaded")

        # Load encoder
        encoder_path = Path(artifacts_dir) / "encoder.joblib"
        if encoder_path.exists():
            self.encoder = joblib.load(encoder_path)
            self.logger.info("Encoder loaded")

        # Load feature names
        feature_names_path = Path(artifacts_dir) / "feature_names.joblib"
        if feature_names_path.exists():
            self.feature_names = joblib.load(feature_names_path)
            self.logger.info(f"Feature names loaded: {len(self.feature_names)} features")

        self.logger.info("All artifacts loaded successfully")

    def validate_input(self, input_data: Union[Dict, pd.DataFrame]) -> pd.DataFrame:
        """
        Validate input data before prediction.

        MLOps Critical:
        Input validation prevents errors and catches data quality issues:
        - Check required features are present
        - Check data types are correct
        - Check for missing values
        - Check for out-of-range values

        Args:
            input_data: Input data (dict or DataFrame)

        Returns:
            Validated DataFrame

        Raises:
            ValueError: If input data is invalid
        """
        self.logger.info("Validating input data...")

        # Convert dict to DataFrame if necessary
        if isinstance(input_data, dict):
            # Check if it's a single sample or multiple samples
            if all(isinstance(v, (list, np.ndarray)) for v in input_data.values()):
                df = pd.DataFrame(input_data)
            else:
                df = pd.DataFrame([input_data])
        else:
            df = input_data.copy()

        # Expected input features (before feature engineering)
        expected_features = (
            self.feature_config['numerical_features'] +
            self.feature_config['categorical_features']
        )

        # Check for missing required features
        missing_features = set(expected_features) - set(df.columns)
        if missing_features:
            raise ValueError(f"Missing required features: {missing_features}")

        # Check for missing values
        if df.isnull().any().any():
            self.logger.warning("Input data contains missing values. Consider handling them.")

        self.logger.info(f"Input validation passed. Samples: {len(df)}")

        return df

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply the same preprocessing as training.

        MLOps Critical: Training/Serving Consistency
        This must match EXACTLY what was done during training.
        Any difference will cause training/serving skew.

        Args:
            df: Input DataFrame

        Returns:
            Preprocessed DataFrame
        """
        self.logger.info("Preprocessing input data...")

        # Import feature engineering (to avoid circular imports)
        from src.features.engineer import FeatureEngineer

        # Initialize feature engineer with loaded artifacts
        feature_engineer = FeatureEngineer(self.config)
        feature_engineer.scaler = self.scaler
        feature_engineer.encoder = self.encoder
        feature_engineer.feature_names = self.feature_names

        # Apply feature engineering (is_training=False to use loaded artifacts)
        df_processed = feature_engineer.engineer_features(df, is_training=False)

        # Ensure feature order matches training
        if self.feature_names is not None:
            # Reorder columns to match training
            missing_features = set(self.feature_names) - set(df_processed.columns)
            if missing_features:
                self.logger.warning(f"Missing features after preprocessing: {missing_features}")
                # Add missing features with zeros
                for feature in missing_features:
                    df_processed[feature] = 0

            # Select and reorder columns
            df_processed = df_processed[self.feature_names]

        self.logger.info("Preprocessing completed")

        return df_processed

    def predict(
        self,
        input_data: Union[Dict, pd.DataFrame],
        return_confidence: bool = False
    ) -> Union[np.ndarray, Dict[str, Any]]:
        """
        Make predictions on input data.

        MLOps Note:
        In production, this method would also:
        - Log predictions for monitoring
        - Measure latency
        - Check for data drift
        - Potentially trigger alerts

        Args:
            input_data: Input data (dict or DataFrame)
            return_confidence: Whether to return prediction confidence (if available)

        Returns:
            Predictions array or dict with predictions and metadata
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model_and_artifacts() first.")

        start_time = datetime.now()

        # Validate input
        df_validated = self.validate_input(input_data)

        # Preprocess
        df_processed = self.preprocess(df_validated)

        # Make predictions
        predictions = self.model.predict(df_processed)

        # Calculate latency
        latency_ms = (datetime.now() - start_time).total_seconds() * 1000

        # Log prediction (for monitoring)
        prediction_log = {
            'timestamp': datetime.now().isoformat(),
            'n_samples': len(predictions),
            'latency_ms': latency_ms,
            'mean_prediction': float(np.mean(predictions)),
            'std_prediction': float(np.std(predictions))
        }
        self.prediction_logs.append(prediction_log)

        self.logger.info(f"Predictions made for {len(predictions)} samples in {latency_ms:.2f}ms")

        if return_confidence:
            # For tree-based models, we can estimate confidence
            if hasattr(self.model, 'predict_proba'):
                confidence = self.model.predict_proba(df_processed)
                return {
                    'predictions': predictions,
                    'confidence': confidence,
                    'latency_ms': latency_ms
                }
            else:
                return {
                    'predictions': predictions,
                    'latency_ms': latency_ms
                }

        return predictions

    def predict_batch(
        self,
        input_file: str,
        output_file: str,
        batch_size: int = 1000
    ) -> None:
        """
        Make batch predictions from a file.

        MLOps Use:
        Batch prediction is common for:
        - Scoring large datasets overnight
        - Generating predictions for reports
        - A/B testing (score same data with different models)
        - Backfilling predictions

        Args:
            input_file: Path to input CSV file
            output_file: Path to save predictions
            batch_size: Number of samples to process at once
        """
        self.logger.info(f"Starting batch prediction from {input_file}...")

        # Read input data
        df_input = pd.read_csv(input_file)
        total_samples = len(df_input)

        self.logger.info(f"Loaded {total_samples} samples for batch prediction")

        # Process in batches
        predictions_list = []

        for i in range(0, total_samples, batch_size):
            batch_end = min(i + batch_size, total_samples)
            batch = df_input.iloc[i:batch_end]

            # Make predictions
            batch_predictions = self.predict(batch)
            predictions_list.extend(batch_predictions)

            self.logger.info(f"Processed batch {i//batch_size + 1}: samples {i+1}-{batch_end}/{total_samples}")

        # Add predictions to input data
        df_input['predicted_median_house_value'] = predictions_list

        # Save results
        df_input.to_csv(output_file, index=False)

        self.logger.info(f"Batch predictions saved to {output_file}")

    def get_prediction_stats(self) -> Dict[str, Any]:
        """
        Get statistics about predictions made.

        MLOps Monitoring:
        Track prediction statistics to detect:
        - Latency issues (predictions getting slower)
        - Prediction drift (distribution changing)
        - Volume changes (unexpected traffic)

        Returns:
            Dictionary with prediction statistics
        """
        if not self.prediction_logs:
            return {'message': 'No predictions made yet'}

        latencies = [log['latency_ms'] for log in self.prediction_logs]
        mean_predictions = [log['mean_prediction'] for log in self.prediction_logs]

        stats = {
            'total_prediction_calls': len(self.prediction_logs),
            'total_samples_predicted': sum(log['n_samples'] for log in self.prediction_logs),
            'latency': {
                'mean_ms': float(np.mean(latencies)),
                'median_ms': float(np.median(latencies)),
                'p95_ms': float(np.percentile(latencies, 95)),
                'max_ms': float(np.max(latencies))
            },
            'predictions': {
                'mean': float(np.mean(mean_predictions)),
                'std': float(np.std(mean_predictions))
            }
        }

        return stats

    def save_prediction_logs(self, output_path: str = "logs/prediction_logs.json") -> None:
        """
        Save prediction logs for analysis.

        Args:
            output_path: Path to save logs
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(self.prediction_logs, f, indent=4)

        self.logger.info(f"Prediction logs saved to {output_path}")
