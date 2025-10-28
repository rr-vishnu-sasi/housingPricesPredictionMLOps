"""
Simple Pipeline Logger

MLOps Importance:
Logging is critical for automation because:
- Track what happened when things run automatically
- Debug issues without manual intervention
- Create audit trail for compliance
- Monitor pipeline health over time
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class PipelineLogger:
    """
    Simple logger for automated pipelines.

    Why Simple?
    - Easy to understand for beginners
    - Logs to both file and console
    - Timestamps every message
    - Different levels for different importance
    """

    def __init__(self, name: str = "pipeline", log_dir: str = "logs"):
        """
        Initialize the pipeline logger.

        Args:
            name: Name of the logger (appears in log messages)
            log_dir: Directory where log files are saved
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Remove existing handlers (avoid duplicates)
        self.logger.handlers = []

        # Create log filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"{name}_{timestamp}.log"

        # File handler (saves to file)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        # Console handler (prints to screen)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        # Format: timestamp - name - level - message
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self.log_file = log_file
        self.info(f"Pipeline logger initialized. Logging to: {log_file}")

    def debug(self, message: str):
        """Log debug message (detailed information for developers)"""
        self.logger.debug(message)

    def info(self, message: str):
        """Log info message (general information about progress)"""
        self.logger.info(message)

    def warning(self, message: str):
        """Log warning message (something unexpected but not critical)"""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message (something went wrong)"""
        self.logger.error(message)

    def critical(self, message: str):
        """Log critical message (severe error, pipeline might stop)"""
        self.logger.critical(message)

    def stage_start(self, stage_name: str):
        """
        Log the start of a pipeline stage.

        Example:
            logger.stage_start("Data Ingestion")
            # Output: ========== STAGE: Data Ingestion - STARTED ==========
        """
        separator = "=" * 60
        self.info(separator)
        self.info(f"STAGE: {stage_name} - STARTED")
        self.info(separator)

    def stage_end(self, stage_name: str, success: bool = True):
        """
        Log the end of a pipeline stage.

        Args:
            stage_name: Name of the stage
            success: Whether the stage completed successfully
        """
        status = "COMPLETED" if success else "FAILED"
        separator = "=" * 60
        self.info(separator)
        self.info(f"STAGE: {stage_name} - {status}")
        self.info(separator)

    def metric(self, name: str, value: float):
        """
        Log a metric (useful for tracking model performance).

        Example:
            logger.metric("RMSE", 48726.11)
            logger.metric("R2_Score", 0.82)
        """
        self.info(f"METRIC | {name}: {value}")

    def data_info(self, description: str, count: int):
        """
        Log data-related information.

        Example:
            logger.data_info("Total houses processed", 20640)
            logger.data_info("Training samples", 16512)
        """
        self.info(f"DATA | {description}: {count:,}")


# Simple example usage
if __name__ == "__main__":
    # Create logger
    logger = PipelineLogger(name="example")

    # Log different levels
    logger.info("Pipeline started")
    logger.debug("This is debug information (only in file)")
    logger.warning("This is a warning")

    # Log a stage
    logger.stage_start("Data Processing")
    logger.data_info("Rows processed", 1000)
    logger.stage_end("Data Processing", success=True)

    # Log metrics
    logger.metric("Accuracy", 0.85)
    logger.metric("RMSE", 45000.0)

    logger.info(f"Log saved to: {logger.log_file}")
