#!/usr/bin/env bash

set -e

VENV_DIR=".venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment at $VENV_DIR..."
    python -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# Check if UV is installed and available in the PATH
if command -v uv &> /dev/null; then
    echo "Using uv to install package in development mode..."
    uv pip install -e .
else
    echo "uv not found, falling back to regular pip..."
    pip install -e .
fi
