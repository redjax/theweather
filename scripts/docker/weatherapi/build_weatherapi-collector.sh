#!/bin/bash

set -euo pipefail

if ! command -v docker compose --version &> /dev/null; then
    echo "docker compose not installed"
    exit 1
fi

THIS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
REPO_ROOT=$( cd -- "$THIS_DIR/../../.." &> /dev/null && pwd )

SKIP_CACHE="false"

## Store path where script was originally called from
ORIGINAL_PWD=$(pwd)

## Source vars file
source "$THIS_DIR/weatherapi_paths"

## Function to switch back to original directory on script exit
function cleanup {
    cd "$ORIGINAL_PWD"
}
trap cleanup EXIT

## Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-cache)
            SKIP_CACHE="true"
            shift
            ;;
        -h | --help)
            echo "Usage: $0 [--skip-cache]"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

## Change working dir to repo root
cd "$REPO_ROOT"

echo "Building weatherapi-collector container"

## Build command
cmd=(docker compose -f "$WEATHERAPI_COLLECTOR_CONTAINER_DIR/compose.yml" build)
if [[ "$SKIP_CACHE" == "true" ]]; then
    echo "Skipping cache build will take longer)"
    cmd+=(--no-cache)
fi

## Preview command
echo "Running build command:"
echo "${cmd[@]}"
echo ""

## Execute command
"${cmd[@]}"
if [[ $? -ne 0 ]]; then
    echo ""
    echo "[ERROR] Failed to build weatherapi-collector container"
    echo ""
    exit 1
else
    echo ""
    echo "weatherapi-collector container built successfully"
    echo ""
fi
