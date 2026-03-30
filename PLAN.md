# React Foundations And Component Ownership Plan

**Last Updated:** 2026-03-30 07:54:25 PM
**Status:** Completed
**Most Recent Session Summary:** `docs/session-summaries/SESSION_139_SUMMARY.md`

## Goal

Build the next implementation cycle around feature `10.0` and feature `11.0` so the repo can move from planning into concrete work without reopening already-settled product and architecture decisions.

The immediate execution target is:

- feature `10.0`: lock and implement the `shadcn/ui` ownership/tooling model for web
- feature `11.0`: implement the first shared React-foundation slice plus the first desktop React hello-world renderer

This plan is intentionally restart-safe and assumes the next agent may begin from a blank context window.

## Post-Completion Testing Notes

- The supported `web+backend` auth matrix now has real runtime evidence for `better-auth/better-auth`, `better-auth/clerk`, and `clerk/clerk`.
- The desktop lane now has real package/start evidence after the follow-up Forge/TanStack dependency fixes.
- Mobile iOS validation is now fully green locally after installing the newer iOS simulator runtime.
- Android TV validation no longer has the missing-Java blocker after installing Java 17 and using it explicitly for Android runs; the remaining gap is stronger app-run/device confirmation, not basic tool availability.

## Locked Decisions

- `shadcn/ui` is the default web component foundation.
- Shared design tokens are the real cross-target visual foundation.
- Mobile and TV keep native presentation layers.
- Desktop must participate in the shared React model.
- Desktop should use `Electron Forge + Vite + React`.
- Desktop should use `@tanstack/react-router` with `createHashHistory()`.
- Desktop should not use `TanStack Start` as the default renderer framework.
- The first desktop React renderer only needs a simple hello-world baseline.
- Shared foundations should preserve the same core style-and-feel identity across frontend targets.
- Shared foundations should remain flexible enough for platform-specific capabilities.
- Shared foundations should include design tokens, theme contracts, branding assets, shared copy/demo content, route intent, domain types/schemas, API/auth contracts, and shared hooks/utilities.
- Platform-specific layers should include rendered component implementations, layout mechanics, platform input/navigation behavior, motion details, storage/notification integrations, and native bridge/device APIs.
- `Welcome To Nurt` is a later cross-frontend demo item, not part of the first desktop React hello-world slice.
- `nurt` should keep deterministic ownership of scaffolded web component files instead of invoking the `shadcn` CLI during normal `nurt new` runs.
- The `shadcn` CLI should still be supported as a maintainer tool and integrated into `nurt sync tools`.
- `Effect` is intentionally not part of the default RC1 baseline for the generated React/shared stack.

## Explicit Non-Goals

- Do not adopt `Effect` as a default library for the next implementation slice.
- Do not make `nurt new` shell out to the live `shadcn` CLI at user runtime.
- Do not attempt to create one universal rendered component library that spans web, desktop, mobile, and TV.
- Do not move desktop onto `TanStack Start`.
- Do not build the full `Welcome To Nurt` cross-frontend demo during the first desktop React migration slice.
- Do not overbuild shared packages before the first concrete shared-foundation slice is working.

## Preferred Minimal Implementation Shape

- Keep the first shared foundation as small as possible.
- Introduce a new `packages/design-tokens` package for cross-target tokens and theme primitives.
- Reuse `packages/shared` for the first shared copy, route intent, types/schemas, auth/runtime abstractions, and generic hooks/utilities instead of creating multiple new support packages immediately.
- Keep web UI implementation web-specific.
- Keep native and desktop rendered UI layers target-specific.

## Fresh-Context Restart

- [x] Run `date "+%Y-%m-%d %I:%M:%S %p"` and record the current timestamp before making new edits.
- [x] Read `PLAN.md` fully.
- [x] Read `PROGRESS.md` fully.
- [x] Read `docs/LIVING_DOCS.md` fully.
- [x] Read `docs/ARCHITECTURE.md` fully.
- [x] Read `TODO-FEATURES.md` fully.
- [x] Read the latest session summary: `docs/session-summaries/SESSION_136_SUMMARY.md`.
- [x] Read `btca.config.jsonc` and `docs/BTCA_RESOURCES.md` so BTCA state and docs are understood before any new changes.
- [x] Re-read the current implementation files that are most likely to change:
  - `src/new_repo_template/scaffold.py`
  - `src/new_repo_template/nurt_cli.py`
  - `src/new_repo_template/tool_sync_runner.py`
  - `src/new_repo_template/sync_ops.py`
  - `src/new_repo_template/tool_sync_tui.py`
