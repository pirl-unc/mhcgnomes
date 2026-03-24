#!/usr/bin/env bash

set -e

SOURCES="mhcgnomes tests deploy.py release_utils.py"

echo "Running ruff check..."
ruff check $SOURCES

echo "Running ruff format check..."
ruff format --check $SOURCES

echo "All checks passed!"
