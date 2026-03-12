# Session 74 Summary

## Date and Time

2026-03-11 09:11:17 PM

## Scope

Relocated generated Python metadata so `.python-version`, `pyproject.toml`, and `uv.lock` exist only inside `apps/python`, with no Python-only files scaffolded at repo root or in foundation output.

## Inputs

- `src/new_repo_template/scaffold.py`
- `src/new_repo_template/version_baseline.py`
- `src/new_repo_template/snapshot_assets/{manifest.json,source_manifest.json}`
- Contract coverage in `tests/contracts/`
- Current tracker/docs state in `PLAN.md`, `PROGRESS.md`, `docs/LIVING_DOCS.md`, and `docs/ARCHITECTURE.md`
- YELLOW context from `btca status`; no dependency-specific `btca ask` lookup was needed because the change stayed inside repo-local scaffold and lockfile placement rules

## Implementation

- Removed root `pyproject.toml` and root `.python-version` from scaffold generation and dry-run planning.
- Replaced the Python-lane `.python-version` symlink with a lane-local file written directly into `apps/python`.
- Updated post-scaffold lockfile generation so Python-target outputs create `apps/python/uv.lock` while root generation keeps `bun.lock` only.
- Renamed the bundled Python-version snapshot asset to `python_lane_python_version.txt` and updated snapshot manifests.
- Revised scaffold, preset-matrix, target-matrix, and generation-lockfile contracts to enforce root absence plus lane-only Python metadata.

## Verification

- `uv run pytest tests/contracts/test_monorepo_foundation_contract.py tests/contracts/test_python_lane_contract.py tests/contracts/test_required_preset_matrix_contract.py tests/contracts/test_target_matrix_and_auth_contract.py tests/contracts/test_generation_lockfiles_contract.py tests/contracts/test_nurt_cli_contract.py tests/contracts/test_snapshot_assets_contract.py`
- `uv run pytest`

## Documentation Sync

- Updated `PLAN.md` and `PROGRESS.md` for this completed relocation slice.
- Updated `docs/LIVING_DOCS.md` and `docs/ARCHITECTURE.md` to reflect lane-only Python metadata and `apps/python/uv.lock` ownership.

## Outcome

- Foundation and JS-only scaffold outputs no longer include Python-only files at repo root.
- Python-target outputs now keep `.python-version`, `pyproject.toml`, and `uv.lock` entirely under `apps/python`.
- Root scaffold output still inherits the shared `.gitignore` baseline and root Bun workspace files without duplicating Python metadata.
