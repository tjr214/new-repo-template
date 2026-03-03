# Regression Suite Policy

This document defines the dedicated regression suite for preset-combination stability during M5 hardening.

## CI Job

- Workflow: `.github/workflows/ci.yml`
- Job name: `Preset Regression Suite`
- Purpose: run high-signal preset-combination contracts in a focused, maintainable job.

## Contract Scope

The preset regression suite runs:

- `tests/contracts/test_required_preset_matrix_contract.py`
- `tests/contracts/test_target_matrix_and_auth_contract.py`
- `tests/contracts/test_fullstack_auth_wiring_contract.py`

These tests cover required preset combinations, target/auth validation boundaries, and fullstack auth-variant wiring stability.

## Local Verification Command

Run the same regression slice locally with:

`uv run pytest tests/contracts/test_required_preset_matrix_contract.py tests/contracts/test_target_matrix_and_auth_contract.py tests/contracts/test_fullstack_auth_wiring_contract.py`

## Maintenance Rules

- Keep this suite focused on preset-combination regressions (not generic unit checks).
- When adding/removing major preset combinations in `PLAN.md`, update this file and the CI job in the same change.
- Keep status-check naming aligned with `docs/BRANCH_PROTECTION.md`.
