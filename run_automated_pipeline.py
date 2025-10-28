"""
Automated Pipeline Runner

This script orchestrates the entire ML pipeline automatically.

MLOps Automation Benefits:
- Runs multiple stages in sequence
- Handles errors gracefully
- Logs everything
- Can be scheduled (cron, Airflow, etc.)
- Consistent execution every time
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline_logger import PipelineLogger


class AutomatedPipeline:
    """
    Orchestrates the ML pipeline stages.

    Think of this as a conductor leading an orchestra:
    - Each stage is an instrument
    - The conductor ensures they play in the right order
    - If one fails, the concert stops
    """

    def __init__(self):
        """Initialize the automated pipeline."""
        self.logger = PipelineLogger(name="automated_pipeline")
        self.stages = [
            {
                'name': 'Data Ingestion',
                'script': 'pipeline/stage_01_ingest_data.py',
                'description': 'Fetch and validate data'
            },
            {
                'name': 'Feature Engineering',
                'script': 'pipeline/stage_02_feature_engineering.py',
                'description': 'Transform data into features'
            },
            {
                'name': 'Model Training',
                'script': 'pipeline/stage_03_train_model.py',
                'description': 'Train and evaluate model'
            }
        ]

    def run_stage(self, stage: dict) -> bool:
        """
        Run a single pipeline stage.

        How it works:
        1. Logs that stage is starting
        2. Runs the Python script
        3. Captures output
        4. Returns success/failure

        Args:
            stage: Dictionary with stage information

        Returns:
            bool: True if successful, False otherwise
        """
        self.logger.info("")
        self.logger.stage_start(stage['name'])
        self.logger.info(f"Description: {stage['description']}")
        self.logger.info(f"Running: python {stage['script']}")

        try:
            # Run the stage script
            result = subprocess.run(
                [sys.executable, stage['script']],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            # Check if successful (exit code 0 = success)
            if result.returncode == 0:
                self.logger.stage_end(stage['name'], success=True)
                return True
            else:
                self.logger.error(f"Stage failed with exit code: {result.returncode}")
                if result.stderr:
                    self.logger.error(f"Error output: {result.stderr}")
                self.logger.stage_end(stage['name'], success=False)
                return False

        except subprocess.TimeoutExpired:
            self.logger.error("Stage timed out after 5 minutes")
            self.logger.stage_end(stage['name'], success=False)
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            self.logger.stage_end(stage['name'], success=False)
            return False

    def run(self) -> bool:
        """
        Run the entire pipeline (all stages in sequence).

        Pipeline Logic:
        - Run stages in order: 1 → 2 → 3
        - If stage fails, stop (don't run next stages)
        - Log overall success/failure

        Returns:
            bool: True if all stages successful, False otherwise
        """
        start_time = datetime.now()

        self.logger.info("=" * 70)
        self.logger.info("AUTOMATED ML PIPELINE - STARTED")
        self.logger.info("=" * 70)
        self.logger.info(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"Total stages: {len(self.stages)}")

        # Run each stage
        for i, stage in enumerate(self.stages, 1):
            self.logger.info(f"\n>>> Stage {i}/{len(self.stages)}: {stage['name']}")

            success = self.run_stage(stage)

            if not success:
                self.logger.error(f"Pipeline FAILED at stage: {stage['name']}")
                self.logger.info("Stopping pipeline (remaining stages not executed)")
                return False

        # All stages completed successfully
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("AUTOMATED ML PIPELINE - COMPLETED SUCCESSFULLY")
        self.logger.info("=" * 70)
        self.logger.info(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"Total duration: {duration:.2f} seconds")
        self.logger.info(f"All {len(self.stages)} stages completed")

        self.logger.info("\n📊 Pipeline Summary:")
        for i, stage in enumerate(self.stages, 1):
            self.logger.info(f"  ✓ Stage {i}: {stage['name']}")

        self.logger.info("\n🎉 Pipeline finished! Check the logs for details.")
        self.logger.info(f"   Log file: {self.logger.log_file}")

        return True


def main():
    """
    Main entry point for automated pipeline.
    """
    print("\n" + "=" * 70)
    print("AUTOMATED ML PIPELINE")
    print("=" * 70)
    print("\nThis will run all pipeline stages automatically:")
    print("  1. Data Ingestion")
    print("  2. Feature Engineering")
    print("  3. Model Training")
    print("\nStarting in 3 seconds...")

    import time
    time.sleep(3)

    # Create and run pipeline
    pipeline = AutomatedPipeline()
    success = pipeline.run()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
