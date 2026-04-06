# Feature 11 Shared React Validation Plan

**Last Updated:** 2026-04-06 03:23:56 PM
**Status:** Completed
**Most Recent Session Summary:** `docs/session-summaries/SESSION_141_SUMMARY.md`

## Goal

Validate and harden feature `11.0` across `web`, `desktop`, `mobile`, and `tv` so the shared React foundation is real, boundary-safe, and ready to support later `Welcome To Nurt` work without over-coupling the targets.

## Completion Summary

- Added `tests/contracts/test_shared_react_boundaries_contract.py` to enforce shared-package import boundaries, web-owned route ownership, non-web exclusion from `@generated/ui`, and `mobile`/`tv` shared-package bootstrap.
- Added a matching add-mode regression in `tests/contracts/test_nurt_add_contract.py` so `nurt add --target mobile` now bootstraps `packages/shared` when needed.
- Updated `src/new_repo_template/scaffold.py` and `src/new_repo_template/add_mode.py` so `packages/shared` now bootstraps for `mobile` and `tv` in both fresh scaffold and add-mode flows.
- Updated the generated mobile and TV package manifests plus starter app templates so both targets now consume `@generated/shared` for shared non-visual frontend copy while leaving rendering/input behavior target-specific.
- Refreshed bundled snapshot metadata with `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."`.
- Revalidated the targeted slice plus the full repository suite: targeted shared-react validation passed (35 tests), `ruff` passed, and `uv run pytest` passed (248 tests).

## Next Likely Target

- Discuss and lock feature `12.0` before building the cross-frontend `Welcome To Nurt` demo.

## Locked Decisions

- [x] Treat feature `11.0` as a four-target validation item covering `web`, `desktop`, `mobile`, and `tv`.
- [x] Keep `packages/shared` renderer-agnostic and safe for React Native/TV import.
- [x] Keep `packages/design-tokens` cross-target only if it remains plain data/contracts and React Native-safe.
- [x] Keep `packages/ui` web-owned for now.
- [x] Keep TanStack Start route files, route-tree generation, and router ownership inside `apps/web`.
- [x] Keep desktop router wiring inside the desktop app, using `@tanstack/react-router` plus `createHashHistory()`.
- [x] Keep mobile and TV app entry/navigation local to those targets even if route intent data is shared.
- [x] Keep rendered components, layout mechanics, storage/notification integrations, native bridges/device APIs, and runtime provider wiring target-specific.
- [x] Keep TV focus handling and remote navigation TV-specific.
- [x] Preserve the shared import rule: shared packages must not import `react-dom`, browser globals, `electron`, or Expo/React Native native runtime APIs.
- [x] Require contract proof and workspace proof for all four targets, with the strongest practical runtime proof captured per target.
- [x] Defer feature `12.0` until feature `11.0` validation and boundary enforcement are complete.

## Explicit Non-Goals

- [x] Do not build the `Welcome To Nurt` demo in this slice.
- [x] Do not create a universal rendered component layer spanning web, desktop, mobile, and TV.
- [x] Do not move TanStack Start route files or generated route trees into shared packages.
- [x] Do not move Electron main/preload/IPC concerns into shared packages.
- [x] Do not move TV focus or remote interaction into broad cross-platform shared packages.
- [x] Do not widen `packages/design-tokens` with renderer-specific styling/runtime behavior.
- [x] Do not add new BTCA resources unless a later YELLOW pass proves they are missing and the user explicitly confirms them.

## Fresh-Context Restart

- [ ] Run `date "+%Y-%m-%d %I:%M:%S %p"` and record the timestamp before making new edits.
- [ ] Read `PLAN.md` fully.
- [ ] Read `PROGRESS.md` fully.
- [ ] Read `docs/LIVING_DOCS.md` fully.
- [ ] Read `docs/ARCHITECTURE.md` fully.
- [ ] Read `TODO-FEATURES.md` fully.
- [ ] Read the latest session summary: `docs/session-summaries/SESSION_140_SUMMARY.md`.
- [ ] Run `btca status`.
- [ ] Re-run the planning-critical BTCA lookups with plain/simple queries before final implementation choices:
  - [ ] `btca ask -r react-docs -q "For code shared between web React and React Native, what assumptions should be avoided so shared modules stay renderer agnostic" --sub-agent`
  - [ ] `btca ask -r tanstack-router-start -q "For TanStack Start on web, should route definitions stay in the web app rather than in a shared package" --sub-agent`
  - [ ] `btca ask -r electron-forge -r electron -q "For an Electron Forge app with a React renderer, what should stay in Electron specific code rather than shared frontend packages" --sub-agent`
  - [ ] `btca ask -r react-native-docs -r expo-docs -q "For Expo React Native apps, what kinds of shared modules are safe to reuse across web desktop mobile and tv without DOM or native runtime assumptions" --sub-agent`
  - [ ] `btca ask -r react-native-tvos -r expo-tv-config -q "For React Native TV apps, should focus handling and remote navigation stay platform specific rather than in shared cross platform packages" --sub-agent`