- [x] Re-read the current template files that define the existing web, desktop, and shared baselines:
  - `src/new_repo_template/snapshot_assets/templates/workspace_packages/web_package.json`
  - `src/new_repo_template/snapshot_assets/templates/workspace_packages/desktop_package.json`
  - `src/new_repo_template/snapshot_assets/templates/workspace_packages/shared_package.json`
  - `src/new_repo_template/snapshot_assets/templates/fullstack/web_client.tsx`
  - `src/new_repo_template/snapshot_assets/templates/fullstack/web_root_route.tsx`
  - `src/new_repo_template/snapshot_assets/templates/fullstack/web_index_route.tsx`
  - `src/new_repo_template/snapshot_assets/templates/fullstack/web_router.tsx`
  - `src/new_repo_template/snapshot_assets/templates/desktop/desktop_index.html`
  - `src/new_repo_template/snapshot_assets/templates/desktop/desktop_main.ts`
  - `src/new_repo_template/snapshot_assets/templates/desktop/desktop_renderer.ts`
  - `src/new_repo_template/snapshot_assets/templates/shared/shared_index.ts`
- [x] Re-read the most relevant contract suites before changing implementation:
  - `tests/contracts/test_nurt_cli_contract.py`
  - `tests/contracts/test_tool_sync_runner_contract.py`
  - `tests/contracts/test_root_workspace_contract.py`
  - `tests/contracts/test_desktop_runtime_smoke_contract.py`
  - `tests/contracts/test_bun_workspace_install_contract.py`
  - `tests/contracts/test_turbo_command_smoke_contract.py`
  - `tests/contracts/test_fullstack_auth_wiring_contract.py`
- [x] Run `btca status`.
- [x] Re-run the planning-critical BTCA lookups with plain/simple query strings before final implementation choices:
  - `btca ask -r shadcn-ui -q "For a start monorepo, what is the normal shadcn CLI setup flow and where do generated components typically live" --sub-agent`
  - `btca ask -r electron-forge -r tanstack-router-start -q "For an Electron desktop app with a React renderer, is the normal architecture Electron Forge plus Vite plus React plus TanStack Router without TanStack Start" --sub-agent`
- [x] Confirm that no new user-authored changes conflict with the planned implementation before editing the touched files.

## Execution Order

- [x] Execute feature `10.0` first: finalize and implement the `shadcn/ui` ownership/tooling model.
- [x] Execute the first feature `11.0` slice second: shared foundations plus desktop React hello world.
- [x] Defer feature `12.0` `Welcome To Nurt` implementation until feature `10.0` and the first feature `11.0` slice are real and validated.

## YELLOW

- [x] Confirm the exact owned web component layout for the first implementation slice.
  - Recommended default: follow the upstream `shadcn` Start-monorepo model conceptually by keeping app config in the web lane and routing generated/owned UI files into a shared workspace UI location, but keep `nurt`'s scaffold deterministic rather than invoking the CLI during `nurt new`.
- [x] Confirm the minimal package boundary for the first shared-foundation implementation.
  - Recommended default: add `packages/design-tokens` and keep first-wave shared copy/contracts/utilities in `packages/shared`.
- [x] Confirm how `nurt sync tools` should install/update the `shadcn` CLI on supported maintainer machines.
- [x] Confirm the exact desktop React baseline file structure and whether the renderer should use a single root route or a tiny two-route baseline.
  - Recommended default: one simple hello-world route first, with router wiring already in place.
- [x] Confirm the validation surface for the slice before RED work begins.

## RED: Feature 10.0

