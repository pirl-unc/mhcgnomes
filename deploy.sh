#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

./lint.sh
./test.sh

PYTHON_BIN="${DEPLOY_PYTHON:-python3}"
"$PYTHON_BIN" deploy.py "$@"
