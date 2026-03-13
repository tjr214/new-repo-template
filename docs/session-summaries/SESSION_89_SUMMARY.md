# Session 89 Summary

## Date and Time

2026-03-12 09:16:05 PM

## Scope

Expanded the foundation-lane governance baseline so scaffolded repos inherit the root planning/readme files, helper scripts, and explicit archive subdirectories required for the new foundation contract.

## Inputs

- `src/new_repo_template/scaffold.py`
- `src/new_repo_template/snapshot_assets/source_manifest.json`
- `src/new_repo_template/snapshot_assets/manifest.json`
- `tests/contracts/test_root_workspace_contract.py`
- `scripts/validate_template.py`
- `scripts/visualize_plan.py`
- `PROGRESS.md`
- `docs/LIVING_DOCS.md`
- `docs/ARCHITECTURE.md`

## Implementation

- Ran the YELLOW pass by rereading the scaffold, snapshot, contract, and live-doc files; checking `btca status`; and using `btca ask` to confirm that explicit manifest-driven resource allowlists remain the safer approach for deterministic package-resource scaffolding than auto-copying directories.
- Added RED coverage in `tests/contracts/test_root_workspace_contract.py` for the new foundation-lane files (`PLAN.md`, `README*`, helper scripts) and the new empty archive subdirectories (`docs/archive/plans`, `docs/archive/progress`).
- Updated `src/new_repo_template/scaffold.py` so the foundation path contract, template-file allowlist, and empty-directory allowlist now include the new files/directories, and extended executable-bit handling to the scaffolded shell/Python helper scripts.
- Expanded `src/new_repo_template/snapshot_assets/source_manifest.json` and `src/new_repo_template/snapshot_assets/manifest.json`, restored root `PROGRESS.template.md` as the source stub for scaffolded `PROGRESS.md`, and regenerated the bundled snapshot assets with `nurt template-assets snapshot`.
- Cleared Ruff findings in the scaffolded helper-script sources by removing extraneous f-strings and an unused import in `scripts/validate_template.py` and `scripts/visualize_plan.py`, then resynced the snapshot bundle.
- Synced the current-state docs in `PROGRESS.md`, `docs/LIVING_DOCS.md`, and `docs/ARCHITECTURE.md` to describe the expanded governance baseline and the restored `PROGRESS.template.md` snapshot source.

## Verification

- `uv run pytest tests/contracts/test_root_workspace_contract.py tests/contracts/test_snapshot_assets_contract.py tests/contracts/test_nurt_cli_contract.py`
- `uv run ruff check src/new_repo_template tests/contracts`

## Documentation Sync

- Updated `PROGRESS.md`.
- Updated `docs/LIVING_DOCS.md`.
- Updated `docs/ARCHITECTURE.md`.

## Outcome

- Foundation scaffolds now include the requested planning/readme/helper-script baseline plus empty `docs/archive/plans` and `docs/archive/progress` directories, and the bundled snapshot assets/contracts are aligned with that expanded output.
