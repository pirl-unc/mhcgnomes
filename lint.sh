#!/bin/bash
set -o errexit

# Run ruff linter
ruff check mhcgnomes tests

echo 'Passes ruff check'

# Run ruff formatter check
ruff format --check mhcgnomes tests

echo 'Passes ruff format check'
