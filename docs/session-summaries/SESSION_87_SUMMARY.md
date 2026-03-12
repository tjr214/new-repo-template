# Session 87 Summary

## Date and Time

2026-03-12 06:50:03 PM

## Scope

Removed the two legacy updater shell scripts, migrated remaining maintainer/test/docs references to native `nurt` command paths, and archived the completed root `PLAN.md` into a fresh next-cycle stub.

## Inputs

- `PLAN.md`
- `PROGRESS.md`
- `docs/LIVING_DOCS.md`
- `docs/ARCHITECTURE.md`
- `install.sh`
- `tests/contracts/test_installer_scripts_dry_run_contract.py`
- `tests/contracts/test_nurt_cli_contract.py`

## Implementation

- Ran the YELLOW pass by rereading the current plan/docs/contracts, scanning every remaining repository reference to the legacy updater scripts, and using `btca status` plus `btca ask` to sanity-check the native-command-only cleanup direction.
- Removed `.template_scripts/update-opencode.sh` and `.template_scripts/update-bmad-method.sh` now that `nurt tools sync` and `nurt bmad sync` are the supported native implementations.
- Updated `install.sh` so the remaining legacy maintainer bootstrap path now runs repo-local native `nurt` commands for BMAD and tool updates, including dry-run output, instead of invoking deleted shell scripts.
- Removed obsolete updater-script contract coverage from `tests/contracts/test_installer_scripts_dry_run_contract.py` and updated remaining dry-run expectations to assert native `nurt` command usage.
- Archived the completed root `PLAN.md` to `docs/archive/plans/PLAN_2026-03-12_06-50-03_PM.md` and reset the root `PLAN.md` file to the standard next-cycle stub format.

## Verification

- `uv run pytest tests/contracts/test_installer_scripts_dry_run_contract.py tests/contracts/test_nurt_cli_contract.py -q`
- `uv run pytest`
- `uv run ruff check src/new_repo_template tests/contracts`

## Documentation Sync

- Updated `PLAN.md`.
- Updated `PROGRESS.md`.
- Updated `docs/LIVING_DOCS.md`.
- Updated `docs/ARCHITECTURE.md`.

## Outcome

- The repository no longer depends on the two legacy updater shell scripts, native `nurt` commands are now the only supported update path for tools and BMAD, and the completed implementation plan has been archived with a fresh root planning stub ready for the next slice.
