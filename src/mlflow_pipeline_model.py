"""
MLflow Custom Model with Preprocessing Pipeline

MLOps Critical Concept:
The model served in production must include ALL preprocessing steps,
not just the ML algorithm!

This creates a "wrapper" model that:
1. Accepts RAW input (like users would send)
2. Applies ALL preprocessing (feature engineering, encoding, scaling)
3. Makes prediction
4. Returns result

This is how production APIs should work!
"""

import mlflow
import pandas as pd
import numpy as np
from typing import Dict, Any
import joblib


class HousingPricePipelineModel(mlflow.pyfunc.PythonModel):
    """
    Custom MLflow model that includes complete preprocessing pipeline.

    Simple Explanation:
    This is a "wrapper" that包含 everything:
    - Feature engineering
    - Encoding
    - Scaling
    - Model prediction

    User sends raw data → This does everything → Returns prediction
    """

    def load_context(self, context):
        """
        Load all artifacts (model, scaler, encoder, etc.)

        This runs once when model is loaded.

        Args:
            context: MLflow context with artifact paths
        """
        # Load the trained model
        self.model = joblib.load(context.artifacts["model"])

        # Load preprocessing artifacts
        self.scaler = joblib.load(context.artifacts["scaler"])
        self.encoder = joblib.load(context.artifacts["encoder"])
        self.feature_names = joblib.load(context.artifacts["feature_names"])

        print("✓ Model and preprocessing artifacts loaded")

    def _create_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create derived features (same as training).

        Args:
            df: DataFrame with raw features

        Returns:
            DataFrame with derived features added
        """
        df = df.copy()

        # rooms_per_household
        df['rooms_per_household'] = df['total_rooms'] / df['households']
        df['rooms_per_household'] = df['rooms_per_household'].replace([np.inf, -np.inf], np.nan)
        df['rooms_per_household'] = df['rooms_per_household'].fillna(df['rooms_per_household'].median())

        # bedrooms_per_room
        df['bedrooms_per_room'] = df['total_bedrooms'] / df['total_rooms']
        df['bedrooms_per_room'] = df['bedrooms_per_room'].replace([np.inf, -np.inf], np.nan)
        df['bedrooms_per_room'] = df['bedrooms_per_room'].fillna(df['bedrooms_per_room'].median())

        # population_per_household
        df['population_per_household'] = df['population'] / df['households']
        df['population_per_household'] = df['population_per_household'].replace([np.inf, -np.inf], np.nan)
        df['population_per_household'] = df['population_per_household'].fillna(df['population_per_household'].median())

        return df

    def predict(self, context, model_input):
        """
        Make prediction on RAW input data.

        This is the magic method that:
        1. Takes raw data
        2. Applies ALL preprocessing
        3. Makes prediction
        4. Returns result

        Args:
            context: MLflow context
            model_input: Raw input DataFrame

        Returns:
            Predictions array
        """
        # Input is a DataFrame with raw features
        df = model_input.copy()

        # Step 1: Create derived features
        df = self._create_derived_features(df)

        # Step 2: Encode categorical features FIRST
        if 'ocean_proximity' in df.columns:
            encoded = self.encoder.transform(df[['ocean_proximity']])
            encoded_names = self.encoder.get_feature_names_out(['ocean_proximity'])

            for i, name in enumerate(encoded_names):
                df[name] = encoded[:, i]

            df = df.drop('ocean_proximity', axis=1)

        # Step 3: Scale numerical features (all columns now)
        # Convert to numpy array to avoid feature name issues
        df_values = self.scaler.transform(df.values)
        df = pd.DataFrame(df_values, columns=df.columns, index=df.index)

        # Step 4: Ensure correct feature order
        df = df[self.feature_names]

        # Step 5: Make prediction
        predictions = self.model.predict(df.values)

        return predictions


def save_pipeline_model_to_mlflow(
    model,
    scaler,
    encoder,
    feature_names,
    model_name: str = "housing_price_predictor_pipeline"
):
    """
    Save complete pipeline (model + preprocessing) to MLflow.

    This creates a model that accepts RAW data!

    Args:
        model: Trained sklearn model
        scaler: Fitted scaler
        encoder: Fitted encoder
        feature_names: List of feature names
        model_name: Name to register in MLflow
    """
    import tempfile
    import os

    # Save artifacts to temp directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Save all components
        model_path = os.path.join(tmp_dir, "model.joblib")
        scaler_path = os.path.join(tmp_dir, "scaler.joblib")
        encoder_path = os.path.join(tmp_dir, "encoder.joblib")
        features_path = os.path.join(tmp_dir, "feature_names.joblib")

        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)
        joblib.dump(encoder, encoder_path)
        joblib.dump(feature_names, features_path)

        # Define artifacts
        artifacts = {
            "model": model_path,
            "scaler": scaler_path,
            "encoder": encoder_path,
            "feature_names": features_path
        }

        # Create example input (for schema)
        example_input = pd.DataFrame([{
            'median_income': 8.3252,
            'housing_median_age': 41.0,
            'total_rooms': 880,
            'total_bedrooms': 129,
            'population': 322,
            'households': 126,
            'latitude': 37.88,
            'longitude': -122.23,
            'ocean_proximity': 'NEAR BAY'
        }])

        # Log pipeline model to MLflow
        mlflow.pyfunc.log_model(
            artifact_path="pipeline_model",
            python_model=HousingPricePipelineModel(),
            artifacts=artifacts,
            registered_model_name=model_name,
            input_example=example_input
        )

        print(f"✓ Complete pipeline model saved to MLflow: {model_name}")
        print("  This model accepts RAW data!")


if __name__ == "__main__":
    print("This module provides a complete preprocessing + model pipeline for MLflow")
    print("\nTo use:")
    print("  from src.mlflow_pipeline_model import save_pipeline_model_to_mlflow")
    print("  save_pipeline_model_to_mlflow(model, scaler, encoder, feature_names)")
