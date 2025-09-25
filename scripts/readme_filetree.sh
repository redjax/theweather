#!/bin/bash

set -uo pipefail

if ! command -v tree &>/dev/null; then
    echo "tree not installed"
    exit 1
fi

IGNORE_STR=".git|.venv|__pycache__|.nox|.ruff_cache|.db|.cache|.logs|dist|.vscode|src|config"

cmd=(tree . -r -a -d -F -L 2 -I "${IGNORE_STR}" --noreport)

echo "Creating filetree. Command:"
echo "  $ ${cmd[@]}"

"${cmd[@]}"
