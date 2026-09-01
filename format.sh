#!/usr/bin/env bash

set -e

# Must match lint.sh, or a ruff-format violation in deploy.py or
# release_utils.py is reported by ./lint.sh and unfixable by ./format.sh.
SOURCES="mhcgnomes scripts tests deploy.py release_utils.py"

echo "Running ruff format..."
ruff format $SOURCES

echo "Formatting complete!"
