# Claude Code Instructions for mhcgnomes

## Before Completing Any Task

Before considering any code change complete, you MUST:

1. **Run `./format.sh`** - Auto-format all code
2. **Run `./lint.sh`** - Verify linting passes (this runs both `ruff check` and `ruff format --check`)
3. **Run `./test.sh`** - Verify all tests pass

Do not tell the user you are "done" or that changes are "complete" until all three of these pass.

## Scripts

- `./format.sh` - Formats code with ruff (run this first)
- `./lint.sh` - Checks linting and formatting (must pass)
- `./test.sh` - Runs pytest with coverage (must pass)
- `./deploy.sh` - Deploys to PyPI (already gates on lint.sh and test.sh)
- `./develop.sh` - Installs package in development mode

## Code Style

- Use ruff for formatting and linting
- Configuration is in `pyproject.toml` under `[tool.ruff]`
- Line length: 100 characters
- Target Python version: 3.9+
