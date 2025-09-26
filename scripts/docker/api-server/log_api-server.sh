#!/bin/bash

set -euo pipefail

THIS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
REPO_ROOT=$( cd -- "$THIS_DIR/../../.." &> /dev/null && pwd )

## Store path where script was originally called from
ORIGINAL_PWD=$(pwd)

## Source vars file
source "$THIS_DIR/api_server_paths"

## Cleanup function to return to original directory
cleanup() {
    cd "$ORIGINAL_PWD"
}
trap cleanup EXIT

## Function to parse arguments if you want to extend
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                echo "Usage: $0"
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                exit 1
                ;;
        esac
    done
}

## Function to run logs command
logs_api_server() {
    cd "$REPO_ROOT"

    echo "Showing logs of api-server container"

    local cmd=(docker compose -f "$API_SERVER_CONTAINER_DIR/compose.yml" logs -f api-server)

    echo "Running logs command:"
    echo "${cmd[@]}"
    echo ""

    "${cmd[@]}"
}

main() {
    parse_args "$@"

    logs_api_server
}

## Run main if script executed (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
