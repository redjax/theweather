#!/bin/bash

set -euo pipefail

## Function to check pre-requisites
check_prereqs() {
    if ! command -v docker compose --version &> /dev/null; then
        echo "docker compose not installed"
        exit 1
    fi
}

## Function to get repository root directory
get_repo_root() {
    local THIS_DIR
    THIS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
    cd "$THIS_DIR/../../.." && pwd
}

## Function to parse arguments
parse_args() {
    SKIP_CACHE="false"
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-cache)
                SKIP_CACHE="true"
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [--skip-cache]"
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                exit 1
                ;;
        esac
    done
}

## Function to build the api-server container
build_api_server() {
    local repo_root="$1"
    local skip_cache="$2"
    local original_pwd
    ORIGINAL_PWD=$(pwd)

    ## Source paths file relative to script location
    local script_dir
    script_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
    source "$script_dir/api_server_paths"

    ## Cleanup function to restore cwd
    cleanup() {
        cd "$ORIGINAL_PWD"
    }
    trap cleanup EXIT

    ## Change directory to repo root
    cd "$repo_root"

    echo "Building api-server container"

    local cmd=(docker compose -f "$API_SERVER_CONTAINER_DIR/compose.yml" build)
    if [[ "$skip_cache" == "true" ]]; then
        echo "Skipping cache (build will take longer)"
        cmd+=(--no-cache)
    fi

    echo "Running build command:"
    echo "${cmd[@]}"
    echo ""

    ## Execute command
    if ! "${cmd[@]}"; then
        echo ""
        echo "[ERROR] Failed to build api-server container"
        echo ""
        exit 1
    else
        echo ""
        echo "api-server container built successfully"
        echo ""
    fi
}

## Main function for CLI execution
main() {
    check_prereqs

    parse_args "$@"

    local repo_root
    repo_root=$(get_repo_root)

    build_api_server "$repo_root" "$SKIP_CACHE"
}

## If sourced, don’t run main; if executed directly, run main
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
