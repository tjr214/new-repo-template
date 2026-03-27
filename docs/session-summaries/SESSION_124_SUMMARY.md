# Session 124 Summary

## Date and Time

2026-03-25 09:03:13 PM

## Scope

Implemented feature `9.0` end to end: composition-aware BTCA generation for `nurt new`, additive BTCA merge/update behavior for `nurt add`, sidecar-based managed-resource ownership tracking, and generated `docs/BTCA_RESOURCES.md` output.

## YELLOW Pass

- Re-read the active implementation plan, current trackers/docs, latest session summary, scaffold/add-mode/contracts, and the current target manifests before editing code.
- Re-ran `btca status` and `btca resources` after the newly approved project BTCA resources were added.
- Used `btca ask` during the discussion/implementation cycle to confirm the direct-tool-coverage rule: direct framework/tool dependencies should have exact BTCA coverage rather than relying only on adjacent docs.

## Implementation

- Added `src/new_repo_template/btca_config_manager.py` for BTCA resource definitions, target mapping, sidecar handling, fingerprint-based drift detection, additive merge logic, and docs rendering.
- Updated `src/new_repo_template/scaffold.py` so scaffold output now writes dynamic `btca.config.jsonc`, `.nurt/btca-managed-resources.json`, and `docs/BTCA_RESOURCES.md` files.
- Updated `src/new_repo_template/add_mode.py` so add mode merges managed BTCA resources by stable name, preserves user-added resources, preserves drifted managed resources with warnings, and refreshes BTCA docs output.
- Added the approved project BTCA resources to this template repo: `react-docs`, `react-native-docs`, `vite`, `electron-forge`, `electron`, `typescript-docs`, `pytest`, `ruff`, and `mypy`.
- Removed the stale static BTCA foundation snapshot entry from `src/new_repo_template/snapshot_assets/source_manifest.json`, deleted `src/new_repo_template/snapshot_assets/templates/foundation/btca.config.jsonc`, and regenerated `src/new_repo_template/snapshot_assets/{manifest.json,metadata.json}`.

## RED / BLUE Coverage

- Added `tests/contracts/test_btca_config_contract.py`.
- Expanded `tests/contracts/test_root_workspace_contract.py`, `tests/contracts/test_nurt_add_contract.py`, and `tests/contracts/test_nurt_cli_contract.py` for BTCA generation, sidecar presence, add-mode merge behavior, warnings, and docs sync.

## Validation

- `uv run pytest tests/contracts/test_btca_config_contract.py tests/contracts/test_root_workspace_contract.py tests/contracts/test_nurt_add_contract.py tests/contracts/test_nurt_cli_contract.py`
- `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."`
- `uv run ruff check src/new_repo_template tests/contracts`
- `uv run pytest`

## Outcome

- Feature `9.0` is complete.
- The next roadmap item is feature `10.0`, which now needs a fresh YELLOW discussion/planning pass for release-candidate testing.