- [x] Add or update contract coverage for `nurt sync tools` so the `shadcn` CLI appears in dry-run planning and non-dry-run tool execution behavior.
- [x] Add or update contract coverage for deterministic web component ownership so the scaffolded web lane has the expected owned component/config layout without runtime CLI shell-outs.
- [x] Add or update contract coverage for any new shared web UI package or config files introduced by the chosen `shadcn` ownership model.

## GREEN: Feature 10.0

- [x] Implement maintainer-side `shadcn` CLI support in the native tool-sync path.
  - Update `src/new_repo_template/tool_sync_runner.py`.
  - Update any sync orchestration or TUI layers that surface tool status/output.
- [x] Implement the deterministic `shadcn/ui` ownership model for generated web projects.
  - Add the required scaffold files/config for the owned web UI foundation.
  - Keep `nurt new` free of live `shadcn` CLI runtime dependencies.
- [x] Document how `nurt` owns, updates, and extends the web component foundation.

## BLUE: Feature 10.0

- [x] Re-run the targeted contract suites for tool sync, CLI behavior, and scaffold layout.
- [x] Re-run `uv run ruff check src/new_repo_template tests/contracts`.
- [x] Re-run `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."` if template assets/manifests changed.
- [x] Re-run the full repository suite with `uv run pytest` after the slice is stable.

## RED: Feature 11.0 First Slice

- [x] Add or update contract coverage for the new shared-foundation package boundary.
- [x] Add or update contract coverage for the desktop React renderer migration.
- [x] Add or update runtime smoke expectations so the desktop target proves React-renderer viability instead of the old plain-DOM baseline.

## GREEN: Feature 11.0 First Slice

- [x] Add `packages/design-tokens` as the first concrete shared-foundation package.
  - Export the first minimal token/theme contract in a target-agnostic TypeScript shape.
- [x] Extend `packages/shared` only as needed for the first wave of shared copy/contracts/utilities.
- [x] Upgrade the desktop scaffold from plain DOM scripting to `Electron Forge + Vite + React`.
- [x] Wire `@tanstack/react-router` into the desktop renderer with `createHashHistory()`.
- [x] Keep the first desktop React UI intentionally minimal: simple hello-world content only.
- [x] Ensure the desktop slice is compatible with the later cross-frontend `Welcome To Nurt` work rather than baking in throwaway structure.

## BLUE: Feature 11.0 First Slice

- [x] Re-run the targeted desktop/shared-foundation contracts and smoke suites.
- [x] Re-run `uv run ruff check src/new_repo_template tests/contracts`.
- [x] Re-run `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."` if template assets/manifests changed.
- [x] Re-run the full repository suite with `uv run pytest` after the slice is stable.

## Documentation Sync

- [x] Update `PROGRESS.md` as each slice moves through YELLOW, RED, GREEN, and BLUE.
- [x] Update `docs/LIVING_DOCS.md` to reflect the final component-foundation and desktop React implementation state.
- [x] Update `docs/ARCHITECTURE.md` to reflect the final package boundaries and renderer architecture that were actually implemented.
- [x] Update `TODO-FEATURES.md` to check off any completed planning or implementation items.
- [x] Create a new session summary in `docs/session-summaries/` for each completed implementation cycle; never overwrite an existing summary.

## Validation Commands

- [x] Use `btca status` during YELLOW.
- [x] Use the two planning-critical `btca ask` commands from the restart section during YELLOW before final implementation choices.
- [x] Run targeted `pytest` suites for the touched contracts before full-suite validation.
- [x] Run `uv run ruff check src/new_repo_template tests/contracts`.
- [x] Run `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."` whenever scaffold templates or snapshot manifests change.
- [x] Run `uv run pytest` before closing the slice.

## Ready-To-Resume Summary

- [x] Resume with feature `10.0`, not feature `12.0`.
- [x] Treat deterministic `shadcn` ownership plus maintainer CLI support as the first concrete implementation target.
- [x] After that, move immediately into the first feature `11.0` slice: `packages/design-tokens`, minimal shared exports, and desktop React hello world.
- [x] Do not reopen already-locked decisions unless the new YELLOW pass reveals a direct upstream/tooling contradiction.
