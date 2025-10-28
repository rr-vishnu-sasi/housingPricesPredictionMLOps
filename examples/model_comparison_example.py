"""
Model Comparison Example

This script demonstrates how to compare multiple models using the model registry.

MLOps Principle: Model Comparison
Always compare multiple models before deploying to production:
- Different algorithms
- Different hyperparameters
- Models trained on different data
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models.registry import ModelRegistry
from src.utils import load_config, setup_logging
import logging
import pandas as pd


def main():
    """
    Compare all models in the registry.
    """
    print("=" * 60)
    print("MODEL COMPARISON EXAMPLE")
    print("=" * 60)

    # Load configuration
    config = load_config()
    setup_logging(config)
    logger = logging.getLogger(__name__)

    # Initialize model registry
    model_registry = ModelRegistry(config)

    # Get registry summary
    summary = model_registry.get_registry_summary()

    print(f"\nTotal models in registry: {summary['total_models']}")
    print(f"Models by stage: {summary['models_by_stage']}")

    if summary['total_models'] == 0:
        logger.error("No models in registry. Please run main_pipeline.py first.")
        return

    # List all models
    all_models = model_registry.list_models()

    print("\n" + "=" * 60)
    print("ALL REGISTERED MODELS")
    print("=" * 60)

    comparison_data = []

    for model in all_models:
        print(f"\nModel Version: {model['version_id']}")
        print(f"  Stage: {model['stage']}")
        print(f"  Registered: {model['registered_at']}")
        print(f"  Model Type: {model['metadata'].get('model_type', 'unknown')}")

        metrics = model['evaluation'].get('metrics', {})
        print(f"  Metrics:")
        for metric_name, metric_value in metrics.items():
            print(f"    {metric_name}: {metric_value:,.4f}")

        # Collect for comparison
        comparison_data.append({
            'version_id': model['version_id'],
            'stage': model['stage'],
            'model_type': model['metadata'].get('model_type', 'unknown'),
            'rmse': metrics.get('rmse', float('inf')),
            'mae': metrics.get('mae', float('inf')),
            'r2_score': metrics.get('r2_score', 0.0),
            'mape': metrics.get('mape', float('inf'))
        })

    # Create comparison DataFrame
    print("\n" + "=" * 60)
    print("MODEL COMPARISON TABLE")
    print("=" * 60)

    comparison_df = pd.DataFrame(comparison_data)

    # Sort by R² score (higher is better)
    comparison_df = comparison_df.sort_values('r2_score', ascending=False)

    print("\n" + comparison_df.to_string(index=False))

    # Identify best model
    print("\n" + "=" * 60)
    print("BEST MODEL ANALYSIS")
    print("=" * 60)

    best_model = comparison_df.iloc[0]

    print(f"\nBest model by R² score:")
    print(f"  Version: {best_model['version_id']}")
    print(f"  Model Type: {best_model['model_type']}")
    print(f"  R² Score: {best_model['r2_score']:.4f}")
    print(f"  RMSE: ${best_model['rmse']:,.2f}")
    print(f"  MAE: ${best_model['mae']:,.2f}")
    print(f"  Current Stage: {best_model['stage']}")

    # Compare production model vs best model
    production_models = [m for m in all_models if m['stage'] == 'production']

    if production_models:
        print("\n" + "=" * 60)
        print("PRODUCTION MODEL COMPARISON")
        print("=" * 60)

        prod_model = production_models[0]
        prod_metrics = prod_model['evaluation'].get('metrics', {})

        print(f"\nCurrent Production Model: {prod_model['version_id']}")
        print(f"  R² Score: {prod_metrics.get('r2_score', 0.0):.4f}")

        print(f"\nBest Available Model: {best_model['version_id']}")
        print(f"  R² Score: {best_model['r2_score']:.4f}")

        improvement = ((best_model['r2_score'] - prod_metrics.get('r2_score', 0.0))
                      / prod_metrics.get('r2_score', 1.0) * 100)

        if improvement > 0:
            print(f"\n✓ Best model shows {improvement:.2f}% improvement over production")
            print("  Consider promoting to production!")
        else:
            print(f"\n✓ Production model is performing well (best by {abs(improvement):.2f}%)")
    else:
        print("\n" + "=" * 60)
        print("NO PRODUCTION MODEL")
        print("=" * 60)
        print(f"\nConsider promoting {best_model['version_id']} to production")

    # MLOps recommendations
    print("\n" + "=" * 60)
    print("MLOPS RECOMMENDATIONS")
    print("=" * 60)

    print("\nBased on this analysis:")

    if summary['total_models'] == 1:
        print("  • Train more models with different hyperparameters")
        print("  • Try different algorithms (e.g., Gradient Boosting)")
        print("  • Experiment with feature engineering")

    if not production_models:
        print("  • Promote best model to production stage")
        print("  • Set up A/B testing infrastructure")
        print("  • Implement monitoring and alerting")

    print("\n  • Continue tracking model performance over time")
    print("  • Monitor for data drift in production")
    print("  • Set up automated retraining schedule")


if __name__ == "__main__":
    main()
