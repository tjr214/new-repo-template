# Session 118 Summary

## Date and Time

2026-03-24 07:31:28 PM

## Scope

Completed the first feature `8.0` slice by replacing the legacy branch-protection shell script with a native `nurt secure-repo` command, preserving the existing GitHub automation behavior, making required-approvals prompting explicit for interactive runs, removing the old script from the scaffold/snapshot baseline, and syncing the roadmap/live docs while deferring `nurt ralph` to the next session.

## Inputs

- `TODO-FEATURES.md`
- `PLAN.md`
- `PROGRESS.md`
- `docs/LIVING_DOCS.md`
- `docs/ARCHITECTURE.md`
- `docs/BRANCH_PROTECTION.md`
- `src/new_repo_template/nurt_cli.py`
- `src/new_repo_template/scaffold.py`
- `src/new_repo_template/foundation_manifest.py`
- `src/new_repo_template/snapshot_assets/source_manifest.json`
- `scripts/configure-repo-protections.sh`
- `src/new_repo_template/snapshot_assets/templates/foundation/scripts/configure-repo-protections.sh`
- `tests/contracts/test_installer_scripts_dry_run_contract.py`
- `tests/contracts/test_branch_protection_guidance_contract.py`
- `tests/contracts/test_root_workspace_contract.py`
- `tests/contracts/test_nurt_cli_contract.py`
- `tests/contracts/test_snapshot_assets_contract.py`

## YELLOW Pass

- Re-read the roadmap, active plan, progress tracker, living docs, architecture docs, branch-protection guidance, CLI/scaffold/snapshot files, the legacy protections shell script, and the current branch-protection/foundation contracts before editing.
- Ran `btca status` and `btca resources`, then used `btca ask -r rich-docs` to confirm the recommended Rich patterns for a short prompt-and-summary terminal flow so the interactive approval prompt could stay polished without growing into a mini TUI.
- Locked the slice scope to `nurt secure-repo` only: preserve the existing flags/behavior surface, prompt interactively for required approvals with default `0`, default to `0` automatically under `--no-interactive`, remove the shell script immediately, and leave the `RALPH` conversion for the next session.

## Changes

- Added `src/new_repo_template/repo_security.py` to own secure-repo validation, repo/check auto-detection, branch-protection payload generation, GitHub apply flow, and verification output.
- Extended `src/new_repo_template/nurt_cli.py` with the new `secure-repo` parser/handler plus the interactive required-approvals prompt and non-interactive `0` default behavior.
- Removed `scripts/configure-repo-protections.sh` from the live repo, removed its bundled snapshot copy, removed its source-manifest entry, and updated `src/new_repo_template/scaffold.py` so generated foundations no longer ship the obsolete shell wrapper.
- Updated `tests/contracts/test_installer_scripts_dry_run_contract.py`, `tests/contracts/test_branch_protection_guidance_contract.py`, and `tests/contracts/test_root_workspace_contract.py` to cover the native command surface, the shell-script removal, the docs shift to `nurt secure-repo`, and the trimmed foundation baseline.
- Updated `docs/BRANCH_PROTECTION.md`, `TODO-FEATURES.md`, `PLAN.md`, `PROGRESS.md`, `docs/LIVING_DOCS.md`, and `docs/ARCHITECTURE.md` to reflect the completed secure-repo slice and the deferred `nurt ralph` follow-up.
- Regenerated bundled snapshot metadata with `nurt template-assets validate` so `src/new_repo_template/snapshot_assets/{manifest.json,metadata.json}` match the new foundation baseline and refreshed live docs.

## Validation

- `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."` -> passed
- `uv run pytest tests/contracts/test_nurt_cli_contract.py tests/contracts/test_installer_scripts_dry_run_contract.py tests/contracts/test_branch_protection_guidance_contract.py tests/contracts/test_root_workspace_contract.py tests/contracts/test_snapshot_assets_contract.py` -> 49 passed
- `uv run ruff check src/new_repo_template tests/contracts` -> passed
- `uv run pytest` -> 220 passed

## Outcome

- The supported maintainer path for repository protections is now `nurt secure-repo`, not a scaffolded shell script.
- Generated repos no longer carry `scripts/configure-repo-protections.sh`; they rely on the installed `nurt` command surface instead.
- Feature `8.0` remains open only for the future `nurt ralph` conversion work.
