#!/bin/bash
#
# Build Docker Image for Housing Price Prediction API
#

echo "══════════════════════════════════════════════════════════════════"
echo "🐳 Building Docker Image"
echo "══════════════════════════════════════════════════════════════════"
echo ""

# Image name and tag
IMAGE_NAME="housing-price-predictor"
TAG="${1:-latest}"
FULL_IMAGE="$IMAGE_NAME:$TAG"

echo "📦 Image: $FULL_IMAGE"
echo ""

# Build with multi-stage Dockerfile
echo "🔨 Building image (this may take 2-3 minutes)..."
echo ""

docker build \
    -t $FULL_IMAGE \
    --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
    --build-arg VERSION="$TAG" \
    .

if [ $? -eq 0 ]; then
    echo ""
    echo "══════════════════════════════════════════════════════════════════"
    echo "✅ Image Built Successfully!"
    echo "══════════════════════════════════════════════════════════════════"
    echo ""
    echo "📦 Image: $FULL_IMAGE"

    # Show image size
    SIZE=$(docker images $IMAGE_NAME:$TAG --format "{{.Size}}")
    echo "💾 Size: $SIZE"
    echo ""

    echo "🚀 Next Steps:"
    echo "   1. Run with Docker Compose: docker-compose up"
    echo "   2. Or run standalone: docker run -p 5000:5000 $FULL_IMAGE"
    echo "   3. Test API: curl http://localhost:5000"
    echo ""
else
    echo ""
    echo "❌ Build failed! Check errors above."
    exit 1
fi
