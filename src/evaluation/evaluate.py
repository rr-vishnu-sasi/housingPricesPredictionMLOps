"""
Model Evaluation Module

MLOps Importance:
Evaluation is not just about calculating metrics once.
In production MLOps, evaluation includes:
- Continuous monitoring of model performance
- Detecting model drift and degradation
- A/B testing different model versions
- Setting up alerts when performance drops
- Generating performance reports for stakeholders
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Tuple
from pathlib import Path
import json

from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
    mean_absolute_percentage_error
)


class ModelEvaluator:
    """
    Handles model evaluation with comprehensive metrics.

    MLOps Principle: Metrics-Driven Development
    Track multiple metrics because:
    - Different stakeholders care about different metrics
    - No single metric tells the whole story
    - Metrics help detect specific types of model failures
    - Metrics evolution over time shows model health
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize ModelEvaluator with configuration.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.eval_config = config['evaluation']
        self.logger = logging.getLogger(__name__)

    def calculate_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> Dict[str, float]:
        """
        Calculate comprehensive evaluation metrics.

        MLOps Note:
        Different metrics reveal different aspects of model performance:
        - RMSE: Penalizes large errors heavily (good for detecting outliers)
        - MAE: More robust to outliers, easier to interpret
        - R2: Proportion of variance explained (0-1 scale)
        - MAPE: Percentage error (useful for business stakeholders)

        Args:
            y_true: True target values
            y_pred: Predicted values

        Returns:
            Dictionary of metric names and values
        """
        self.logger.info("Calculating evaluation metrics...")

        metrics = {}

        # Root Mean Squared Error
        if 'rmse' in self.eval_config['metrics']:
            rmse = np.sqrt(mean_squared_error(y_true, y_pred))
            metrics['rmse'] = float(rmse)
            self.logger.info(f"RMSE: ${rmse:,.2f}")

        # Mean Absolute Error
        if 'mae' in self.eval_config['metrics']:
            mae = mean_absolute_error(y_true, y_pred)
            metrics['mae'] = float(mae)
            self.logger.info(f"MAE: ${mae:,.2f}")

        # R-squared Score
        if 'r2_score' in self.eval_config['metrics']:
            r2 = r2_score(y_true, y_pred)
            metrics['r2_score'] = float(r2)
            self.logger.info(f"R² Score: {r2:.4f}")

        # Mean Absolute Percentage Error
        if 'mape' in self.eval_config['metrics']:
            # Avoid division by zero
            mask = y_true != 0
            if mask.sum() > 0:
                mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
                metrics['mape'] = float(mape)
                self.logger.info(f"MAPE: {mape:.2f}%")

        return metrics

    def check_performance_thresholds(self, metrics: Dict[str, float]) -> Dict[str, bool]:
        """
        Check if metrics meet defined thresholds.

        MLOps Critical:
        Threshold checks enable:
        - Automated model validation (pass/fail)
        - Alerts when model degrades
        - Preventing bad models from reaching production
        - CI/CD integration (fail pipeline if metrics are poor)

        Args:
            metrics: Dictionary of calculated metrics

        Returns:
            Dictionary of threshold checks (True = passed, False = failed)
        """
        self.logger.info("Checking performance thresholds...")

        checks = {}

        # Check RMSE threshold
        if 'rmse' in metrics and 'threshold_rmse' in self.eval_config:
            threshold = self.eval_config['threshold_rmse']
            passed = metrics['rmse'] <= threshold
            checks['rmse_threshold'] = passed

            if passed:
                self.logger.info(f"✓ RMSE threshold check passed: {metrics['rmse']:.2f} <= {threshold}")
            else:
                self.logger.warning(f"✗ RMSE threshold check failed: {metrics['rmse']:.2f} > {threshold}")

        # Check R2 threshold
        if 'r2_score' in metrics and 'threshold_r2' in self.eval_config:
            threshold = self.eval_config['threshold_r2']
            passed = metrics['r2_score'] >= threshold
            checks['r2_threshold'] = passed

            if passed:
                self.logger.info(f"✓ R² threshold check passed: {metrics['r2_score']:.4f} >= {threshold}")
            else:
                self.logger.warning(f"✗ R² threshold check failed: {metrics['r2_score']:.4f} < {threshold}")

        return checks

    def analyze_residuals(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> Dict[str, Any]:
        """
        Analyze prediction residuals (errors).

        MLOps Insight:
        Residual analysis helps identify:
        - Systematic biases (model consistently over/under predicts)
        - Heteroscedasticity (error variance changes with prediction magnitude)
        - Outliers (cases where model fails badly)
        These insights guide model improvements.

        Args:
            y_true: True target values
            y_pred: Predicted values

        Returns:
            Dictionary of residual statistics
        """
        self.logger.info("Analyzing prediction residuals...")

        residuals = y_true - y_pred

        analysis = {
            'mean_residual': float(np.mean(residuals)),
            'std_residual': float(np.std(residuals)),
            'min_residual': float(np.min(residuals)),
            'max_residual': float(np.max(residuals)),
            'median_residual': float(np.median(residuals)),
            'q25_residual': float(np.percentile(residuals, 25)),
            'q75_residual': float(np.percentile(residuals, 75))
        }

        # Check for systematic bias
        if abs(analysis['mean_residual']) > 1000:  # Arbitrary threshold for housing prices
            self.logger.warning(
                f"Model shows systematic bias: mean residual = ${analysis['mean_residual']:,.2f}"
            )
        else:
            self.logger.info("No significant systematic bias detected")

        return analysis

    def create_evaluation_report(
        self,
        metrics: Dict[str, float],
        threshold_checks: Dict[str, bool],
        residual_analysis: Dict[str, Any],
        feature_importance: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Create comprehensive evaluation report.

        MLOps Use:
        Evaluation reports serve multiple purposes:
        - Documentation for model registry
        - Comparison across model versions
        - Communication with stakeholders
        - Compliance and audit trail

        Args:
            metrics: Calculated metrics
            threshold_checks: Threshold check results
            residual_analysis: Residual analysis results
            feature_importance: Feature importance scores (optional)

        Returns:
            Complete evaluation report dictionary
        """
        self.logger.info("Creating evaluation report...")

        report = {
            'metrics': metrics,
            'threshold_checks': threshold_checks,
            'residual_analysis': residual_analysis,
            'all_checks_passed': all(threshold_checks.values()) if threshold_checks else True
        }

        if feature_importance:
            report['feature_importance'] = feature_importance

        return report

    def save_evaluation_report(
        self,
        report: Dict[str, Any],
        output_path: str = "logs/evaluation_report.json"
    ) -> None:
        """
        Save evaluation report to disk.

        Args:
            report: Evaluation report dictionary
            output_path: Path to save the report
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=4)

        self.logger.info(f"Evaluation report saved to {output_path}")

    def evaluate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        feature_importance: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Main evaluation pipeline.

        Args:
            y_true: True target values
            y_pred: Predicted values
            feature_importance: Feature importance scores (optional)

        Returns:
            Complete evaluation report
        """
        self.logger.info("Starting model evaluation pipeline...")

        # Calculate metrics
        metrics = self.calculate_metrics(y_true, y_pred)

        # Check thresholds
        threshold_checks = self.check_performance_thresholds(metrics)

        # Analyze residuals
        residual_analysis = self.analyze_residuals(y_true, y_pred)

        # Create report
        report = self.create_evaluation_report(
            metrics,
            threshold_checks,
            residual_analysis,
            feature_importance
        )

        self.logger.info("Model evaluation completed")

        return report

    def compare_models(
        self,
        model_reports: List[Dict[str, Any]],
        model_names: List[str]
    ) -> pd.DataFrame:
        """
        Compare multiple models side by side.

        MLOps Use:
        Model comparison helps select the best model for production:
        - Compare different algorithms
        - Compare different hyperparameters
        - Track performance evolution over time

        Args:
            model_reports: List of evaluation reports
            model_names: List of model names

        Returns:
            DataFrame with comparison results
        """
        self.logger.info(f"Comparing {len(model_reports)} models...")

        comparison_data = []

        for name, report in zip(model_names, model_reports):
            row = {'model': name}
            row.update(report['metrics'])
            row['all_checks_passed'] = report.get('all_checks_passed', False)
            comparison_data.append(row)

        comparison_df = pd.DataFrame(comparison_data)

        self.logger.info("Model comparison completed")

        return comparison_df
