#!/bin/bash

set -uo pipefail

if ! command -v uv &> /dev/null; then
    echo "uv not installed"
    exit 1
fi

## Packages in the repository to install
#  with uv pip install -e
declare -a packages=(
    "shared"
    "collectors/weatherapi-collector"
)

function uv_init() {
    echo "Synchronizing packages"
    uv sync --dev --all-extras

    ## Install packages for local development
    echo "Installing packages for local development"
    for pkg in "${packages[@]}"; do
        uv pip install -e $pkg
    done
}

function main() {
    uv_init
    if [[ $? -ne 0 ]]; then
        echo "[ERROR] Failed to install packages for local development"
        exit 1
    fi
}

main
if [[ $? -ne 0 ]]; then
    echo ""
    echo "[ERROR] Failed to setup local development environment"
    echo ""

    exit 1
else
    echo ""
    echo "Local development environment setup successfully"
    echo ""
fi
