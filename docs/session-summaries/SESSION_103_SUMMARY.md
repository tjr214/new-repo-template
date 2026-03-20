# Session 103 Summary

## Date and Time

2026-03-13 03:50:26 PM

## Scope

Completed the manifest-driven foundation refactor so `source_manifest.json` now acts as the single source of truth for foundation scaffold files and scaffold-only empty directories, with runtime snapshot manifest regeneration wired into `nurt template-assets validate`.

## Inputs

- `src/new_repo_template/snapshot_assets/source_manifest.json`
- `src/new_repo_template/foundation_manifest.py`
- `src/new_repo_template/scaffold.py`
- `src/new_repo_template/snapshot_builder.py`
- `src/new_repo_template/nurt_cli.py`
- `src/new_repo_template/snapshot_assets/manifest.json`
- `src/new_repo_template/snapshot_assets/metadata.json`
- `tests/contracts/test_root_workspace_contract.py`
- `tests/contracts/test_snapshot_assets_contract.py`
- `tests/contracts/test_nurt_cli_contract.py`
- `PROGRESS.md`
- `docs/LIVING_DOCS.md`
- `docs/ARCHITECTURE.md`

## Implementation

- Preserved the CRITICAL maintenance warning at the top of `src/new_repo_template/snapshot_assets/source_manifest.json` and extended the manifest with `empty_directories` entries for foundation scaffold-only directories.
- Added `src/new_repo_template/foundation_manifest.py` to validate manifest paths and derive foundation scaffold file mappings, dry-run path visibility, scaffold-only empty-directory creation, and the runtime snapshot manifest from one explicit manifest source.
- Refactored `src/new_repo_template/scaffold.py` so foundation governance assets no longer rely on duplicated hard-coded file/path lists.
- Refactored `src/new_repo_template/snapshot_builder.py` and `src/new_repo_template/nurt_cli.py` so `nurt template-assets validate` regenerates `src/new_repo_template/snapshot_assets/manifest.json`, refreshes `metadata.json`, and reports both refresh operations.
- Expanded contract coverage to guard the manifest-driven empty-directory baseline, runtime manifest generation, and validate-command dry-run/output reporting.
- Regenerated the bundled snapshot artifacts from the live source manifest.

## Verification

- `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."`
- `uv run pytest tests/contracts/test_root_workspace_contract.py tests/contracts/test_snapshot_assets_contract.py tests/contracts/test_nurt_cli_contract.py`
- `uv run pytest`
- `uv run ruff check src/new_repo_template tests/contracts`

## Documentation Sync

- Updated `PROGRESS.md`.
- Updated `docs/LIVING_DOCS.md`.
- Updated `docs/ARCHITECTURE.md`.

## Outcome

- Adding a normal foundation scaffold file now requires one source-manifest entry plus `nurt template-assets validate`, and adding a scaffold-only foundation empty directory now requires one `empty_directories` entry plus the same validation flow.
