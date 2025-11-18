#!/bin/bash
#
# Run Housing Price Prediction API with Docker Compose
#

echo "══════════════════════════════════════════════════════════════════"
echo "🐳 Starting ML API with Docker Compose"
echo "══════════════════════════════════════════════════════════════════"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "   Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Build and start services
echo "🔨 Building and starting services..."
echo "   - Redis Cache"
echo "   - ML API (Flask + Gunicorn)"
echo ""

docker-compose up --build -d

if [ $? -eq 0 ]; then
    echo ""
    echo "══════════════════════════════════════════════════════════════════"
    echo "✅ Services Started!"
    echo "══════════════════════════════════════════════════════════════════"
    echo ""

    # Wait for services to be healthy
    echo "⏳ Waiting for services to be ready..."
    sleep 5

    # Check status
    echo ""
    docker-compose ps

    echo ""
    echo "══════════════════════════════════════════════════════════════════"
    echo "🌐 Access Points"
    echo "══════════════════════════════════════════════════════════════════"
    echo ""
    echo "ML API:"
    echo "   http://localhost:5000"
    echo ""
    echo "Health Check:"
    echo "   curl http://localhost:5000/health"
    echo ""
    echo "Test Prediction:"
    echo "   curl -X POST http://localhost:5000/predict \\"
    echo "     -H 'Content-Type: application/json' \\"
    echo "     -d '{\"median_income\":8.3,\"housing_median_age\":41,\"total_rooms\":880,\"total_bedrooms\":129,\"population\":322,\"households\":126,\"latitude\":37.88,\"longitude\":-122.23,\"ocean_proximity\":\"NEAR BAY\"}'"
    echo ""
    echo "══════════════════════════════════════════════════════════════════"
    echo "📊 Useful Commands"
    echo "══════════════════════════════════════════════════════════════════"
    echo ""
    echo "View logs:"
    echo "   docker-compose logs -f ml-api"
    echo "   docker-compose logs -f redis"
    echo ""
    echo "Stop services:"
    echo "   docker-compose down"
    echo ""
    echo "Rebuild:"
    echo "   docker-compose up --build"
    echo ""
else
    echo "❌ Failed to start services!"
    exit 1
fi
