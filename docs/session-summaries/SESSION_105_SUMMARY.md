# Session 105 Summary

## Date and Time

2026-03-13 05:37:33 PM

## Scope

Completed feature `2.0` by adding reusable `python-lib` and `typescript-lib` scaffold targets, moving generated library code into `packages/python` and `packages/typescript`, and upgrading Python-enabled repos to use a root uv workspace.

## Inputs

- `TODO-FEATURES.md`
- `PROGRESS.md`
- `docs/LIVING_DOCS.md`
- `docs/ARCHITECTURE.md`
- `src/new_repo_template/scaffold.py`
- `src/new_repo_template/{interactive_ui.py,interactive_tui.py,nurt_cli.py,version_baseline.py}`
- `src/new_repo_template/snapshot_assets/templates/python_lane_*`
- `src/new_repo_template/snapshot_assets/templates/{python_lib,typescript_lib}/*`
- `src/new_repo_template/snapshot_assets/templates/root_python_workspace_pyproject.toml`
- `src/new_repo_template/snapshot_assets/templates/workspace_packages/typescript_lib_package.json`
- `tests/contracts/test_python_lane_contract.py`
- `tests/contracts/test_python_lib_scaffold_contract.py`
- `tests/contracts/test_typescript_lib_scaffold_contract.py`
- `tests/contracts/test_typescript_lib_runtime_smoke_contract.py`
- `tests/contracts/test_required_preset_matrix_contract.py`
- `tests/contracts/test_nurt_cli_contract.py`
- `tests/contracts/test_interactive_tui_contract.py`
- `tests/contracts/test_generation_lockfiles_contract.py`
- `tests/contracts/test_cli_validation_and_python_commands_contract.py`

## Implementation

- Ran the YELLOW phase by rereading scaffold, CLI, interactive, lockfile, and documentation files; checking `btca status` / `btca resources`; and using `btca ask` for uv workspace behavior plus Bun/Turborepo mixed-package layout guidance.
- Expanded `src/new_repo_template/scaffold.py` so the target matrix now includes `python-lib` and `typescript-lib`, library outputs land at `packages/python` and `packages/typescript`, and Python-enabled repos scaffold a root uv workspace `pyproject.toml`.
- Updated the generated Python app baseline so its README and starter commands use workspace-targeted `uv sync/run --package python-app ...` flows, and the app wires `python-lib` through `[tool.uv.sources]` when both Python targets are selected.
- Added bundled Python library templates for a Hatchling-based package with starter source/tests and bundled TypeScript library templates for a publishable Bun/TypeScript package with `dist` build wiring.
- Updated `src/new_repo_template/{interactive_ui.py,interactive_tui.py}` so both new library lanes appear in plain and Textual target-selection flows.
- Updated `src/new_repo_template/version_baseline.py` so Python-enabled generated repos create a single root `uv.lock` for the uv workspace instead of an app-local lockfile.
- Added dedicated scaffold/runtime contracts for the new library lanes and expanded the existing Python, preset-matrix, lockfile, `nurt`, CLI-validation, and Textual wizard suites for the new workspace model.

## Verification

- `uv run pytest tests/contracts/test_python_lane_contract.py tests/contracts/test_python_lib_scaffold_contract.py tests/contracts/test_typescript_lib_scaffold_contract.py tests/contracts/test_typescript_lib_runtime_smoke_contract.py tests/contracts/test_required_preset_matrix_contract.py tests/contracts/test_nurt_cli_contract.py tests/contracts/test_interactive_tui_contract.py tests/contracts/test_generation_lockfiles_contract.py tests/contracts/test_cli_validation_and_python_commands_contract.py`
- `uv run ruff check src/new_repo_template tests/contracts`
- `uv run pytest`

## Documentation Sync

- Updated `TODO-FEATURES.md`.
- Updated `PROGRESS.md`.
- Updated `docs/LIVING_DOCS.md`.
- Updated `docs/ARCHITECTURE.md`.

## Outcome

- Feature `2.0` is now complete, and the next logical implementation slice is feature `3.0` for supporting multiple projects of the same type in `nurt new`.
