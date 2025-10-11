#!/bin/bash

THIS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
REPO_ROOT=$( dirname "$THIS_DIR" )

IGNORE_STR=".git|.venv|__pycache__|.nox|.ruff_cache|.cache|.direnv|.db|.python-version|*.log|*.log.*|dist|.logs|*.whl|.rar|.zip|.tar.gz"

if ! command -v tree > /dev/null; then
    echo "tree not installed"
    exit 1
fi

tree "$REPO_ROOT" -r -a -f -I "$IGNORE_STR"
