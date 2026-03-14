# Session 106 Summary

## Date and Time

2026-03-13 07:51:41 PM

## Scope

Completed feature `3.0` by migrating scaffold output to named project-instance directories and updating `nurt new` to support multiple projects of the same type in both the CLI and interactive flows.

## Inputs

- `PLAN.md`
- `TODO-FEATURES.md`
- `PROGRESS.md`
- `docs/LIVING_DOCS.md`
- `docs/ARCHITECTURE.md`
- `src/new_repo_template/{scaffold.py,nurt_cli.py,interactive_ui.py,interactive_tui.py,version_baseline.py}`
- `src/new_repo_template/snapshot_assets/templates/root_package.json`
- `src/new_repo_template/snapshot_assets/templates/root_python_workspace_pyproject.toml`
- contract suites under `tests/contracts/`

## Implementation

- Ran the YELLOW phase by rereading the scaffold, CLI, plain/TUI interactive flows, workspace templates, lockfile behavior, and current contracts, then using `btca ask` to confirm Bun/Turborepo nested workspace globs and uv named-member workspace patterns.
- Refactored `src/new_repo_template/scaffold.py` around typed `ProjectSpec` instances so generated app/library output now lives under nested instance paths like `apps/web/<name>`, `apps/python/<name>`, `packages/python/<name>`, and `packages/typescript/<name>`.
- Added repeatable `--project <type>:<name>` support plus `--backend-auth` / `--web-backend` routing in `src/new_repo_template/scaffold.py` and `src/new_repo_template/nurt_cli.py`, while preserving `--target` as a default-name compatibility shim.
- Updated root workspace generation so Bun workspaces now include `apps/*`, `packages/*`, `apps/*/*`, and `packages/*/*`, while Python-enabled repos now use uv workspace members `apps/python/*` and `packages/python/*`.
- Extended `nurt new` plain interactive flow to collect comma-separated project names per selected target type and wired the Textual wizard in `src/new_repo_template/interactive_tui.py` to collect project names before review.
- Updated dynamic scaffold rendering so package names, Python distribution/module names, console scripts, env-example placement, and backend/web auth wiring are derived from the resolved project instance names.
- Expanded and updated contract coverage across scaffold, workspace, runtime-smoke, `nurt new`, and Textual wizard suites for the new multi-instance model.

## Verification

- `uv run pytest`
- `uv run ruff check src/new_repo_template tests/contracts`
- `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."`

## Documentation Sync

- Updated `PLAN.md`.
- Updated `PROGRESS.md`.
- Updated `docs/LIVING_DOCS.md`.
- Updated `docs/ARCHITECTURE.md`.
- Updated `TODO-FEATURES.md`.

## Outcome

- Feature `3.0` is now complete, and the next logical implementation slice is feature `4.0` for `nurt add` support on existing monorepos.
