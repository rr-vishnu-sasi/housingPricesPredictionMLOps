#!/bin/bash
#
# Push Docker Image to Docker Hub
#

echo "══════════════════════════════════════════════════════════════════"
echo "🐳 Push to Docker Hub"
echo "══════════════════════════════════════════════════════════════════"
echo ""

# Configuration
DOCKERHUB_USERNAME="${DOCKERHUB_USERNAME:-your-dockerhub-username}"
IMAGE_NAME="housing-price-predictor"
TAG="${1:-latest}"

echo "📦 Image: $IMAGE_NAME:$TAG"
echo "👤 Docker Hub User: $DOCKERHUB_USERNAME"
echo ""

# Check if logged in to Docker Hub
if ! docker info | grep -q "Username"; then
    echo "⚠️  Not logged in to Docker Hub"
    echo ""
    read -p "Do you want to login now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker login
        if [ $? -ne 0 ]; then
            echo "❌ Login failed!"
            exit 1
        fi
    else
        echo "❌ Must be logged in to push. Run: docker login"
        exit 1
    fi
fi

# Tag image for Docker Hub
DOCKERHUB_IMAGE="$DOCKERHUB_USERNAME/$IMAGE_NAME:$TAG"

echo "🏷️  Tagging image..."
docker tag $IMAGE_NAME:$TAG $DOCKERHUB_IMAGE

if [ $? -ne 0 ]; then
    echo "❌ Tagging failed! Make sure image exists:"
    echo "   docker images | grep $IMAGE_NAME"
    exit 1
fi

# Push to Docker Hub
echo "📤 Pushing to Docker Hub..."
echo "   This may take a few minutes..."
echo ""

docker push $DOCKERHUB_IMAGE

if [ $? -eq 0 ]; then
    echo ""
    echo "══════════════════════════════════════════════════════════════════"
    echo "✅ Successfully Pushed to Docker Hub!"
    echo "══════════════════════════════════════════════════════════════════"
    echo ""
    echo "📦 Image: $DOCKERHUB_IMAGE"
    echo ""
    echo "🌐 View on Docker Hub:"
    echo "   https://hub.docker.com/r/$DOCKERHUB_USERNAME/$IMAGE_NAME"
    echo ""
    echo "🚀 Others can pull with:"
    echo "   docker pull $DOCKERHUB_IMAGE"
    echo ""
    echo "🎯 Run on any machine:"
    echo "   docker run -p 5000:5000 $DOCKERHUB_IMAGE"
    echo ""
else
    echo "❌ Push failed!"
    exit 1
fi
