# Python Lane

This app is the dedicated Python CLI and Textual TUI baseline for the generated monorepo.

## Local Setup

- `uv sync --package python-app --group dev`

## CLI Entry Points

- `uv run --package python-app python-app demo-user`
- `uv run --package python-app python-app --help`
- `uv run --package python-app python-app-tui`
- `uv run --package python-app python-app-tui --help`

## Baseline developer commands

- `uv run --package python-app pytest apps/python/tests`
- `uv run --package python-app ruff check apps/python`
- `uv run --package python-app mypy apps/python/src`

The plain CLI uses Rich output, while the interactive mode launches a starter Textual app.
