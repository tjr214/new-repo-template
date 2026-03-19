# Session 116 Summary

## Date and Time

2026-03-19 07:01:28 PM

## Scope

Corrected the post-feature-6 template-sync regression so `src/new_repo_template/snapshot_assets/source_manifest.json` is once again the sole source of truth for foundation sync scope, restored the user-managed `sync` flags that were manually set in the source manifest, relaxed the over-strict contract expectation, and revalidated the sync-related contract slices.

## Inputs

- `PROGRESS.md`
- `docs/LIVING_DOCS.md`
- `docs/ARCHITECTURE.md`
- `PLAN.md`
- `src/new_repo_template/foundation_manifest.py`
- `src/new_repo_template/snapshot_assets/source_manifest.json`
- `tests/contracts/test_snapshot_assets_contract.py`
- `tests/contracts/test_template_asset_sync_contract.py`
- `tests/contracts/test_nurt_cli_contract.py`

## YELLOW Pass

- Re-read `src/new_repo_template/foundation_manifest.py`, `src/new_repo_template/snapshot_assets/source_manifest.json`, and the affected sync-related contract files before editing.
- Confirmed this slice was internal manifest-governance logic and did not require an additional dependency-behavior `btca ask` lookup beyond the earlier feature-6 work.
- Verified the root cause: `foundation_manifest.py` had grown a second hardcoded foundation sync allowlist that overrode user-managed `management.sync` flags in `source_manifest.json`.

## Changes

- Removed the hardcoded `FOUNDATION_SYNC_ALLOWED_DESTINATIONS` gate from `src/new_repo_template/foundation_manifest.py` so `get_foundation_sync_template_file_pairs(...)` now derives sync scope directly from the JSON manifest.
- Restored the manually configured `management.sync = true` entries in `src/new_repo_template/snapshot_assets/source_manifest.json` for the plan-template, task-template, and plan-helper OpenCode assets.
- Updated `tests/contracts/test_snapshot_assets_contract.py` so the sync-surface assertion now verifies that foundation sync destinations come directly from manifest metadata, while still asserting a few representative included and excluded paths.
- Refreshed bundled snapshot metadata with `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."`.
- Synced `PROGRESS.md`, `docs/LIVING_DOCS.md`, `docs/ARCHITECTURE.md`, and `PLAN.md` to reflect that manifest `management.sync` flags are the controlling contract.

## Validation

- `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."` -> passed
- `uv run pytest tests/contracts/test_snapshot_assets_contract.py tests/contracts/test_template_asset_sync_contract.py tests/contracts/test_nurt_cli_contract.py` -> 35 passed

## Outcome

- Template-sync scope is manifest-controlled again, the manually configured `sync` flags are restored, and the sync-related contract surface is back in alignment with the intended design.
