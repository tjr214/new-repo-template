# Session 117 Summary

## Date and Time

2026-03-24 01:33:44 PM

## Scope

Completed feature `7.0` by replacing the transitional `nurt update` path with the real `nurt upgrade` workflow, locking the self-update surface to `uv`-managed installs, switching startup notices to uv's non-mutating outdated-tool listing, and syncing the roadmap/live docs to the finished contract.

## Inputs

- `TODO-FEATURES.md`
- `PLAN.md`
- `PROGRESS.md`
- `README.md`
- `pyproject.toml`
- `docs/LIVING_DOCS.md`
- `docs/ARCHITECTURE.md`
- `.github/workflows/release.yml`
- `src/new_repo_template/nurt_cli.py`
- `tests/contracts/test_nurt_cli_contract.py`

## YELLOW Pass

- Re-read the roadmap, active plan, progress tracker, living docs, architecture docs, README install guidance, release workflow, CLI implementation, and the `nurt` CLI contract file before editing.
- Ran `btca status` and `btca resources`, then used `btca ask -r uv` to confirm that `uv tool upgrade <installed-package>` is the supported self-update path for uv-managed tools, that `uv tool list --outdated` is the better non-mutating startup-check surface, and that reinstall remediation should reuse `uv tool install` with the same Git source when needed.
- Verified the package-vs-executable nuance empirically in an isolated workspace-local uv tool directory: the installed executable is `nurt`, but the uv-managed tool identity is `nurt-ai`, so the real upgrade target must be `uv tool upgrade nurt-ai`.

## Changes

- Replaced the old `update` parser entry in `src/new_repo_template/nurt_cli.py` with `upgrade` and renamed the handler accordingly.
- Updated the startup notice path in `src/new_repo_template/nurt_cli.py` to use `uv tool list --outdated` plus `nurt upgrade` messaging instead of `uv tool upgrade --dry-run` plus `nurt update` copy.
- Implemented the real upgrade command against `uv tool upgrade nurt-ai`, added explicit missing-uv remediation, and kept template-asset refresh separate by suggesting `nurt sync template-assets` only as a follow-up.
- Expanded `tests/contracts/test_nurt_cli_contract.py` so the contract now covers `nurt upgrade --dry-run`, rejection of the removed `nurt update` command, the non-mutating startup-check subprocess shape, the real distribution-name upgrade target, and missing-uv failure handling.
- Updated `README.md`, `TODO-FEATURES.md`, `PLAN.md`, `PROGRESS.md`, `docs/LIVING_DOCS.md`, and `docs/ARCHITECTURE.md` to reflect the completed feature `7.0` contract and the next-up feature `8.0` planning target.

## Validation

- `uv run pytest tests/contracts/test_nurt_cli_contract.py` -> 31 passed
- `uv run ruff check src/new_repo_template tests/contracts` -> passed
- `uv run pytest` -> 219 passed

## Outcome

- Feature `7.0` is complete: `nurt upgrade` is now the only supported self-update command, the old `nurt update` surface is gone, the uv package target is correctly aligned to `nurt-ai`, and template-asset sync remains a separate operator-controlled step.
