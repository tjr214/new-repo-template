# Session 113 Summary

## Date and Time

2026-03-19 04:10:11 PM

## Scope

Implemented feature `5.0` end to end so `nurt sync template-assets` is now a real native, manifest-driven maintenance command backed by bundled snapshot assets, then retired the legacy shell updater and synced the project docs to the completed state.

## Inputs

- `PLAN.md`
- `PROGRESS.md`
- `TODO-FEATURES.md`
- `docs/LIVING_DOCS.md`
- `docs/ARCHITECTURE.md`
- `docs/session-summaries/SESSION_112_SUMMARY.md`
- `src/new_repo_template/sync_ops.py`
- `src/new_repo_template/nurt_cli.py`
- `src/new_repo_template/foundation_manifest.py`
- `src/new_repo_template/snapshot_builder.py`
- `src/new_repo_template/snapshot_assets_loader.py`
- `src/new_repo_template/snapshot_assets/source_manifest.json`
- `tests/contracts/test_nurt_cli_contract.py`
- `tests/contracts/test_snapshot_assets_contract.py`
- `tests/contracts/test_template_asset_sync_contract.py`
- `tests/contracts/test_installer_scripts_dry_run_contract.py`
- `.template_scripts/update-template-from-git.sh`

## Implementation

- Ran the full YELLOW pass from the active plan: reread the required docs, sync/runtime-manifest implementation files, source manifest, bundled foundation template surface, and current contracts, then ran `btca status` plus `btca ask -r uv ... --sub-agent` to preserve the feature `5.0` versus feature `7.0` boundary around `uv tool upgrade`.
- Added RED coverage for source-manifest `management` metadata, the exact manifest-derived sync allowlist, dry-run sync reporting, `.nurt/repo.json` root validation, dirty-git refusal, managed-file refresh behavior, custom-sibling preservation, and no-delete/no-empty-namespace guarantees.
- Extended `src/new_repo_template/foundation_manifest.py` with typed `management` parsing, scaffold/sync-aware source-manifest entries, a validated exact-path sync allowlist helper, and runtime-manifest generation that remains compatible with existing scaffold consumers.
- Updated `src/new_repo_template/snapshot_assets/source_manifest.json` so entries now carry explicit `management` flags, keeping scaffold behavior broad while marking only the approved managed subset as syncable.
- Replaced the clone-based sync implementation in `src/new_repo_template/sync_ops.py` with bundled-snapshot exact-file writes, manifest-derived sync planning, `.nurt/repo.json` root validation, and strict clean-working-tree enforcement.
- Regenerated `src/new_repo_template/snapshot_assets/manifest.json` and `src/new_repo_template/snapshot_assets/metadata.json` with `nurt template-assets validate` so the packaged runtime bundle matches the corrected source manifest and actual packaged template files.
- Manually reviewed the legacy `.template_scripts/update-template-from-git.sh` flow after the native implementation landed, confirmed it was redundant, removed it, and updated installer-script contract coverage to enforce its absence.
- Corrected the stray feature `5.0` plan typo that referenced a non-existent `project-get-back-to-work.md` command; the real manifest-driven sync allowlist now excludes that nonexistent path entirely.

## Verification

- `btca status`
- `btca ask -r uv -q "For a CLI tool installed with uv tool install git plus a repository URL, is uv tool upgrade the standard way to refresh the installed tool version later?" --sub-agent`
- `uv run pytest tests/contracts/test_snapshot_assets_contract.py tests/contracts/test_template_asset_sync_contract.py tests/contracts/test_nurt_cli_contract.py`
- `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."`
- `uv run pytest tests/contracts/test_snapshot_assets_contract.py tests/contracts/test_template_asset_sync_contract.py tests/contracts/test_nurt_cli_contract.py`
- `uv run pytest tests/contracts/test_nurt_cli_contract.py`
- `uv run pytest tests/contracts/test_snapshot_assets_contract.py`
- `uv run pytest tests/contracts/test_template_asset_sync_contract.py tests/contracts/test_installer_scripts_dry_run_contract.py`
- `uv run ruff check src/new_repo_template tests/contracts`
- `uv run pytest` (214 passed)

## Documentation Sync

- Updated `PLAN.md` to mark feature `5.0` complete and removed the stray nonexistent sync-target typo.
- Updated `TODO-FEATURES.md` to mark feature `5.0` and legacy-updater retirement complete.
- Updated `PROGRESS.md` with the completed feature `5.0` implementation slice and feature `6.0` as the next planned effort.
- Updated `docs/LIVING_DOCS.md` to describe the completed native manifest-driven sync behavior and legacy-script retirement.
- Updated `docs/ARCHITECTURE.md` to record the final feature `5.0` implementation shape.

## Outcome

- Feature `5.0` is complete: `nurt sync template-assets` now refreshes only the explicit managed file set from bundled snapshot assets, enforces real repo identity plus clean-git safety for non-dry-run execution, preserves custom sibling files, and no longer depends on or ships the old clone-based updater script.
