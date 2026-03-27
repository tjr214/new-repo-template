# Session 125 Summary

## Date and Time

2026-03-26 08:51:51 PM

## Scope

Audited the GitHub Actions Node 20 deprecation warning, upgraded the template workflows to Node 24-ready action majors, and opted both live and scaffolded workflows into explicit Node 24 action-runtime validation.

## YELLOW Pass

- Re-read the live CI/release workflows, mirrored foundation workflow templates, current workflow contracts, and the tracker/docs files before editing.
- Ran `btca resources` and `btca status` during the YELLOW pass to confirm there was no existing GitHub Actions-specific project BTCA resource to use for this slice.
- Collected the upstream GitHub action compatibility details from the official action release notes plus the GitHub Actions Node 20 deprecation changelog so the version bumps stayed grounded in official runtime guidance.

## Implementation

- Updated `.github/workflows/ci.yml` and `.github/workflows/release.yml` to use Node 24-ready action majors and set `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true` at workflow scope.
- Updated the mirrored foundation workflow templates under `src/new_repo_template/snapshot_assets/templates/foundation/.github/workflows/` to keep generated repositories aligned with the live workflow baseline.
- Updated `tests/contracts/test_ci_versions_guardrail_contract.py` and `tests/contracts/test_m5_release_hardening_contract.py` so workflow-governance coverage now locks the new action majors and explicit Node 24 opt-in.
- Synced the workflow-maintenance note across `docs/OPTIONAL_SIGNING_PIPELINE.md`, `docs/LIVING_DOCS.md`, `docs/ARCHITECTURE.md`, and `PROGRESS.md`.

## RED / BLUE Coverage

- Expanded the CI workflow contract to assert the Node 24 opt-in flag plus the new checkout/setup-python/cache action majors.
- Expanded the release-workflow hardening contract to assert the Node 24 opt-in flag plus the new checkout/setup-python/upload-artifact/download-artifact/setup-java majors.

## Validation

- `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."`
- `uv run pytest tests/contracts/test_ci_versions_guardrail_contract.py tests/contracts/test_m5_release_hardening_contract.py tests/contracts/test_snapshot_assets_contract.py tests/contracts/test_root_workspace_contract.py`

## Outcome

- The template workflows are now explicitly aligned with GitHub's Node 24 JavaScript-action runtime transition path.
- Generated foundation repos will inherit the same Node 24-ready workflow baseline as the live template repository.
- Snapshot metadata has been refreshed and the targeted workflow/snapshot validation suite passed (14 tests).
