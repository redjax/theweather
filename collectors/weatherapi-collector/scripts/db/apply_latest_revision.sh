#!/bin/bash

apply_latest_cmd=(uv run alembic upgrade head)

echo "Applying latest revision. Command:"
echo "  ${create_revision_cmd[*]}"

"${apply_latest_cmd[@]}"
if [[ $? -ne 0 ]]; then
    echo "[ERROR] Failed applying latest revision"
    exit $?
fi

echo "Upgraded database to latest revision"
exit 0
