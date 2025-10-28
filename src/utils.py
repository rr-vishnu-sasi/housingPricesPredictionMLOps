"""
Utility functions for the MLOps pipeline.

MLOps Importance:
- Centralized utilities promote code reusability and DRY principles
- Consistent logging helps with debugging and monitoring
- Configuration management ensures reproducibility across environments
"""

import yaml
import json
import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    MLOps Insight:
    Configuration management is crucial in MLOps. It allows you to:
    - Version control your experimental parameters
    - Reproduce experiments exactly
    - Switch between development, staging, and production settings easily
    - Track what parameters were used for each model version

    Args:
        config_path: Path to configuration YAML file

    Returns:
        Dictionary containing configuration parameters
    """
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        logging.info(f"Configuration loaded from {config_path}")
        return config
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {config_path}")
        raise
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML configuration: {e}")
        raise


def setup_logging(config: Dict[str, Any]) -> None:
    """
    Setup logging configuration.

    MLOps Insight:
    Proper logging is essential for:
    - Debugging issues in production
    - Monitoring pipeline health
    - Auditing model predictions
    - Understanding system behavior over time

    Args:
        config: Configuration dictionary
    """
    log_config = config.get('logging', {})
    log_level = getattr(logging, log_config.get('level', 'INFO'))
    log_format = log_config.get('format',
                                  '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file = log_config.get('log_file', 'logs/pipeline.log')

    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also output to console
        ]
    )

    logging.info("Logging setup completed")


def save_json(data: Dict[str, Any], filepath: str) -> None:
    """
    Save dictionary as JSON file.

    Args:
        data: Dictionary to save
        filepath: Path where to save the JSON file
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4, default=str)
    logging.info(f"JSON data saved to {filepath}")


def load_json(filepath: str) -> Dict[str, Any]:
    """
    Load dictionary from JSON file.

    Args:
        filepath: Path to JSON file

    Returns:
        Dictionary containing JSON data
    """
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        logging.info(f"JSON data loaded from {filepath}")
        return data
    except FileNotFoundError:
        logging.warning(f"JSON file not found: {filepath}")
        return {}


def generate_version_id(strategy: str = "timestamp") -> str:
    """
    Generate version ID for model versioning.

    MLOps Insight:
    Model versioning is critical for:
    - Rolling back to previous versions if needed
    - A/B testing different model versions
    - Tracking model lineage and evolution
    - Compliance and audit requirements

    Args:
        strategy: Versioning strategy (timestamp, semantic, auto_increment)

    Returns:
        Version ID string
    """
    if strategy == "timestamp":
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    elif strategy == "semantic":
        # In production, this would check existing versions and increment
        return "v1.0.0"
    elif strategy == "auto_increment":
        # In production, this would check existing versions and increment
        return "v1"
    else:
        return datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_directory_exists(directory: str) -> None:
    """
    Create directory if it doesn't exist.

    Args:
        directory: Path to directory
    """
    os.makedirs(directory, exist_ok=True)


def get_project_root() -> Path:
    """
    Get the project root directory.

    Returns:
        Path object pointing to project root
    """
    return Path(__file__).parent.parent


def compute_mape(y_true, y_pred) -> float:
    """
    Compute Mean Absolute Percentage Error.

    Args:
        y_true: True values
        y_pred: Predicted values

    Returns:
        MAPE value as percentage
    """
    import numpy as np
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    # Avoid division by zero
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
