"""
Data Ingestion Module

MLOps Importance:
This module handles the critical first step of the ML pipeline - data ingestion.
In production MLOps:
- Data sources can be databases, APIs, data lakes, or streaming sources
- Data validation catches issues early before they affect model training
- Data versioning ensures reproducibility
- Monitoring data quality prevents model degradation
"""

import pandas as pd
import logging
from typing import Dict, Any, Tuple
from pathlib import Path
from sklearn.datasets import fetch_california_housing


class DataIngestor:
    """
    Handles data ingestion and initial quality checks.

    MLOps Principle: Separation of Concerns
    Each class has a single responsibility, making the pipeline:
    - Easier to test
    - Easier to maintain
    - Easier to replace components (e.g., switch data sources)
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize DataIngestor with configuration.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.data_config = config['data']
        self.quality_config = config['data_quality']
        self.logger = logging.getLogger(__name__)

    def fetch_data(self) -> pd.DataFrame:
        """
        Fetch housing data (California Housing dataset as example).

        MLOps Note:
        In production, this would connect to:
        - Data warehouses (Snowflake, BigQuery, Redshift)
        - Data lakes (S3, GCS, Azure Blob)
        - Databases (PostgreSQL, MongoDB)
        - APIs or streaming sources (Kafka)

        Returns:
            DataFrame containing raw data
        """
        self.logger.info("Fetching California Housing dataset...")

        try:
            # Fetch the California Housing dataset
            housing_data = fetch_california_housing(as_frame=True)
            df = housing_data.frame

            # Rename columns for clarity
            df.rename(columns={
                'MedInc': 'median_income',
                'HouseAge': 'housing_median_age',
                'AveRooms': 'avg_rooms',
                'AveBedrms': 'avg_bedrooms',
                'Population': 'population',
                'AveOccup': 'avg_occupancy',
                'Latitude': 'latitude',
                'Longitude': 'longitude',
                'MedHouseVal': 'median_house_value'
            }, inplace=True)

            # Add ocean_proximity feature for categorical encoding practice
            # Simplified version based on latitude/longitude
            df['ocean_proximity'] = 'INLAND'
            df.loc[df['longitude'] < -121, 'ocean_proximity'] = 'NEAR BAY'
            df.loc[(df['latitude'] < 35) & (df['longitude'] < -118), 'ocean_proximity'] = 'NEAR OCEAN'
            df.loc[df['latitude'] > 38, 'ocean_proximity'] = '<1H OCEAN'

            # Convert to actual room/bedroom counts for more realistic features
            df['total_rooms'] = (df['avg_rooms'] * df['population'] / df['avg_occupancy']).astype(int)
            df['total_bedrooms'] = (df['avg_bedrooms'] * df['population'] / df['avg_occupancy']).astype(int)
            df['households'] = (df['population'] / df['avg_occupancy']).astype(int)

            # Drop intermediate columns
            df = df.drop(['avg_rooms', 'avg_bedrooms', 'avg_occupancy'], axis=1)

            # Convert target to actual prices (multiply by 100,000)
            df['median_house_value'] = df['median_house_value'] * 100000

            self.logger.info(f"Data fetched successfully. Shape: {df.shape}")
            return df

        except Exception as e:
            self.logger.error(f"Error fetching data: {e}")
            raise

    def perform_quality_checks(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Perform data quality checks.

        MLOps Importance:
        Data quality issues are the #1 cause of ML model failures in production.
        These checks help:
        - Detect data pipeline issues early
        - Prevent training on corrupt data
        - Maintain model performance over time
        - Alert teams to data drift

        Args:
            df: Input DataFrame

        Returns:
            Tuple of (cleaned DataFrame, quality report dictionary)
        """
        self.logger.info("Performing data quality checks...")

        quality_report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'checks_performed': []
        }

        # Check 1: Missing Values
        if self.quality_config['check_missing_values']:
            missing_values = df.isnull().sum()
            missing_pct = (missing_values / len(df)) * 100

            quality_report['missing_values'] = {
                col: {'count': int(count), 'percentage': float(pct)}
                for col, count, pct in zip(df.columns, missing_values, missing_pct)
                if count > 0
            }

            if missing_values.sum() > 0:
                self.logger.warning(f"Found {missing_values.sum()} missing values")
                # For this example, drop rows with missing values
                # In production, you might impute or use more sophisticated strategies
                df = df.dropna()
                self.logger.info(f"Dropped rows with missing values. New shape: {df.shape}")

            quality_report['checks_performed'].append('missing_values')

        # Check 2: Duplicates
        if self.quality_config['check_duplicates']:
            duplicates = df.duplicated().sum()
            quality_report['duplicates'] = int(duplicates)

            if duplicates > 0:
                self.logger.warning(f"Found {duplicates} duplicate rows")
                df = df.drop_duplicates()
                self.logger.info(f"Removed duplicates. New shape: {df.shape}")

            quality_report['checks_performed'].append('duplicates')

        # Check 3: Outliers (using IQR method)
        if self.quality_config['check_outliers']:
            outlier_info = {}
            numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns

            for col in numeric_columns:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - self.quality_config['outlier_threshold'] * IQR
                upper_bound = Q3 + self.quality_config['outlier_threshold'] * IQR

                outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
                outlier_info[col] = {
                    'count': int(outliers),
                    'percentage': float(outliers / len(df) * 100)
                }

            quality_report['outliers'] = outlier_info
            quality_report['checks_performed'].append('outliers')

            # Log outlier summary
            total_outliers = sum(info['count'] for info in outlier_info.values())
            self.logger.info(f"Detected {total_outliers} outliers across all columns")
            # Note: We're not removing outliers here, as they might be legitimate
            # In production, you'd apply domain knowledge

        quality_report['final_rows'] = len(df)
        quality_report['rows_removed'] = quality_report['total_rows'] - quality_report['final_rows']

        self.logger.info(f"Data quality checks completed. Quality report: {quality_report}")

        return df, quality_report

    def save_data(self, df: pd.DataFrame, output_path: str) -> None:
        """
        Save data to disk.

        MLOps Note:
        Saving intermediate data artifacts helps with:
        - Debugging pipeline issues
        - Data versioning and lineage tracking
        - Rerunning downstream steps without full recomputation

        Args:
            df: DataFrame to save
            output_path: Path where to save the data
        """
        # Create directory if it doesn't exist
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        df.to_csv(output_path, index=False)
        self.logger.info(f"Data saved to {output_path}")

    def ingest(self) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Main ingestion pipeline: fetch, validate, and save data.

        Returns:
            Tuple of (cleaned DataFrame, quality report)
        """
        self.logger.info("Starting data ingestion pipeline...")

        # Fetch data
        df = self.fetch_data()

        # Perform quality checks
        df_cleaned, quality_report = self.perform_quality_checks(df)

        # Save raw and processed data
        self.save_data(df, self.data_config['raw_data_path'])
        self.save_data(df_cleaned, self.data_config['processed_data_path'])

        self.logger.info("Data ingestion pipeline completed successfully")

        return df_cleaned, quality_report