- [ ] Re-read the most relevant implementation files before editing:
  - [ ] `src/new_repo_template/scaffold.py`
  - [ ] `src/new_repo_template/add_mode.py`
- [ ] Re-read the relevant scaffold templates before editing:
  - [ ] `src/new_repo_template/snapshot_assets/templates/workspace_packages/shared_package.json`
  - [ ] `src/new_repo_template/snapshot_assets/templates/workspace_packages/design_tokens_package.json`
  - [ ] `src/new_repo_template/snapshot_assets/templates/workspace_packages/ui_package.json`
  - [ ] `src/new_repo_template/snapshot_assets/templates/workspace_packages/web_package.json`
  - [ ] `src/new_repo_template/snapshot_assets/templates/workspace_packages/desktop_package.json`
  - [ ] `src/new_repo_template/snapshot_assets/templates/workspace_packages/desktop_package_with_shared.json`
  - [ ] `src/new_repo_template/snapshot_assets/templates/workspace_packages/mobile_package.json`
  - [ ] `src/new_repo_template/snapshot_assets/templates/workspace_packages/tv_package.json`
  - [ ] `src/new_repo_template/snapshot_assets/templates/shared/shared_index.ts`
  - [ ] `src/new_repo_template/snapshot_assets/templates/design_tokens/design_tokens_index.ts`
  - [ ] `src/new_repo_template/snapshot_assets/templates/ui/ui_index.ts`
  - [ ] `src/new_repo_template/snapshot_assets/templates/ui/ui_button.tsx`
  - [ ] `src/new_repo_template/snapshot_assets/templates/fullstack/web_client.tsx`
  - [ ] `src/new_repo_template/snapshot_assets/templates/fullstack/web_router.tsx`
  - [ ] `src/new_repo_template/snapshot_assets/templates/fullstack/web_root_route.tsx`
  - [ ] `src/new_repo_template/snapshot_assets/templates/fullstack/web_index_route.tsx`
  - [ ] `src/new_repo_template/snapshot_assets/templates/fullstack/web_route_tree.gen.ts`
  - [ ] `src/new_repo_template/snapshot_assets/templates/desktop/desktop_app.ts`
  - [ ] `src/new_repo_template/snapshot_assets/templates/desktop/desktop_router.ts`
  - [ ] `src/new_repo_template/snapshot_assets/templates/desktop/desktop_renderer_with_shared.ts`
  - [ ] `src/new_repo_template/snapshot_assets/templates/mobile/mobile_app.tsx`
  - [ ] `src/new_repo_template/snapshot_assets/templates/tv/tv_app.tsx`
- [ ] Re-read the most relevant contract suites before editing:
  - [ ] `tests/contracts/test_fullstack_auth_wiring_contract.py`
  - [ ] `tests/contracts/test_desktop_scaffold_contract.py`
  - [ ] `tests/contracts/test_desktop_runtime_smoke_contract.py`
  - [ ] `tests/contracts/test_mobile_tv_scaffold_contract.py`
  - [ ] `tests/contracts/test_mobile_tv_runtime_smoke_contract.py`
  - [ ] `tests/contracts/test_mobile_tv_setup_docs_contract.py`
  - [ ] `tests/contracts/test_tv_input_hid_contract.py`
  - [ ] `tests/contracts/test_shared_infra_packages_contract.py`
  - [ ] `tests/contracts/test_bun_workspace_install_contract.py`

## Validation Matrix

- [x] `web` must consume the shared non-visual foundation while keeping TanStack Start route ownership, route-tree generation, and browser/runtime wiring inside the web app.
- [x] `desktop` must consume the shared non-visual foundation while keeping Electron main/preload/IPC/window/runtime wiring inside the desktop app.
- [x] `mobile` must be a safe consumer of `@generated/shared`, and may consume `@generated/design-tokens` only if the token package remains plain data and React Native-safe.
- [x] `tv` must be a safe consumer of `@generated/shared`, and may consume `@generated/design-tokens` only if the token package remains plain data and React Native-safe.
- [x] `packages/ui` must remain a web-only dependency until a truly renderer-neutral UI case exists.
- [x] Shared packages must remain free of DOM globals, `react-dom`, Electron imports, and native module assumptions.
- [x] TV focus and remote navigation behavior must remain target-local and must not move into broad shared packages.

