# Session 127 Summary

## Date and Time

2026-03-29 08:08:46 PM

## Scope

Locked the feature `10.0` pre-build architecture for RC1, focusing on `web + backend` local-dev/auth validation, the compose strategy, and the supported local/prod auth-provider matrix.

## YELLOW Pass

- Re-read `PLAN.md`, `PROGRESS.md`, `docs/LIVING_DOCS.md`, `docs/ARCHITECTURE.md`, `TODO-FEATURES.md`, and `docs/session-summaries/SESSION_126_SUMMARY.md` before editing any docs.
- Re-read the current fullstack/auth scaffold surfaces in `src/new_repo_template/scaffold.py` plus the current backend/auth template files under `src/new_repo_template/snapshot_assets/templates/`.
- Ran `btca status` to confirm the current project BTCA state.
- Used `btca ask` to confirm that Clerk development and production instances keep users separate by default.
- Attempted additional BTCA research for self-hosted Convex auth guidance and found that the current `convex-docs` project resource is only an archived stub, so authoritative self-hosted Convex guidance remains a follow-up requirement for implementation YELLOW.

## Locked Decisions

- Feature `10.0` is the next roadmap item and its first implementation slice is `web + backend` local-dev/auth validation.
- Convex is mandatory in all environments.
- Local development always uses self-hosted Convex via the official Docker image in a local compose override.
- Production always uses Convex Cloud.
- The base `compose.yaml` is the deployment baseline, and local development layers on an override file.
- Generated apps should expose a provider-neutral auth boundary rather than hard-coding Clerk widgets.
- The supported RC1 auth combinations are:
  - `local=better-auth`, `prod=clerk`
  - `local=better-auth`, `prod=better-auth`
  - `local=clerk`, `prod=clerk`
- The unsupported combination is `local=clerk`, `prod=better-auth`.
- Default auth posture for the next slice is `local=better-auth`, `prod=clerk`.

## Documentation Sync

- Updated `PROGRESS.md` with the completed planning pass and the next execution steps.
- Updated `docs/LIVING_DOCS.md` with the locked feature `10.0` local/prod topology, compose model, and auth matrix.
- Updated `docs/ARCHITECTURE.md` with the same planning decisions and the current self-hosted Convex documentation risk.
- Updated `TODO-FEATURES.md` to record the locked `10.0` planning decisions and the remaining self-hosted Convex + Clerk verification item.
- Replaced the stub root `PLAN.md` with a comprehensive restart-safe feature `10.0` pre-build plan.

## Outcome

- The repository now has a restart-safe record of the RC1 pre-build decisions, and the next fresh-context session can begin directly with the implementation YELLOW pass for the `web + backend` local-dev/auth slice.
