# Branch Protection Guidance

This guide defines the baseline branch-protection policy for this template repository.

## Automation Script

Use the maintainer script at `.template_scripts/configure-repo-protections.sh` to apply baseline policy to this template repo or any repo generated from it.

Defaults:

- If `--repo` is omitted, the script auto-detects the current repository via `gh repo view`.
- If `--branch` is omitted, the script defaults to `main`.

Examples:

- Auto-detect repo/checks and apply protections to `main`:
  - `sh .template_scripts/configure-repo-protections.sh`
- Apply protections to an explicit repository (still defaults to `main`):
  - `sh .template_scripts/configure-repo-protections.sh --repo <owner>/<repo>`
- Preview changes without applying:
  - `sh .template_scripts/configure-repo-protections.sh --dry-run --repo <owner>/<repo> --required-check "Tests (ubuntu-latest)" --required-check "Preset Regression Suite" --required-check "Version Baseline Guardrail"`

Script baseline behavior:

- Enables `dependabot_security_updates` at repository level.
- Applies branch protection requiring pull requests, required status checks, up-to-date branches, conversation resolution, and linear history.
- Restricts force pushes and branch deletions.

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