## YELLOW

- [x] Confirm the current shared-package export surface and identify every existing host/runtime assumption in `packages/shared` and `packages/design-tokens`.
- [x] Confirm whether `mobile` and `tv` can consume `@generated/design-tokens` immediately without forcing renderer-specific styling/runtime logic into that package.
- [x] Confirm that the current scaffold/add-mode paths will create or update shared package dependencies consistently for `nurt new` and `nurt add` if `mobile` and `tv` begin consuming the shared non-visual foundation now.
- [x] Confirm the exact target-owned boundaries before RED work begins:
  - [x] web-owned route files and router generation
  - [x] desktop-owned Electron lifecycle/preload/IPC and renderer routing
  - [x] mobile-owned app entry/navigation/runtime integrations
  - [x] TV-owned focus and remote navigation behavior

## RED

- [x] Add a new contract suite for shared React boundaries, likely `tests/contracts/test_shared_react_boundaries_contract.py`.
- [x] In that suite, add explicit assertions that shared packages do not import DOM globals, `react-dom`, `electron`, or Expo/React Native native runtime APIs.
- [x] Add contract assertions that TanStack Start route definitions and generated route trees remain in the web app package rather than shared packages.
- [x] Add contract assertions that `packages/ui` remains web-only and is not wired into desktop/mobile/tv manifests.
- [x] Expand scaffold/runtime contracts to assert the intended shared dependency wiring for `web`, `desktop`, `mobile`, and `tv`.
- [x] Add contract coverage that `tv` keeps focus/remote behavior target-local and does not depend on a broad shared focus abstraction.

## GREEN

- [x] Refactor `packages/shared` exports only as needed so they stay pure JS/TS or React-core only and remain safe for React Native/TV import.
- [x] Refactor `packages/design-tokens` only as needed so any cross-target exports remain plain data/contracts and avoid renderer-specific behavior.
- [x] Wire `mobile` and `tv` manifests/templates to consume `@generated/shared` for non-visual shared foundations.
- [x] Wire `mobile` and `tv` to consume `@generated/design-tokens` only if the YELLOW/RED pass confirms the package stays React Native-safe.
- [x] Keep `packages/ui` limited to web templates and manifests.
- [x] Keep TanStack Start routes, route-tree generation, and router creation in `apps/web`.
- [x] Keep desktop router wiring and all Electron-specific runtime code local to the desktop target.
- [x] Keep mobile runtime integrations local to the mobile target.
- [x] Keep TV focus and remote navigation logic local to the TV target.
- [x] Update `src/new_repo_template/add_mode.py` if the shared dependency/package bootstrapping rules change for `mobile` and `tv`.

## BLUE

- [x] Run the targeted shared-react validation slice:
  - [x] `uv run pytest tests/contracts/test_shared_react_boundaries_contract.py tests/contracts/test_fullstack_auth_wiring_contract.py tests/contracts/test_desktop_scaffold_contract.py tests/contracts/test_desktop_runtime_smoke_contract.py tests/contracts/test_mobile_tv_scaffold_contract.py tests/contracts/test_mobile_tv_runtime_smoke_contract.py tests/contracts/test_tv_input_hid_contract.py tests/contracts/test_shared_infra_packages_contract.py tests/contracts/test_bun_workspace_install_contract.py`
- [x] Run `uv run ruff check src/new_repo_template tests/contracts`.
- [x] Run `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."` if templates or snapshot metadata change.
- [x] Run `uv run pytest` after the targeted slice is stable.

## Documentation Sync

- [x] Update `PROGRESS.md` as the feature `11.0` slice moves through YELLOW, RED, GREEN, and BLUE.
- [x] Update `docs/LIVING_DOCS.md` to reflect the final shared-boundary enforcement and all-target validation state.
- [x] Update `docs/ARCHITECTURE.md` to reflect the final shared-vs-target-owned package boundaries that were actually implemented.
- [x] Update `TODO-FEATURES.md` to check off any newly completed feature `11.0` discussion or implementation items.
- [x] Create a new session summary in `docs/session-summaries/` when the implementation slice closes; never overwrite an existing summary.

## Exact Next Execution Steps

- [x] Start with RED, not new UI work.
- [x] Create the shared-boundary contract suite first.
- [x] Make the smallest template and scaffold changes needed to satisfy the new boundary assertions.
- [x] Re-run the targeted contract slice before touching broader validation.
- [x] Only after the contracts are green should the work expand into any additional runtime-smoke confirmation.
