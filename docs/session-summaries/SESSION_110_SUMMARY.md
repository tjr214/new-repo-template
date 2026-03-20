# Session 110 Summary

## Date and Time

2026-03-18 07:34:05 PM

## Scope

Fixed the first live `nurt add` regression where add-mode failed while refreshing an existing `bun.lock` after the workspace graph changed.

## Inputs

- `src/new_repo_template/version_baseline.py`
- `src/new_repo_template/add_mode.py`
- `tests/contracts/test_generation_lockfiles_contract.py`
- `PROGRESS.md`
- `docs/LIVING_DOCS.md`
- `docs/ARCHITECTURE.md`

## Implementation

- Re-ran the YELLOW pass for the bugfix by rereading the add-mode and lockfile-regeneration code paths.
- Used `btca ask -r bun` to confirm that workspace-changing add flows should use a mutable Bun install command, not `--frozen-lockfile`.
- Removed `--frozen-lockfile` from the Bun lockfile regeneration command in `src/new_repo_template/version_baseline.py`, keeping `--save-text-lockfile --lockfile-only` for root lockfile refreshes.
- Added a regression contract in `tests/contracts/test_generation_lockfiles_contract.py` that seeds an existing `bun.lock`, adds a new workspace via `nurt add`, and asserts the lockfile updates successfully.

## Verification

- `uv run pytest tests/contracts/test_generation_lockfiles_contract.py`
- `uv run ruff check src/new_repo_template tests/contracts`
- `uv run pytest`

## Documentation Sync

- Updated `PROGRESS.md`.
- Updated `docs/LIVING_DOCS.md`.
- Updated `docs/ARCHITECTURE.md`.

## Outcome

- `nurt add` now refreshes existing Bun lockfiles correctly when new workspaces are introduced, matching Bun’s documented update semantics.
