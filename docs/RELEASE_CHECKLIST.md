# Release Checklist

Use this checklist before each phased rollout.

## M4 carryover gate

These manual items must be complete before release sign-off:

- Android TV Emulator run completed and logged in `apps/tv/TV_VALIDATION_LOG.md`.
- NVIDIA Shield run completed and logged in `apps/tv/TV_VALIDATION_LOG.md`.
- Remote-primary navigation and keyboard/mouse/gamepad fallback checks marked pass from run evidence.

## Required CI gates

- `Tests (ubuntu-latest)` passing
- `Tests (macos-latest)` passing
- `Tests (windows-latest)` passing
- `Preset Regression Suite` passing
- `Version Baseline Guardrail` passing

## Dependency/versioning gates

- `uv run nurt versions check --check-lockfiles --check-latest` passes.
- Baseline metadata and lockfiles are committed for dependency update slices.

## Signing gate (optional)

- If release requires signed artifacts, follow `docs/OPTIONAL_SIGNING_PIPELINE.md`.
- If signing is not required for the release phase, confirm unsigned distribution policy is acceptable for target audience.

## Documentation synchronization

- `PLAN.md`, `PROGRESS.md`, `docs/LIVING_DOCS.md`, and `docs/ARCHITECTURE.md` updated in same release PR.
- Session summary added under `docs/session-summaries/` for the final release-prep slice.
