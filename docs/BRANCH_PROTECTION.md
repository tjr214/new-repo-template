# Branch Protection Guidance

This guide defines the baseline branch-protection policy for this template repository.

## Automation Command

Use `nurt secure-repo` to apply baseline policy to this template repo or any repo generated from it.

Defaults:

- If `--repo` is omitted, the command auto-detects the current repository via `gh repo view`.
- If `--branch` is omitted, the command defaults to `main`.
- If `--required-approvals` is omitted, interactive runs ask for it with default `0`, and `--no-interactive` runs default it to `0` automatically so solo-maintainer repos are not blocked waiting on a second reviewer.

Examples:

- Auto-detect repo/checks and apply protections to `main`:
  - `nurt secure-repo`
- Apply a team-oriented policy that requires one write-access approval:
  - `nurt secure-repo --repo <owner>/<repo> --required-approvals 1`
- Apply protections to an explicit repository (still defaults to `main`):
  - `nurt secure-repo --repo <owner>/<repo>`
- Preview changes without applying:
  - `nurt secure-repo --dry-run --repo <owner>/<repo> --required-check "Tests (ubuntu-latest)" --required-check "Preset Regression Suite" --required-check "Version Baseline Guardrail"`

Command baseline behavior:

- Enables `dependabot_security_updates` at repository level.
- Applies branch protection requiring pull requests, required status checks, up-to-date branches, conversation resolution, and linear history.
- Restricts force pushes and branch deletions.

## Target Branches

- Apply this policy to `main`.
- If release branches are added later, mirror the same required checks there.

## Required Settings

- Enable **Require a pull request before merging**.
- For solo-dev repositories, keep **Required approvals** at `0` so the author can merge once required checks pass.
- For team repositories, set **Required approvals** to `1` or higher with `--required-approvals <n>`.
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
