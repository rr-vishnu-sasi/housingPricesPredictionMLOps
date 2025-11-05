#!/bin/bash
#
# Quick Status Checker for All MLOps Services
#

echo "══════════════════════════════════════════════════════════════════"
echo "🔍 MLOps Services Status Check"
echo "══════════════════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check MLflow
echo -n "MLflow UI (port 5000): "
if lsof -ti:5000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ RUNNING${NC}"
    echo "  → http://localhost:5000"
else
    echo -e "${RED}❌ NOT RUNNING${NC}"
    echo "  Start with: mlflow ui"
fi

echo ""

# Check Airflow Webserver
echo -n "Airflow Webserver (port 8080): "
if lsof -ti:8080 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ RUNNING${NC}"
    echo "  → http://localhost:8080"
    echo "  Login: admin/admin"
else
    echo -e "${RED}❌ NOT RUNNING${NC}"
    echo "  Start with: bash start_airflow.sh"
fi

echo ""

# Check Airflow Scheduler
echo -n "Airflow Scheduler: "
if pgrep -f "airflow scheduler" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ RUNNING${NC}"
else
    echo -e "${RED}❌ NOT RUNNING${NC}"
fi

echo ""
echo "══════════════════════════════════════════════════════════════════"
echo "📊 Project Status"
echo "══════════════════════════════════════════════════════════════════"
echo ""

# Check DVC
if [ -f "dvc.yaml" ]; then
    echo -e "${GREEN}✅ DVC${NC} - Pipeline defined"
    echo "  Run with: dvc repro"
else
    echo -e "${YELLOW}⚠️  DVC${NC} - Not configured"
fi

echo ""

# Check latest model
if [ -d "models/saved_models" ] && [ "$(ls -A models/saved_models)" ]; then
    LATEST_MODEL=$(ls -t models/saved_models/*.joblib 2>/dev/null | head -1)
    if [ -n "$LATEST_MODEL" ]; then
        echo -e "${GREEN}✅ Latest Model${NC}: $(basename $LATEST_MODEL)"
        echo "  Modified: $(stat -f %Sm -t "%Y-%m-%d %H:%M" "$LATEST_MODEL" 2>/dev/null || stat -c %y "$LATEST_MODEL" 2>/dev/null | cut -d' ' -f1-2)"
    fi
else
    echo -e "${YELLOW}⚠️  No models${NC} - Run pipeline first"
fi

echo ""

# Check latest evaluation
if [ -f "logs/evaluation_report.json" ]; then
    echo -e "${GREEN}✅ Latest Evaluation${NC}:"
    R2=$(grep -o '"r2_score": [0-9.]*' logs/evaluation_report.json | grep -o '[0-9.]*')
    RMSE=$(grep -o '"rmse": [0-9.]*' logs/evaluation_report.json | grep -o '[0-9.]*')
    if [ -n "$R2" ] && [ -n "$RMSE" ]; then
        echo "  R² Score: $R2"
        echo "  RMSE: \$$(printf "%.0f" $RMSE)"
    fi
else
    echo -e "${YELLOW}⚠️  No evaluation${NC} - Run pipeline first"
fi

echo ""
echo "══════════════════════════════════════════════════════════════════"
echo "🚀 Quick Actions"
echo "══════════════════════════════════════════════════════════════════"
echo ""
echo "Run complete pipeline:"
echo "  bash run_complete_pipeline.sh"
echo ""
echo "Start all services:"
echo "  bash start_airflow.sh    # Starts Airflow"
echo "  mlflow ui                # Starts MLflow"
echo ""
echo "Stop services:"
echo "  bash stop_airflow.sh"
echo "  pkill -f 'mlflow ui'"
echo ""
