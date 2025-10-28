#!/bin/bash
#
# DVC-Based Data Watcher
#
# MLOps Pattern: Smart Change Detection with DVC
# DVC automatically detects which stages need to rerun based on:
# - Data file changes (checksums)
# - Code changes (file hashes)
# - Config changes (parameters)
#
# Advantage over manual watching:
# - Only reruns changed stages (not everything)
# - Built-in caching
# - Tracks dependencies automatically

echo "=========================================="
echo "DVC-BASED PIPELINE TRIGGER"
echo "=========================================="
echo ""
echo "Checking for changes in:"
echo "  • Data files"
echo "  • Configuration"
echo "  • Code"
echo ""

# Check if DVC is installed
if ! command -v dvc &> /dev/null; then
    echo "❌ DVC not installed"
    echo "Install with: pip install dvc"
    exit 1
fi

# Initialize DVC if not already done
if [ ! -d ".dvc" ]; then
    echo "Initializing DVC..."
    dvc init
    git add .dvc .dvcignore
    git commit -m "Initialize DVC"
fi

# Run DVC pipeline
echo "Running DVC pipeline (only changed stages will run)..."
echo ""

dvc repro

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✓ Pipeline completed successfully"
    echo "=========================================="

    # Show what was run
    echo ""
    echo "To see what changed:"
    echo "  dvc status"
    echo ""
    echo "To see metrics:"
    echo "  dvc metrics show"

else
    echo ""
    echo "=========================================="
    echo "✗ Pipeline failed"
    echo "=========================================="
    exit 1
fi
