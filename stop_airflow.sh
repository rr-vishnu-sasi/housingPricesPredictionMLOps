#!/bin/bash
#
# Stop Apache Airflow

echo "======================================================================"
echo "STOPPING APACHE AIRFLOW"
echo "======================================================================"
echo ""

# Kill Airflow processes
echo "Stopping Airflow webserver..."
pkill -f "airflow webserver"

echo "Stopping Airflow scheduler..."
pkill -f "airflow scheduler"

sleep 2

# Check if processes are still running
if lsof -ti:8080 > /dev/null 2>&1; then
    echo "⚠️  Warning: Port 8080 is still in use"
else
    echo "✅ Airflow stopped successfully!"
fi

echo ""