#!/usr/bin/env bash

set -e

SOURCES="mhcgnomes tests"

echo "Running ruff format..."
ruff format $SOURCES

echo "Formatting complete!"
