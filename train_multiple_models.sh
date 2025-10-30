#!/bin/bash
#
# Train Multiple Models for Comparison
#
# This script trains 3 different models and logs all to MLflow
# Then you can compare them in the MLflow UI

echo "======================================================================"
echo "TRAINING MULTIPLE MODELS FOR MLFLOW COMPARISON"
echo "======================================================================"
echo ""
echo "This will train 3 models with different settings:"
echo "  1. Random Forest with 100 trees"
echo "  2. Random Forest with 150 trees (already done)"
echo "  3. Random Forest with 200 trees"
echo ""
echo "All will be tracked in MLflow for easy comparison!"
echo ""

# Model 1: 100 trees
echo "▶ Training Model 1: 100 trees..."
sed -i.bak 's/n_estimators: [0-9]*/n_estimators: 100/' config/config.yaml
dvc repro -f > /dev/null 2>&1
echo "  ✓ Model 1 complete"

# Model 2: 150 trees (already done, but let's redo)
echo "▶ Training Model 2: 150 trees..."
sed -i.bak 's/n_estimators: [0-9]*/n_estimators: 150/' config/config.yaml
dvc repro -f > /dev/null 2>&1
echo "  ✓ Model 2 complete"

# Model 3: 200 trees
echo "▶ Training Model 3: 200 trees..."
sed -i.bak 's/n_estimators: [0-9]*/n_estimators: 200/' config/config.yaml
dvc repro -f > /dev/null 2>&1
echo "  ✓ Model 3 complete"

echo ""
echo "======================================================================"
echo "✓ ALL 3 MODELS TRAINED!"
echo "======================================================================"
echo ""
echo "View comparison in MLflow UI:"
echo "  1. Make sure MLflow UI is running: mlflow ui"
echo "  2. Open: http://localhost:5000"
echo "  3. Click 'Experiments' tab"
echo "  4. Select all 3 runs"
echo "  5. Click 'Compare'"
echo ""
echo "You'll see a side-by-side comparison of:"
echo "  • Parameters (100 vs 150 vs 200 trees)"
echo "  • Metrics (RMSE, R², MAE, MAPE)"
echo "  • Visual charts"
echo ""

# Restore to 150 (our best so far)
sed -i.bak 's/n_estimators: [0-9]*/n_estimators: 150/' config/config.yaml
rm config/config.yaml.bak

echo "Config restored to 150 trees"
