# Session 129 Summary

## Date and Time

2026-03-29 10:13:28 PM

## Scope

Continued feature `10.0` runtime validation, fixed the first real browser/runtime blockers in the generated `web + backend` stack, confirmed the first manual auth-matrix case can now render, cleaned up the temporary runtime repos, and synced the docs.

## Runtime Findings

- Generated repos for all three supported auth combinations scaffolded successfully, installed successfully, passed the built-in Bun/Convex smoke commands, and exposed the expected Docker service endpoints.
- The first manual browser pass (`local=better-auth`, `prod=clerk`) found a real compose/runtime bug: the generated web container was reusing host-installed Bun dependencies inside Linux Docker, which crashed Vite/Rollup.
- The first manual browser pass also found a generated router bug: the route setup produced duplicate `__root__` routes and a blank page in the browser.
- The same pass produced a larger product finding: the current generated web app is still plain Vite + TanStack Router rather than a true TanStack Start app.

## Fixes Applied

- Updated the generated compose templates so local-only source bind mounts and `bun install --frozen-lockfile` now live in `compose.override.yaml` instead of the deployment-oriented base `compose.yaml`.
- Added Docker-managed `bun-install` and `convex-data` volumes for Linux-native Bun dependencies and self-hosted Convex persistence.
- Updated the generated web route template so the index route attaches explicitly beneath the root route, eliminating the duplicate-`__root__` crash.
- Revalidated the compose/router fixes with targeted contract coverage and Ruff.
- Regenerated the first runtime repo and confirmed the browser now renders `nurt.ai fullstack scaffold baseline` for the first manual case.

## Cleanup

- Brought down the active Docker stack.
- Removed the remaining temporary runtime repo after clearing the Docker-created ACL issue on the leftover `node_modules` directory.

## Documentation Sync

- Updated `PROGRESS.md` with the runtime blockers, fixes, and revised next steps.
- Updated `docs/LIVING_DOCS.md` with the compose corrections, first-manual-case result, and the confirmed TanStack Start gap.
- Updated `docs/ARCHITECTURE.md` with the corrected compose-baseline/override design and the generated-router/runtime findings.
- Updated `TODO-FEATURES.md` so feature `10.0` records the runtime fixes and explicitly tracks that the web lane is still not a true TanStack Start implementation.

## Outcome

- The first manual runtime case now renders successfully.
- The remaining auth/runtime cases are still pending.
- The next meaningful implementation discussion should focus on replacing the current Vite + TanStack Router web lane with a real TanStack Start scaffold before RC1 can close the web roadmap item.
