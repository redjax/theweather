#!/bin/bash

# Container build helper script
# This script helps build containers with proper requirements export

set -e

APP_NAME=${1:-"weatherapi-collector"}
BUILD_CONTEXT="../../"

echo "Building container for $APP_NAME..."

case $APP_NAME in
    "weatherapi-collector")
        APP_DIR="collectors/weatherapi-collector"
        CONTAINER_DIR="containers/weatherapi-collector"
        ;;
    "api-server")
        APP_DIR="servers/api-server"
        CONTAINER_DIR="containers/api-server"
        ;;
    *)
        echo "Unknown app: $APP_NAME"
        echo "Usage: $0 [weatherapi-collector|api-server]"
        exit 1
        ;;
esac

echo "Building container for $APP_NAME from $APP_DIR..."

# Change to the container directory
cd "$CONTAINER_DIR"

# Build the container
docker build -t "$APP_NAME:latest" -f Dockerfile "$BUILD_CONTEXT"

echo "✓ Container $APP_NAME:latest built successfully!"
echo ""
echo "To run the container:"
echo "  docker run --rm $APP_NAME:latest"
echo ""
echo "Or use docker-compose:"
echo "  cd $CONTAINER_DIR && docker-compose up"