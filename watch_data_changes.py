"""
Data Change Watcher - Automatic Pipeline Trigger

MLOps Pattern: Event-Driven Pipeline
- Watches for changes in data files
- Automatically triggers pipeline when data changes
- Prevents unnecessary reruns (only when data actually changes)

Use Cases:
- Daily data drops from upstream systems
- Manual data updates
- Automated data collection processes
"""

import sys
import time
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.pipeline_logger import PipelineLogger


class DataWatcher:
    """
    Watches data files for changes and triggers pipeline.

    How it works:
    1. Calculates hash (fingerprint) of data files
    2. Checks periodically if hash changed
    3. If changed → triggers pipeline
    4. If not changed → skips (no unnecessary work!)
    """

    def __init__(self, watch_paths: list, check_interval: int = 60):
        """
        Initialize data watcher.

        Args:
            watch_paths: List of file paths to watch
            check_interval: How often to check (seconds)
        """
        self.watch_paths = [Path(p) for p in watch_paths]
        self.check_interval = check_interval
        self.logger = PipelineLogger(name="data_watcher")
        self.file_hashes = {}

        # Calculate initial hashes
        self._update_hashes()

    def _calculate_hash(self, filepath: Path) -> str:
        """
        Calculate MD5 hash of a file.

        Hash = unique fingerprint of file contents
        If file changes even 1 byte, hash changes completely!

        Args:
            filepath: Path to file

        Returns:
            Hash string (e.g., "5d41402abc4b2a76b9719d911017c592")
        """
        if not filepath.exists():
            return None

        md5 = hashlib.md5()
        with open(filepath, 'rb') as f:
            # Read in chunks (efficient for large files)
            for chunk in iter(lambda: f.read(4096), b""):
                md5.update(chunk)
        return md5.hexdigest()

    def _update_hashes(self):
        """Update stored hashes for all watched files."""
        for path in self.watch_paths:
            if path.exists():
                self.file_hashes[str(path)] = self._calculate_hash(path)
                self.logger.info(f"Watching: {path} (hash: {self.file_hashes[str(path)][:8]}...)")
            else:
                self.logger.warning(f"File not found: {path}")

    def _check_for_changes(self) -> list:
        """
        Check if any watched files changed.

        Returns:
            List of changed file paths
        """
        changed_files = []

        for path in self.watch_paths:
            if not path.exists():
                continue

            current_hash = self._calculate_hash(path)
            old_hash = self.file_hashes.get(str(path))

            if current_hash != old_hash:
                changed_files.append(path)
                self.logger.info(f"🔔 CHANGE DETECTED: {path}")
                self.logger.info(f"   Old hash: {old_hash[:8] if old_hash else 'None'}...")
                self.logger.info(f"   New hash: {current_hash[:8]}...")

        return changed_files

    def _trigger_pipeline(self):
        """
        Trigger the ML pipeline.

        Runs: python run_automated_pipeline.py
        """
        self.logger.info("=" * 60)
        self.logger.info("TRIGGERING PIPELINE (data changed)")
        self.logger.info("=" * 60)

        try:
            # Run pipeline
            result = subprocess.run(
                [sys.executable, "run_automated_pipeline.py"],
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )

            if result.returncode == 0:
                self.logger.info("✓ Pipeline completed successfully")

                # Update hashes after successful run
                self._update_hashes()

                return True
            else:
                self.logger.error(f"✗ Pipeline failed with exit code {result.returncode}")
                if result.stderr:
                    self.logger.error(f"Error: {result.stderr[:500]}")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error("✗ Pipeline timed out after 10 minutes")
            return False
        except Exception as e:
            self.logger.error(f"✗ Pipeline failed: {str(e)}")
            return False

    def watch(self, run_on_start: bool = False):
        """
        Start watching for data changes.

        Args:
            run_on_start: If True, run pipeline immediately on start
        """
        self.logger.info("=" * 60)
        self.logger.info("DATA WATCHER STARTED")
        self.logger.info("=" * 60)
        self.logger.info(f"Watching {len(self.watch_paths)} files")
        self.logger.info(f"Check interval: {self.check_interval} seconds")

        if run_on_start:
            self.logger.info("Running pipeline on startup...")
            self._trigger_pipeline()

        self.logger.info("\n👀 Watching for changes... (Press Ctrl+C to stop)")

        try:
            check_count = 0
            while True:
                check_count += 1

                # Check for changes
                changed_files = self._check_for_changes()

                if changed_files:
                    # Data changed! Trigger pipeline
                    self.logger.info(f"\n🚀 Data changed in {len(changed_files)} file(s)")
                    self._trigger_pipeline()
                else:
                    # No changes
                    if check_count % 10 == 0:  # Log every 10 checks
                        self.logger.info(f"No changes detected (check #{check_count})")

                # Wait before next check
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            self.logger.info("\n" + "=" * 60)
            self.logger.info("DATA WATCHER STOPPED (user interrupted)")
            self.logger.info("=" * 60)
            self.logger.info(f"Total checks performed: {check_count}")


def main():
    """
    Main entry point for data watcher.
    """
    print("\n" + "=" * 70)
    print("DATA CHANGE WATCHER - Automatic Pipeline Trigger")
    print("=" * 70)
    print("\nThis will watch data files and automatically run the pipeline")
    print("when changes are detected.")
    print("\nWatching:")
    print("  • data/raw/housing_data.csv")
    print("  • config/config.yaml")
    print("\nPress Ctrl+C to stop\n")

    # Files to watch
    watch_files = [
        "data/raw/housing_data.csv",    # Raw data
        "config/config.yaml",            # Configuration
        # Add more files to watch:
        # "data/incoming/new_data.csv",
    ]

    # Create watcher
    watcher = DataWatcher(
        watch_paths=watch_files,
        check_interval=30  # Check every 30 seconds
    )

    # Start watching
    watcher.watch(run_on_start=False)  # Set to True to run immediately


if __name__ == "__main__":
    main()
