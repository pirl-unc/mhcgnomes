#!/usr/bin/env bash

set -e

# Check if UV is installed and available in the PATH
if command -v uv &> /dev/null; then
    echo "Using uv to install package in development mode..."
    uv pip install -e .
else
    echo "uv not found, falling back to regular pip..."
    pip install -e .
fi

