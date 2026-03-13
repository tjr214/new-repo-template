# Session 90 Summary

## Date and Time

2026-03-12 11:38:36 PM

## Scope

Expanded the foundation scaffold baseline so bundled docs now include the live architecture/living-doc files and the full `docs/markdown-templates/` directory with both tracked template files.

## Inputs

- `src/new_repo_template/scaffold.py`
- `src/new_repo_template/snapshot_assets/source_manifest.json`
- `src/new_repo_template/snapshot_assets/manifest.json`
- `tests/contracts/test_root_workspace_contract.py`
- `docs/markdown-templates/PLAN.template.md`
- `docs/markdown-templates/PROGRESS.template.md`
- `PROGRESS.md`
- `docs/LIVING_DOCS.md`
- `docs/ARCHITECTURE.md`

## Implementation

- Ran the YELLOW pass by rereading the scaffold, snapshot-manifest, contract, and live-doc files; checking `btca status`; and reusing the same manifest-driven scaffold guidance established earlier in the thread after a fresh `btca ask` attempt stalled.
- Added RED coverage in `tests/contracts/test_root_workspace_contract.py` for `docs/ARCHITECTURE.md`, `docs/LIVING_DOCS.md`, the `docs/markdown-templates/` directory, and both mirrored template files.
- Updated `src/new_repo_template/scaffold.py` so foundation dry-run/scaffold output now includes `docs/ARCHITECTURE.md`, `docs/LIVING_DOCS.md`, `docs/markdown-templates/PLAN.template.md`, and `docs/markdown-templates/PROGRESS.template.md`, while root scaffolded `PLAN.md` and `PROGRESS.md` now read from the markdown-template sources.
- Expanded `src/new_repo_template/snapshot_assets/source_manifest.json` and `src/new_repo_template/snapshot_assets/manifest.json` so the bundled package resources now track the two live docs plus both markdown-template files explicitly.
- Refreshed the bundled template store with `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."`, which updated the packaged foundation assets and refreshed `src/new_repo_template/snapshot_assets/metadata.json`.
- Synced `PROGRESS.md`, `docs/LIVING_DOCS.md`, and `docs/ARCHITECTURE.md` so the live documentation now describes the docs-inclusive foundation baseline and the template-backed `PLAN.md` / `PROGRESS.md` scaffold model accurately.

## Verification

- `uv run pytest tests/contracts/test_root_workspace_contract.py tests/contracts/test_snapshot_assets_contract.py`
- `uv run ruff check src/new_repo_template tests/contracts`

## Documentation Sync

- Updated `PROGRESS.md`.
- Updated `docs/LIVING_DOCS.md`.
- Updated `docs/ARCHITECTURE.md`.

## Outcome

- Foundation scaffolds now carry `docs/ARCHITECTURE.md`, `docs/LIVING_DOCS.md`, and the full tracked `docs/markdown-templates/` directory, and bundled snapshot metadata/contracts are aligned with that expanded documentation baseline.
