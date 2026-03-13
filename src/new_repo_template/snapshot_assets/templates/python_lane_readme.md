# Python Lane

This app is the dedicated Python CLI and Textual TUI baseline for the generated monorepo.

## Local Setup

- `uv sync --group dev`

## CLI Entry Points

- `uv run python-app demo-user`
- `uv run python-app --help`
- `uv run python-app-tui`
- `uv run python-app-tui --help`

## Baseline developer commands

- `uv run pytest`
- `uv run ruff check .`
- `uv run mypy src`

The plain CLI uses Rich output, while the interactive mode launches a starter Textual app.
