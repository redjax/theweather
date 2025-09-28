#!/bin/bash

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

NAMESPACE="weatherapi"
TEMPORAL_ADDRESS="localhost:7233"

function print_help() {
    echo ""
    echo "[Temporal Namespace Management]"
    echo " Creates a Temporal namespace."
    echo ""
    echo " Usage: $0 [options]"
    echo "   -n|--namespace <namespace>"
    echo "   -t|--temporal-address <address>"
    echo ""
    echo " Options:"
    echo "   -h|--help      Print this help message."
    echo ""
}

while [[ $# -gt 0 ]]; do
  case $1 in
    -n|--namespace)
      if [[ -z "$2" ]]; then
        echo "Option $1 requires an argument."
        print_help
        exit 1
      fi
      NAMESPACE="$2"
      shift 2
      ;;
    -h|--help)
      print_help
      exit 0
      ;;
    *)
      echo "Unknown option $1"
      print_help
      exit 1
      ;;
  esac
done

CMD=(
    docker run --rm \
    --network=host \
    temporalio/temporal \
    operator namespace create \
    --namespace "$NAMESPACE" \
    --address "$TEMPORAL_ADDRESS"
)

echo ""
echo "Create Temporal namespace: $NAMESPACE"
echo "  Command: ${CMD[*]}"
echo ""

"${CMD[@]}"
if [[ $? -ne 0 ]]; then
  echo "Failed to $OPERATION temporal namespace."
  exit 1
fi
