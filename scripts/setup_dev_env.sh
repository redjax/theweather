#!/bin/bash

# Development setup script for theweather monorepo
# This script sets up isolated virtual environments for each package

set -e

echo "Setting up theweather monorepo development environment..."

# Define package directories
PACKAGES=(
    "shared"
    "collectors/weatherapi-collector"
    "collectors/openmeteo-collector"
    "servers/api-server"
)

# Function to setup a package
setup_package() {
    local package_dir=$1
    echo "Setting up $package_dir..."
    
    cd "$package_dir"
    
    # Create isolated virtual environment and install dependencies
    uv sync --isolated
    
    echo "✓ $package_dir setup complete"
    cd - > /dev/null
}

# Setup root tooling first
echo "Setting up root tooling..."
uv sync --dev

# Setup each package
for package in "${PACKAGES[@]}"; do
    if [ -d "$package" ]; then
        setup_package "$package"
    else
        echo "Warning: Package directory $package not found"
    fi
done

echo ""
echo "Development environment setup complete!"
echo ""
echo "Each package now has its own isolated virtual environment:"
for package in "${PACKAGES[@]}"; do
    if [ -d "$package" ]; then
        echo "  - $package/.venv"
    fi
done
echo ""
echo "To work on a specific package:"
echo "  cd <package-directory>"
echo "  uv run <command>"
echo ""
echo "Example:"
echo "  cd servers/api-server"
echo "  uv run python -c 'import shared; print(\"Shared package available!\")'"