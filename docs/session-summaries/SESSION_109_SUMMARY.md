# Session 109 Summary

## Date and Time

2026-03-18 07:02:40 PM

## Scope

Completed feature `4.0` by shipping `nurt add` for existing nurt-generated monorepos, including strict repo identity validation, additive in-place mutation support, and matching CLI/Textual flows.

## Inputs

- `PLAN.md`
- `TODO-FEATURES.md`
- `PROGRESS.md`
- `docs/LIVING_DOCS.md`
- `docs/ARCHITECTURE.md`
- `src/new_repo_template/nurt_cli.py`
- `src/new_repo_template/add_mode.py`
- `src/new_repo_template/interactive_tui.py`
- `src/new_repo_template/repo_identity.py`
- `src/new_repo_template/snapshot_assets/source_manifest.json`
- `tests/contracts/test_nurt_cli_contract.py`
- `tests/contracts/test_nurt_add_contract.py`
- `tests/contracts/test_failure_atomicity_contract.py`
- `tests/contracts/test_generation_lockfiles_contract.py`
- `tests/contracts/test_interactive_tui_contract.py`

## Implementation

- Ran the full YELLOW phase for feature `4.0`: reread the add-related source/tests/docs, ran `btca status` and `btca resources`, and used `btca ask` for uv relock guidance, Bun workspace refresh guidance, and Textual in-place wizard recommendations.
- Added the explicit generated-repo identity marker `.nurt/repo.json` to the foundation baseline and synced the bundled snapshot metadata so `nurt add` can validate repo identity without heuristics.
- Implemented `nurt add` in `src/new_repo_template/nurt_cli.py` with strict repo-root validation, additive dry-run reporting, and a lockfile-regeneration-only completion path.
- Added `src/new_repo_template/add_mode.py` to inventory existing generated repos, resolve requested additions against live repo state, apply rollback-safe in-place mutations, and support the required retrofit cases.
- Extended `src/new_repo_template/interactive_tui.py` with a dedicated add wizard for rich sessions while keeping plain interactive add behavior available through the CLI fallback path.
- Covered the full feature with new/expanded contracts for CLI routing, add-mode mutations, rollback, lockfiles, foundation marker presence, and the new add wizard flow.

## Verification

- `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."`
- `uv run pytest tests/contracts/test_nurt_cli_contract.py tests/contracts/test_root_workspace_contract.py tests/contracts/test_nurt_add_contract.py tests/contracts/test_failure_atomicity_contract.py tests/contracts/test_generation_lockfiles_contract.py tests/contracts/test_interactive_tui_contract.py`
- `uv run pytest tests/contracts/test_snapshot_assets_contract.py`
- `uv run ruff check src/new_repo_template tests/contracts`
- `uv run pytest`

## Documentation Sync

- Updated `PLAN.md`.
- Updated `TODO-FEATURES.md`.
- Updated `PROGRESS.md`.
- Updated `docs/LIVING_DOCS.md`.
- Updated `docs/ARCHITECTURE.md`.

## Outcome

- Feature `4.0` is complete: generated repos now carry an explicit nurt identity marker, and `nurt add` can safely extend those repos in place without re-running the new-project bootstrap lifecycle.
