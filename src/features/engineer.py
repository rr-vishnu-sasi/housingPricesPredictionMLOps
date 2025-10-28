"""
Feature Engineering Module

MLOps Importance:
Feature engineering is often the most impactful part of the ML pipeline.
Key MLOps principles applied here:
- Feature store concepts (consistent features across train/serve)
- Transformation persistence (save scalers/encoders for inference)
- Feature versioning (track which features are used in which models)
- Feature validation (ensure feature quality)
"""

import pandas as pd
import numpy as np
import logging
import joblib
from typing import Dict, Any, Tuple, List
from pathlib import Path
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.preprocessing import OneHotEncoder


class FeatureEngineer:
    """
    Handles feature engineering and transformation.

    MLOps Principle: Transformation Persistence
    All transformers (scalers, encoders) are saved so that:
    - The same transformations can be applied during inference
    - Training/serving skew is prevented
    - Features are consistent across environments
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize FeatureEngineer with configuration.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.feature_config = config['features']
        self.data_config = config['data']
        self.logger = logging.getLogger(__name__)

        # Initialize transformers
        self.scaler = None
        self.encoder = None
        self.feature_names = None

    def create_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create derived features from existing ones.

        MLOps Note:
        Domain knowledge-driven features often outperform complex models.
        Document the rationale behind each feature for:
        - Team knowledge sharing
        - Model interpretability
        - Feature importance analysis

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with additional derived features
        """
        self.logger.info("Creating derived features...")

        df = df.copy()

        # Feature 1: Rooms per household
        # Rationale: Larger homes (more rooms per household) may be more valuable
        if 'rooms_per_household' in self.feature_config['derived_features']:
            df['rooms_per_household'] = df['total_rooms'] / df['households']
            # Handle any division by zero
            df['rooms_per_household'].replace([np.inf, -np.inf], np.nan, inplace=True)
            df['rooms_per_household'].fillna(df['rooms_per_household'].median(), inplace=True)

        # Feature 2: Bedrooms to rooms ratio
        # Rationale: A higher bedroom ratio might indicate smaller individual rooms
        if 'bedrooms_per_room' in self.feature_config['derived_features']:
            df['bedrooms_per_room'] = df['total_bedrooms'] / df['total_rooms']
            df['bedrooms_per_room'].replace([np.inf, -np.inf], np.nan, inplace=True)
            df['bedrooms_per_room'].fillna(df['bedrooms_per_room'].median(), inplace=True)

        # Feature 3: Population per household
        # Rationale: Population density in households might affect prices
        if 'population_per_household' in self.feature_config['derived_features']:
            df['population_per_household'] = df['population'] / df['households']
            df['population_per_household'].replace([np.inf, -np.inf], np.nan, inplace=True)
            df['population_per_household'].fillna(df['population_per_household'].median(), inplace=True)

        self.logger.info(f"Created {len(self.feature_config['derived_features'])} derived features")

        return df

    def encode_categorical_features(self, df: pd.DataFrame, is_training: bool = True) -> pd.DataFrame:
        """
        Encode categorical features using one-hot encoding.

        MLOps Critical Point:
        During training: fit_transform (learn categories)
        During inference: transform (use learned categories)
        This prevents training/serving skew.

        Args:
            df: Input DataFrame
            is_training: Whether this is training data (fit) or inference data (transform only)

        Returns:
            DataFrame with encoded categorical features
        """
        self.logger.info("Encoding categorical features...")

        df = df.copy()
        categorical_features = self.feature_config['categorical_features']

        if not categorical_features:
            self.logger.info("No categorical features to encode")
            return df

        # Check if categorical columns exist
        existing_categorical = [col for col in categorical_features if col in df.columns]

        if not existing_categorical:
            self.logger.warning("No categorical features found in DataFrame")
            return df

        if is_training:
            # Training: fit and transform
            self.encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
            encoded_features = self.encoder.fit_transform(df[existing_categorical])

            # Get feature names
            encoded_feature_names = self.encoder.get_feature_names_out(existing_categorical)

        else:
            # Inference: only transform using fitted encoder
            if self.encoder is None:
                raise ValueError("Encoder not fitted. Cannot transform categorical features.")

            encoded_features = self.encoder.transform(df[existing_categorical])
            encoded_feature_names = self.encoder.get_feature_names_out(existing_categorical)

        # Create DataFrame with encoded features
        encoded_df = pd.DataFrame(
            encoded_features,
            columns=encoded_feature_names,
            index=df.index
        )

        # Drop original categorical columns and add encoded ones
        df = df.drop(existing_categorical, axis=1)
        df = pd.concat([df, encoded_df], axis=1)

        self.logger.info(f"Encoded {len(existing_categorical)} categorical features into {len(encoded_feature_names)} binary features")

        return df

    def scale_numerical_features(self, df: pd.DataFrame, is_training: bool = True) -> pd.DataFrame:
        """
        Scale numerical features.

        MLOps Critical Point:
        Scaler must be fitted on training data only, then applied to:
        - Validation data
        - Test data
        - Production inference data
        Using the SAME scaler prevents data leakage and ensures consistency.

        Args:
            df: Input DataFrame
            is_training: Whether this is training data (fit) or inference data (transform only)

        Returns:
            DataFrame with scaled features
        """
        self.logger.info("Scaling numerical features...")

        df = df.copy()

        # Get numerical features (exclude target if present)
        numerical_features = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

        # Remove target column if present
        if 'median_house_value' in numerical_features:
            numerical_features.remove('median_house_value')

        if not numerical_features:
            self.logger.warning("No numerical features to scale")
            return df

        # Select scaler based on configuration
        scaling_method = self.feature_config['scaling_method']

        if is_training:
            # Training: fit and transform
            if scaling_method == 'standard':
                self.scaler = StandardScaler()
            elif scaling_method == 'minmax':
                self.scaler = MinMaxScaler()
            elif scaling_method == 'robust':
                self.scaler = RobustScaler()
            else:
                self.logger.warning(f"Unknown scaling method: {scaling_method}. Using StandardScaler.")
                self.scaler = StandardScaler()

            df[numerical_features] = self.scaler.fit_transform(df[numerical_features])
            self.logger.info(f"Fitted and transformed {len(numerical_features)} numerical features using {scaling_method} scaling")

        else:
            # Inference: only transform using fitted scaler
            if self.scaler is None:
                raise ValueError("Scaler not fitted. Cannot transform numerical features.")

            df[numerical_features] = self.scaler.transform(df[numerical_features])
            self.logger.info(f"Transformed {len(numerical_features)} numerical features using fitted scaler")

        return df

    def save_artifacts(self, output_dir: str = "models/saved_models") -> None:
        """
        Save feature engineering artifacts (scaler, encoder).

        MLOps Critical:
        These artifacts are REQUIRED for production inference.
        Without them, you cannot reproduce the same feature transformations,
        leading to training/serving skew and model failure.

        Args:
            output_dir: Directory to save artifacts
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        if self.scaler is not None:
            scaler_path = Path(output_dir) / "scaler.joblib"
            joblib.dump(self.scaler, scaler_path)
            self.logger.info(f"Scaler saved to {scaler_path}")

        if self.encoder is not None:
            encoder_path = Path(output_dir) / "encoder.joblib"
            joblib.dump(self.encoder, encoder_path)
            self.logger.info(f"Encoder saved to {encoder_path}")

        # Save feature names for validation during inference
        if self.feature_names is not None:
            feature_names_path = Path(output_dir) / "feature_names.joblib"
            joblib.dump(self.feature_names, feature_names_path)
            self.logger.info(f"Feature names saved to {feature_names_path}")

    def load_artifacts(self, input_dir: str = "models/saved_models") -> None:
        """
        Load feature engineering artifacts.

        Args:
            input_dir: Directory containing artifacts
        """
        scaler_path = Path(input_dir) / "scaler.joblib"
        encoder_path = Path(input_dir) / "encoder.joblib"
        feature_names_path = Path(input_dir) / "feature_names.joblib"

        if scaler_path.exists():
            self.scaler = joblib.load(scaler_path)
            self.logger.info(f"Scaler loaded from {scaler_path}")

        if encoder_path.exists():
            self.encoder = joblib.load(encoder_path)
            self.logger.info(f"Encoder loaded from {encoder_path}")

        if feature_names_path.exists():
            self.feature_names = joblib.load(feature_names_path)
            self.logger.info(f"Feature names loaded from {feature_names_path}")

    def engineer_features(self, df: pd.DataFrame, is_training: bool = True) -> pd.DataFrame:
        """
        Main feature engineering pipeline.

        MLOps Pipeline Pattern:
        Each transformation is a separate, testable step.
        This modular approach allows:
        - Easy debugging (identify which step failed)
        - A/B testing (compare different feature sets)
        - Incremental improvements (add/remove steps)

        Args:
            df: Input DataFrame
            is_training: Whether this is training data

        Returns:
            DataFrame with engineered features
        """
        self.logger.info("Starting feature engineering pipeline...")

        # Step 1: Create derived features
        df = self.create_derived_features(df)

        # Step 2: Encode categorical features
        df = self.encode_categorical_features(df, is_training=is_training)

        # Step 3: Scale numerical features
        df = self.scale_numerical_features(df, is_training=is_training)

        # Store feature names (excluding target)
        feature_columns = [col for col in df.columns if col != 'median_house_value']
        if is_training:
            self.feature_names = feature_columns

        self.logger.info(f"Feature engineering completed. Final feature count: {len(feature_columns)}")

        return df
