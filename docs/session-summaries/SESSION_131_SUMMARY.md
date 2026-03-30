# Session 131 Summary

## Date and Time

2026-03-29 11:01:17 PM

## Scope

Executed the TanStack Start replacement plan end-to-end: re-primed the YELLOW context, updated the fullstack web contracts, replaced the fake web lane with a real minimal TanStack Start scaffold, revalidated the repository, and reran the first generated runtime case against the corrected web stack.

## YELLOW Pass

- Re-read `PLAN.md`, `PROGRESS.md`, `docs/LIVING_DOCS.md`, `docs/ARCHITECTURE.md`, `TODO-FEATURES.md`, `docs/session-summaries/SESSION_129_SUMMARY.md`, and `docs/session-summaries/SESSION_130_SUMMARY.md` before changing implementation files.
- Re-read `src/new_repo_template/scaffold.py`, `src/new_repo_template/snapshot_assets/templates/workspace_packages/web_package.json`, the current fullstack web templates, and the relevant fullstack/auth contract suites.
- Ran `date` and `btca status`.
- Used `btca ask` for Start Vite/plugin requirements, minimal file structure, `getRouter()` export expectations, `StartClient` client-entry behavior, route-tree shape, package-script/router-generation flow, and the creator-vs-mirrored-template strategy question.

## RED

- Updated `tests/contracts/test_fullstack_auth_wiring_contract.py` so the web lane must now scaffold real Start signals instead of the old placeholder shape.
- The contract now requires `@tanstack/react-start`, `@tanstack/react-start/plugin/vite`, `src/client.tsx`, `getRouter()`, `HeadContent`, `Scripts`, and `createFileRoute("/")`.
- The contract also now rejects the old `src/main.tsx`, `app.config.ts`, and `index.html` pattern as Start proof.
- Ran `uv run pytest tests/contracts/test_fullstack_auth_wiring_contract.py` and confirmed the expected RED failures before implementation.

## GREEN

- Updated `src/new_repo_template/scaffold.py` so web projects now scaffold `src/client.tsx` and no longer scaffold `app.config.ts`, `index.html`, or `src/main.tsx`.
- Updated `src/new_repo_template/snapshot_assets/templates/workspace_packages/web_package.json` to include `@tanstack/react-start`, `@vitejs/plugin-react`, current React type packages, and Start-aligned app scripts.
- Added `src/new_repo_template/snapshot_assets/templates/fullstack/web_client.tsx` with an explicit `StartClient` hydration entry.
- Updated the web router template to export `getRouter()`.
- Updated the root-route template to render a real document shell with `HeadContent`, `Outlet`, and `Scripts`.
- Updated the index route template to use `createFileRoute("/")`.
- Updated the Vite config template to use `tanstackStart()` before `viteReact()`.
- Replaced the static route-tree template with a valid minimal generated Start-style route-tree baseline.
- Removed the obsolete fake `web_main.tsx`, `web_app.config.ts`, and `web_index.html` templates.

## BLUE

- Re-ran `uv run pytest tests/contracts/test_fullstack_auth_wiring_contract.py tests/contracts/test_target_matrix_and_auth_contract.py` (24 passed).
- Re-ran `uv run ruff check src/new_repo_template tests/contracts`.
- Refreshed bundled snapshot metadata with `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."`.
- Re-ran the full repository suite with `uv run pytest` (245 passed).

## Runtime Revalidation

- Regenerated a fresh in-repo runtime test repo for `local=better-auth`, `prod=clerk`.
- Ran `bun install --frozen-lockfile` in the generated repo.
- Ran the generated root smoke commands plus the real web `build:app` command.
- Brought up the generated stack with `docker compose up -d --build`.
- Verified `http://127.0.0.1:3000` serves the baseline page content from the Start-based scaffold.
- Brought the stack down and removed the temporary runtime repo afterward.

## Documentation Sync

- Updated `PLAN.md` to mark the TanStack Start replacement plan complete.
- Updated `PROGRESS.md` with the completed YELLOW/RED/GREEN/BLUE work and the successful first runtime revalidation.
- Updated `TODO-FEATURES.md` so the TanStack Start item and the local web/backend Docker-dev item are now checked complete.
- Updated `docs/LIVING_DOCS.md` and `docs/ARCHITECTURE.md` so they describe the new real Start baseline instead of the old fake placeholder lane.

## Outcome

- The web lane now scaffolds a real minimal TanStack Start app.
- The first regenerated runtime case passes again on the corrected Start-based baseline.
- The next session can resume the remaining RC1 runtime/auth matrix on the corrected web stack instead of the old placeholder implementation.
