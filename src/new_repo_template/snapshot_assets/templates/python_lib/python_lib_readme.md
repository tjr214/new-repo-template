# Python Library

This package is the reusable Python library baseline for the generated monorepo.

## Local Setup

- From the repo root: `uv sync --package python-lib --group dev`

## Baseline developer commands

- `uv run --package python-lib pytest packages/python/tests`
- `uv run --package python-lib ruff check packages/python`
- `uv run --package python-lib mypy packages/python/src`

The generated `python-app` target can depend on this package through the shared uv workspace.
