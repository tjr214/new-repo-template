# Session 37 Summary

## Date and Time

2026-03-02 10:32:13 AM

## Scope

Closed remaining M0 governance task and completed the final M2 implementation items by expanding the web scaffold to a fuller TanStack Start-style baseline and adding shared-package integration for fullstack presets.

## Changes Made

- Ran YELLOW BTCA research:
  - `btca ask -r tanstack-router-start` for minimal TanStack Start app file/script baseline in Bun/Turbo monorepos.
  - `btca ask -r turborepo -r bun` for workspace shared-package modeling and cross-platform reliability.
  - `btca clear` after TanStack resource fetch failure hint, then retried with `btca ask -r tanstack-router-start -r convex-docs` for lightweight web/backend shared-package boundaries.
- Added RED contract assertions in `tests/contracts/test_fullstack_auth_wiring_contract.py` for:
  - expanded web scaffold files (`app.config.ts`, `vite.config.ts`, `tsconfig.json`, `index.html`, `src/routeTree.gen.ts`, styles)
  - shared package scaffold output (`packages/shared/package.json`, `packages/shared/src/index.ts`)
  - web/backend workspace dependency wiring to `@generated/shared`
  - dry-run visibility of new scaffold paths
- Implemented GREEN scaffold/template changes:
  - Updated `src/new_repo_template/scaffold.py` to plan/write expanded web files and fullstack-only shared package outputs.
  - Added new web templates:
    - `src/new_repo_template/snapshot_assets/templates/fullstack/web_app.config.ts`
    - `src/new_repo_template/snapshot_assets/templates/fullstack/web_vite.config.ts`
    - `src/new_repo_template/snapshot_assets/templates/fullstack/web_tsconfig.json`
    - `src/new_repo_template/snapshot_assets/templates/fullstack/web_index.html`
    - `src/new_repo_template/snapshot_assets/templates/fullstack/web_route_tree.gen.ts`
    - `src/new_repo_template/snapshot_assets/templates/fullstack/web_styles.css`
  - Updated existing web templates to consume shared package baseline exports:
    - `src/new_repo_template/snapshot_assets/templates/fullstack/web_main.tsx`
    - `src/new_repo_template/snapshot_assets/templates/fullstack/web_index_route.tsx`
  - Added shared package templates:
    - `src/new_repo_template/snapshot_assets/templates/workspace_packages/shared_package.json`
    - `src/new_repo_template/snapshot_assets/templates/shared/shared_index.ts`
  - Updated workspace manifests:
    - `src/new_repo_template/snapshot_assets/templates/workspace_packages/web_package.json`
    - `src/new_repo_template/snapshot_assets/templates/workspace_packages/backend_package.json`
- Updated planning/tracking docs:
  - `PLAN.md` (M0 canonical-source checkbox complete; M2 remaining tasks complete)
  - `PROGRESS.md`
  - `docs/LIVING_DOCS.md`
  - `docs/ARCHITECTURE.md`

## Verification

- `uv run pytest tests/contracts/test_fullstack_auth_wiring_contract.py` -> pass (3 tests)
- `uv run pytest tests/contracts/test_bun_workspace_install_contract.py tests/contracts/test_turbo_command_smoke_contract.py tests/contracts/test_convex_backend_smoke_contract.py` -> pass (4 tests)
- `uv run pytest` -> pass (87 tests)

## Outcome

M0 is now fully complete, and M2 is fully complete with richer TanStack Start-style web scaffolding plus practical shared-package integration for fullstack presets while preserving credentialless CI-safe contract behavior.
