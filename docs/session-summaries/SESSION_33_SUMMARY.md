# Session 33 Summary

## Date and Time

2026-03-01 04:57:36 PM

## Scope

Completed the next M1 closure slice: Python baseline command execution contracts, user-doc alignment to `nurt`-first bootstrap flow, and cross-platform CI smoke-check wiring.

## Changes Made

- Ran YELLOW BTCA lookup via `btca ask -r turborepo` to confirm root `packageManager` metadata requirement for Turborepo workspace resolution.
- Expanded Python lane contract coverage in `tests/contracts/test_python_lane_contract.py`:
  - scaffolds Python target and executes baseline command set
  - validates `uv sync --group dev`, `uv run pytest`, `uv run ruff check .`, and `uv run mypy src`
- Updated Python lane scaffold metadata template:
  - `src/new_repo_template/snapshot_assets/templates/python_lane_pyproject.toml`
  - switched dev dependency declaration to `[dependency-groups].dev` for uv group-command compatibility
- Strengthened root workspace template for Turbo resolution:
  - `src/new_repo_template/snapshot_assets/templates/root_package.json`
  - includes `packageManager: bun@1.3.10` and `devDependencies.turbo: ^2.8.12`
- Updated CI workflow for explicit cross-platform smoke checks:
  - `.github/workflows/ci.yml`
  - adds Bun setup on matrix runners and executes targeted smoke contracts
- Expanded CI workflow contract assertions:
  - `tests/contracts/test_ci_versions_guardrail_contract.py`
  - now checks OS matrix scope, Bun setup, smoke-contract step wiring, and existing versions guardrail command
- Updated user-facing bootstrap documentation:
  - `README.md` now documents canonical `nurt` install/new flow and marks `install.sh` as legacy/maintainer path
- Synced implementation tracking docs:
  - `PLAN.md`
  - `PROGRESS.md`
  - `docs/LIVING_DOCS.md`
  - `docs/ARCHITECTURE.md`

## Verification

- `uv run pytest tests/contracts/test_python_lane_contract.py tests/contracts/test_ci_versions_guardrail_contract.py tests/contracts/test_bun_workspace_install_contract.py tests/contracts/test_turbo_command_smoke_contract.py` -> pass (7 tests)
- `uv run pytest` -> pass (83 tests)

## Outcome

Python-target baseline command viability is now contract-enforced, CI now wires explicit cross-platform smoke checks for script/tooling execution, and user-facing docs are aligned to the global `nurt` bootstrap flow (no script-first default guidance).
