#!/bin/bash
#
# Start Apache Airflow for Housing Price ML Pipeline
#
# This script starts the Airflow webserver and scheduler

echo "======================================================================"
echo "STARTING APACHE AIRFLOW"
echo "======================================================================"
echo ""

# Activate virtual environment
source .venv_airflow/bin/activate

# Set AIRFLOW_HOME
export AIRFLOW_HOME=$PWD/airflow
export HOUSING_PIPELINE_ROOT=$PWD

echo "✓ Virtual environment activated"
echo "✓ AIRFLOW_HOME: $AIRFLOW_HOME"
echo "✓ Project root: $HOUSING_PIPELINE_ROOT"
echo ""

# Check if Airflow is already running
if lsof -ti:8080 > /dev/null 2>&1; then
    echo "⚠️  Airflow webserver is already running on port 8080"
    echo ""
    read -p "Do you want to kill it and restart? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Stopping existing Airflow processes..."
        pkill -f "airflow webserver"
        pkill -f "airflow scheduler"
        sleep 2
    else
        echo "Exiting..."
        exit 0
    fi
fi

# Start Airflow webserver in background
echo "🚀 Starting Airflow webserver..."
airflow webserver --port 8080 > airflow/logs/webserver.log 2>&1 &
WEBSERVER_PID=$!
echo "   PID: $WEBSERVER_PID"

# Wait a moment
sleep 2

# Start Airflow scheduler in background
echo "🚀 Starting Airflow scheduler..."
airflow scheduler > airflow/logs/scheduler.log 2>&1 &
SCHEDULER_PID=$!
echo "   PID: $SCHEDULER_PID"

echo ""
echo "======================================================================"
echo "✅ AIRFLOW STARTED SUCCESSFULLY!"
echo "======================================================================"
echo ""
echo "Access Airflow UI:"
echo "  • URL: http://localhost:8080"
echo "  • Username: admin"
echo "  • Password: admin"
echo ""
echo "Your ML Pipeline DAG:"
echo "  • DAG ID: housing_price_ml_pipeline"
echo "  • Location: $AIRFLOW_HOME/dags/housing_ml_pipeline.py"
echo ""
echo "Process IDs:"
echo "  • Webserver PID: $WEBSERVER_PID"
echo "  • Scheduler PID: $SCHEDULER_PID"
echo ""
echo "Logs:"
echo "  • Webserver: airflow/logs/webserver.log"
echo "  • Scheduler: airflow/logs/scheduler.log"
echo ""
echo "To stop Airflow:"
echo "  pkill -f 'airflow webserver'"
echo "  pkill -f 'airflow scheduler'"
echo ""
echo "Or use: bash stop_airflow.sh"
echo ""
echo "======================================================================"
echo "⏳ Waiting for Airflow to be ready..."
echo "   (This may take 30-60 seconds)"
echo "======================================================================"
echo ""

# Wait for Airflow to be ready
for i in {1..30}; do
    if curl -s http://localhost:8080/health > /dev/null 2>&1; then
        echo "✅ Airflow is ready!"
        echo ""
        echo "🎉 Open http://localhost:8080 in your browser!"
        echo ""
        exit 0
    fi
    echo -n "."
    sleep 2
done

echo ""
echo "⚠️  Airflow is taking longer than expected to start."
echo "   Check the logs:"
echo "   tail -f airflow/logs/webserver.log"
echo "   tail -f airflow/logs/scheduler.log"