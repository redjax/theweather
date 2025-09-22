#!/bin/bash

set -euo pipefail

THIS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
REPO_ROOT=$( cd -- "$THIS_DIR/../../.." &> /dev/null && pwd )

SKIP_CACHE="false"
REBUILD="false"
RECREATE="false"

## Store path where script was originally called from
ORIGINAL_PWD=$(pwd)

## Source vars file
source "$THIS_DIR/weatherapi_paths"

## Import build function from build script
source "$THIS_DIR/build_weatherapi-collector.sh"

## Cleanup function to return to original directory
cleanup() {
    cd "$ORIGINAL_PWD"
}
trap cleanup EXIT

## Parse arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-cache)
                SKIP_CACHE="true"
                shift
                ;;
            --build|--rebuild)
                REBUILD="true"
                shift
                ;;
            -f|--force-recreate)
                RECREATE="true"
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [--skip-cache] [--build|--rebuild]"
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                exit 1
                ;;
        esac
    done
}

run_container() {
    cd "$REPO_ROOT"

    if [[ "$RECREATE" == "true" ]] && [[ "$REBUILD" == "true" ]]; then
        echo ""
        echo "[ERROR] Cannot pass both --build and --force-recreate"
        echo ""
        exit 1
    fi

    echo "Running weatherapi-collector container"

    local cmd=(docker compose -f "$WEATHERAPI_COLLECTOR_CONTAINER_DIR/compose.yml" up -d)
    if [[ "$REBUILD" == "true" ]]; then
        echo "Rebuilding weatherapi-collector container"
        if [[ "$SKIP_CACHE" == "true" ]]; then
            echo "Skipping cache (build will take longer)"
            cmd+=(--no-cache)
        else
            cmd+=(--build)
        fi
    fi

    if [[ "$RECREATE" == "true" ]]; then
        echo "Containers will be recreated"
        cmd+=(--force-recreate)
    fi

    echo "Running start command:"
    echo "${cmd[@]}"
    echo ""

    if ! "${cmd[@]}"; then
        echo ""
        echo "[ERROR] Failed to run weatherapi-collector container"
        echo ""
        exit 1
    else
        echo ""
        echo "weatherapi-collector container started successfully. Check health with docker ps -a"
        echo ""
    fi
}

main() {
    parse_args "$@"

    if [[ "$REBUILD" == "true" ]]; then
        build_weatherapi_collector "$REPO_ROOT" "$SKIP_CACHE"
    fi

    run_container
}

## Run main if script is executed (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
