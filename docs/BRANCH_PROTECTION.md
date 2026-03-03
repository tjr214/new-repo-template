# Branch Protection Guidance

This guide defines the baseline branch-protection policy for this template repository.

## Target Branches

- Apply this policy to `main`.
- If release branches are added later, mirror the same required checks there.

## Required Settings

- Enable **Require a pull request before merging**.
- Enable **Require status checks to pass before merging**.
- Enable **Require branches to be up to date before merging**.
- Enable **Require conversation resolution before merging**.
- Enable **Require linear history**.
- Restrict force pushes and branch deletions.

## Required Status Checks

Mark these checks as required:

- `Tests (ubuntu-latest)`
- `Tests (macos-latest)`
- `Tests (windows-latest)`
- `Preset Regression Suite`
- `Version Baseline Guardrail`

## Advisory (Non-Blocking) Check

Keep this job visible but **do not require it**:

- `Secret Scan (Advisory)`

Reason: this job is intentionally configured with `continue-on-error: true` to surface findings without blocking baseline delivery.

## Maintenance Notes

- `Tests (windows-latest)` is intentionally a focused Windows-critical lane (workspace install + backend/desktop/turbo/python command smoke contracts) to keep native Windows validation fast and reliable.
- If CI job names change in `.github/workflows/ci.yml`, update this file in the same PR.
- Keep this guidance aligned with `PLAN.md` M5 hardening tasks and `PROGRESS.md` status.
