#!/bin/bash
#
# Complete MLOps Pipeline Runner
# Runs: DVC + MLflow + Airflow Integration
#

echo "══════════════════════════════════════════════════════════════════"
echo "🚀 COMPLETE MLOPS PIPELINE - DVC + MLflow + Airflow"
echo "══════════════════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$PWD"

# ============================================================================
# STEP 1: Check Services Status
# ============================================================================
echo -e "${BLUE}📊 Step 1: Checking Services Status...${NC}"
echo ""

# Check MLflow
if lsof -ti:5000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ MLflow UI: Running on http://localhost:5000${NC}"
else
    echo -e "${YELLOW}⚠️  MLflow UI: Not running${NC}"
    echo "   Starting MLflow..."
    mlflow ui --backend-store-uri file:./logs/mlruns &
    sleep 3
    echo -e "${GREEN}   ✅ MLflow started!${NC}"
fi

# Check Airflow
if lsof -ti:8080 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Airflow UI: Running on http://localhost:8080${NC}"
else
    echo -e "${YELLOW}⚠️  Airflow UI: Not running${NC}"
    echo "   Please run: bash start_airflow.sh"
    exit 1
fi

echo ""

# ============================================================================
# STEP 2: Show Current Project Status
# ============================================================================
echo -e "${BLUE}📁 Step 2: Current Project Status${NC}"
echo ""

# Show DVC status
echo -e "${YELLOW}DVC Pipeline Status:${NC}"
if [ -f "dvc.lock" ]; then
    echo "  ✓ DVC pipeline defined (dvc.yaml)"
    echo "  ✓ DVC lockfile exists (dvc.lock)"
    echo "  Stages:"
    echo "    • ingest_data"
    echo "    • feature_engineering"
    echo "    • train_model"
else
    echo "  ⚠️  DVC not initialized"
fi

echo ""

# Show MLflow experiments
echo -e "${YELLOW}MLflow Experiments:${NC}"
if [ -d "logs/mlruns" ]; then
    EXPERIMENTS=$(find logs/mlruns -name "meta.yaml" | wc -l | tr -d ' ')
    echo "  ✓ Tracking URI: file:./logs/mlruns"
    echo "  ✓ Experiments tracked: $EXPERIMENTS"
else
    echo "  No experiments yet"
fi

echo ""

# Show Airflow DAGs
echo -e "${YELLOW}Airflow DAGs:${NC}"
if [ -f "airflow/dags/housing_ml_pipeline.py" ]; then
    echo "  ✓ DAG: housing_price_ml_pipeline"
    echo "  ✓ Schedule: @daily (every midnight)"
else
    echo "  ⚠️  DAG not found"
fi

echo ""
echo "══════════════════════════════════════════════════════════════════"
echo ""

# ============================================================================
# STEP 3: Choose Execution Mode
# ============================================================================
echo -e "${BLUE}🎯 Step 3: Choose How to Run Pipeline${NC}"
echo ""
echo "You have 3 options:"
echo ""
echo "  1) 🔧 Manual DVC Run (Development)"
echo "     • Fast with caching"
echo "     • Good for testing"
echo "     • Command: dvc repro"
echo ""
echo "  2) 🤖 Airflow Trigger (Production Style)"
echo "     • Full monitoring"
echo "     • Scheduled automation"
echo "     • Uses Airflow UI"
echo ""
echo "  3) 🚀 Full Integration (DVC via Airflow)"
echo "     • Best of both worlds"
echo "     • DVC caching + Airflow monitoring"
echo "     • Requires modified DAG"
echo ""

read -p "Choose option (1/2/3) or 'q' to quit: " choice

case $choice in
    1)
        echo ""
        echo "══════════════════════════════════════════════════════════════════"
        echo -e "${GREEN}🔧 Running Manual DVC Pipeline...${NC}"
        echo "══════════════════════════════════════════════════════════════════"
        echo ""

        # Run DVC pipeline
        dvc repro -v

        echo ""
        echo "══════════════════════════════════════════════════════════════════"
        echo -e "${GREEN}✅ DVC Pipeline Complete!${NC}"
        echo "══════════════════════════════════════════════════════════════════"
        echo ""
        echo "📊 Check Results:"
        echo "  • MLflow UI: http://localhost:5000"
        echo "  • Evaluation: cat logs/evaluation_report.json"
        echo "  • Model Registry: cat models/model_registry/registry.json"
        ;;

    2)
        echo ""
        echo "══════════════════════════════════════════════════════════════════"
        echo -e "${GREEN}🤖 Triggering Airflow Pipeline...${NC}"
        echo "══════════════════════════════════════════════════════════════════"
        echo ""
        echo "To trigger via UI:"
        echo "  1. Open: http://localhost:8080"
        echo "  2. Login: admin/admin"
        echo "  3. Find: housing_price_ml_pipeline"
        echo "  4. Enable toggle switch"
        echo "  5. Click ▶️ play button → Trigger DAG"
        echo ""
        echo "To trigger via CLI:"

        source .venv_airflow/bin/activate
        export AIRFLOW_HOME=$PWD/airflow

        echo "  Running: airflow dags trigger housing_price_ml_pipeline"
        airflow dags trigger housing_price_ml_pipeline

        echo ""
        echo -e "${GREEN}✅ Pipeline Triggered!${NC}"
        echo ""
        echo "📊 Monitor Progress:"
        echo "  • Airflow UI: http://localhost:8080"
        echo "  • Click DAG → Graph view"
        echo "  • Watch tasks turn green!"
        echo ""
        echo "  After completion, check:"
        echo "  • MLflow UI: http://localhost:5000"
        ;;

    3)
        echo ""
        echo "══════════════════════════════════════════════════════════════════"
        echo -e "${GREEN}🚀 Full Integration Mode${NC}"
        echo "══════════════════════════════════════════════════════════════════"
        echo ""
        echo "This requires creating a hybrid DAG that uses DVC."
        echo ""
        echo "See: INTEGRATION_GUIDE.md for implementation details"
        echo ""
        echo "Quick setup:"
        echo "  1. Create: airflow/dags/housing_ml_pipeline_dvc.py"
        echo "  2. Use BashOperator: dvc repro"
        echo "  3. Add Airflow validation tasks"
        echo ""
        ;;

    q|Q)
        echo "Exiting..."
        exit 0
        ;;

    *)
        echo "Invalid option!"
        exit 1
        ;;
esac

echo ""
echo "══════════════════════════════════════════════════════════════════"
echo -e "${BLUE}📊 Quick Status Check${NC}"
echo "══════════════════════════════════════════════════════════════════"
echo ""
echo "Open these URLs to monitor:"
echo ""
echo "  🤖 Airflow Dashboard:"
echo "     http://localhost:8080"
echo "     (Username: admin, Password: admin)"
echo ""
echo "  📊 MLflow Experiments:"
echo "     http://localhost:5000"
echo ""
echo "  📁 Local Files:"
echo "     • Evaluation Report: logs/evaluation_report.json"
echo "     • Model Registry: models/model_registry/registry.json"
echo "     • Data Quality: logs/data_quality_report.json"
echo ""
echo "══════════════════════════════════════════════════════════════════"
echo -e "${GREEN}🎉 All Systems Ready!${NC}"
echo "══════════════════════════════════════════════════════════════════"
