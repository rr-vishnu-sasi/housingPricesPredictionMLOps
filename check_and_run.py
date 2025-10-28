"""
Scheduled Data Check and Pipeline Trigger

MLOps Pattern: Scheduled Event-Driven Pipeline
- Runs on schedule (e.g., hourly via cron)
- Checks if data changed since last run
- Only runs pipeline if data actually changed
- Logs when pipeline was skipped vs run

Best for:
- Production environments
- Scheduled retraining (daily, weekly)
- Integration with orchestration tools (Airflow, etc.)
"""

import sys
import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline_logger import PipelineLogger


class ScheduledDataChecker:
    """
    Checks data and runs pipeline only if changed.

    State file tracks last known data state.
    If data unchanged → skip pipeline (save time & money!)
    If data changed → run pipeline
    """

    def __init__(self, state_file: str = "logs/pipeline_state.json"):
        """
        Initialize checker.

        Args:
            state_file: Where to store last known state
        """
        self.state_file = Path(state_file)
        self.logger = PipelineLogger(name="scheduled_checker")
        self.state_file.parent.mkdir(exist_ok=True)

    def _load_state(self) -> dict:
        """Load last known state from file."""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_state(self, state: dict):
        """Save current state to file."""
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=4)

    def _calculate_hash(self, filepath: Path) -> str:
        """Calculate file hash."""
        if not filepath.exists():
            return None

        md5 = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5.update(chunk)
        return md5.hexdigest()

    def check_and_run(self, data_path: str = "data/raw/housing_data.csv") -> bool:
        """
        Check if data changed and run pipeline if needed.

        Args:
            data_path: Path to data file to check

        Returns:
            bool: True if pipeline was run, False if skipped
        """
        self.logger.info("=" * 60)
        self.logger.info("SCHEDULED DATA CHECK")
        self.logger.info("=" * 60)
        self.logger.info(f"Check time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Load last known state
        state = self._load_state()
        last_hash = state.get('data_hash')
        last_run = state.get('last_run')

        self.logger.info(f"Last pipeline run: {last_run if last_run else 'Never'}")

        # Calculate current data hash
        data_file = Path(data_path)
        if not data_file.exists():
            self.logger.warning(f"Data file not found: {data_path}")
            return False

        current_hash = self._calculate_hash(data_file)
        self.logger.info(f"Current data hash: {current_hash[:16]}...")

        # Check if changed
        if current_hash == last_hash:
            # NO CHANGE - Skip pipeline!
            self.logger.info("✓ Data unchanged - skipping pipeline (saves time!)")
            self.logger.info(f"   Last hash: {last_hash[:16]}...")
            self.logger.info(f"   Current:   {current_hash[:16]}...")

            # Update state with check time
            state['last_check'] = datetime.now().isoformat()
            self._save_state(state)

            return False

        # DATA CHANGED - Run pipeline!
        self.logger.info("🔔 DATA CHANGED - triggering pipeline!")

        if last_hash:
            self.logger.info(f"   Old hash: {last_hash[:16]}...")
        else:
            self.logger.info("   (First run - no previous hash)")

        self.logger.info(f"   New hash: {current_hash[:16]}...")

        # Run pipeline
        self.logger.info("")
        self.logger.info("Starting pipeline...")

        try:
            result = subprocess.run(
                [sys.executable, "run_automated_pipeline.py"],
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode == 0:
                self.logger.info("✓ Pipeline completed successfully")

                # Update state
                state.update({
                    'data_hash': current_hash,
                    'last_run': datetime.now().isoformat(),
                    'last_check': datetime.now().isoformat(),
                    'status': 'success'
                })
                self._save_state(state)

                return True

            else:
                self.logger.error(f"✗ Pipeline failed (exit code {result.returncode})")

                # Update state (but keep old hash since pipeline failed)
                state.update({
                    'last_check': datetime.now().isoformat(),
                    'status': 'failed',
                    'error': result.stderr[:500] if result.stderr else None
                })
                self._save_state(state)

                return False

        except Exception as e:
            self.logger.error(f"✗ Error running pipeline: {str(e)}")
            return False


def main():
    """
    Main entry point.

    Use this script with cron:
    # Check every hour
    0 * * * * cd /path/to/project && python check_and_run.py
    """
    print("=" * 70)
    print("SCHEDULED DATA CHECK & PIPELINE TRIGGER")
    print("=" * 70)
    print(f"\nCurrent time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nChecking if data changed since last run...")
    print("(If unchanged, pipeline will be skipped)\n")

    checker = ScheduledDataChecker()
    was_run = checker.check_and_run()

    if was_run:
        print("\n✓ Pipeline was triggered and completed")
        sys.exit(0)
    else:
        print("\n○ Pipeline was skipped (data unchanged)")
        sys.exit(0)


if __name__ == "__main__":
    main()
