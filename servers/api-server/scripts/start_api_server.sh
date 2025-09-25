#!/bin/bash

set -uo pipefail

if ! commannd uv &> /dev/null && [[ ! -f "$HOME/.local/bin/uv" ]]; then
    echo "[ERROR] uv is not installed"
    exit 1
fi

echo ""
echo "Synching dependencies"
echo ""
uv sync --dev --all-extras

echo ""
echo "Starting API server"
echo ""
uv run python -m api_server
