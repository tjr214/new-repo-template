# Session 95 Summary

## Date and Time

2026-03-13 12:23:56 AM

## Scope

Expanded the foundation-lane scaffold baseline to include the repository `.github/` workflow tree and preserved the manifest guardrail that snapshot alias entries must continue to use `templates-snapshot-files/...` sources.

## Inputs

- `.github/workflows/ci.yml`
- `.github/workflows/release.yml`
- `src/new_repo_template/scaffold.py`
- `src/new_repo_template/snapshot_assets/source_manifest.json`
- `src/new_repo_template/snapshot_assets/manifest.json`
- `tests/contracts/test_root_workspace_contract.py`
- `PROGRESS.md`
- `docs/LIVING_DOCS.md`
- `docs/ARCHITECTURE.md`

## Implementation

- Ran the YELLOW pass by rereading the current `.github/` tree, scaffold wiring, snapshot manifests, and root workspace contracts; checking `btca status`; and using `btca ask` to confirm that deterministic package-resource scaffolds should explicitly enumerate tracked `.github` files rather than recursively copying the directory at runtime.
- Added RED coverage in `tests/contracts/test_root_workspace_contract.py` so dry-run/scaffold output now asserts the presence of `.github/`, `.github/workflows/`, `.github/workflows/ci.yml`, and `.github/workflows/release.yml`, and verifies the mirrored `.github` tree exists in generated output.
- Updated `src/new_repo_template/scaffold.py` so the foundation governance path contract and template-file allowlist now include the `.github` directory plus both workflow files.
- Expanded `src/new_repo_template/snapshot_assets/source_manifest.json` and `src/new_repo_template/snapshot_assets/manifest.json` to track `.github/workflows/ci.yml` and `.github/workflows/release.yml` as bundled foundation assets.
- Restored the `templates-snapshot-files/...` alias-backed source entries after a mistaken direct-path substitution and added an explicit maintenance note in `src/new_repo_template/snapshot_assets/source_manifest.json` stating that those alias entries must never be replaced with direct paths.
- Refreshed the bundled snapshot store with `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."` and synced the live docs to describe the new `.github` foundation baseline plus the alias-entrypoint guardrail.

## Verification

- `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."`
- `uv run pytest tests/contracts/test_root_workspace_contract.py tests/contracts/test_snapshot_assets_contract.py`
- `uv run ruff check src/new_repo_template tests/contracts`

## Documentation Sync

- Updated `PROGRESS.md`.
- Updated `docs/LIVING_DOCS.md`.
- Updated `docs/ARCHITECTURE.md`.

## Outcome

- Foundation scaffolds now include the repository `.github/workflows` baseline, and the snapshot source manifest now carries an explicit warning to preserve `templates-snapshot-files/...` alias sources for snapshot-managed entries.
