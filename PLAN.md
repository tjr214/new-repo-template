# Feature 13 Operator Console Plan

**Last Updated:** 2026-04-07 09:18:58 PM
**Status:** Planning Locked / Ready for RED
**Latest Session Summary:** `docs/session-summaries/SESSION_144_SUMMARY.md`
**Current Roadmap Item:** `13.0 UPDATE THE "WELCOME TO NURT" APP TO USE THE CHOSEN COMPONENT APPROACH`

## Goal

Implement feature `13.0` as a cross-frontend `Operator Console` redesign of `Welcome To Nurt` that applies the chosen component strategy across `web`, `desktop`, `mobile`, and `tv` without violating the feature `11.0` ownership boundaries.

## Locked Decisions

- The redesign direction is `Operator Console`.
- `web`, `desktop`, `mobile`, and `tv` are all in scope for this slice.
- Execution should proceed `web` first, but the slice does not close until desktop/mobile/TV are updated too.
- `packages/ui` remains web-owned and continues to be the `shadcn/ui`-style implementation layer.
- Shared packages continue to own only renderer-safe tokens, content, and semantic structure.
- Desktop remains `Electron Forge + Vite + React`, not React Native.
- Mobile and TV remain Expo/React Native apps with target-local rendered components and normal native capability access through Expo/RN integrations.
- Desktop/mobile/TV should match the same system language through target-local components rather than by importing `@generated/ui`.
- TV must keep focus-first, remote-primary behavior target-local.

## Exact Information Architecture

- Hero: what the generated repo is and why it is ready.
- Foundations: what ships already wired.
- Build Path: how to start shaping the product.
- Actions: primary and secondary next moves.
- Footer/Caption: shared-intent statement that each target remains runtime-local.
- TV mapping: focusable rail on the left, richer detail panel on the right.

## Locked Component Inventory

- Shared content/data shape:
  - `NURT_WELCOME_HERO`
  - `NURT_WELCOME_SECTIONS`
  - `NURT_WELCOME_ACTIONS`
  - `NURT_WELCOME_HIGHLIGHTS`
  - `NURT_GETTING_STARTED_STEPS`
  - TV-specific structured detail content as needed
- Web-owned UI components in `packages/ui`:
  - `HeroPanel`
  - `SectionFrame`
  - `FeatureCard`
  - `StepList`
  - `ActionCluster`
  - `Badge` or `Eyebrow`
  - the existing `Button`, expanded only as needed
- Desktop target-local components:
  - `DesktopHeroPanel`
  - `DesktopFeatureCard`
  - `DesktopStepList`
  - `DesktopActionCluster`
- Mobile target-local components:
  - `MobileHeroPanel`
  - `MobileHighlightCard`
  - `MobileStepCard`
  - `MobileActionRow`
- TV target-local components:
  - `TVFocusRail`
  - `TVFocusCard`
  - `TVDetailPanel`
  - `TVActionHint` or equivalent focus/footer treatment

## Explicit Non-Goals

- Do not make `packages/ui` a cross-platform runtime UI package.
- Do not convert desktop to React Native.
- Do not move route files or router generation into shared packages.
- Do not move TV focus, remote navigation, or interaction wiring into shared packages.
- Do not turn the welcome experience into a command cheat sheet.
- Do not begin feature `14.0` TV auth/device-link work in this slice.
- Do not overfit tests to exact prose when semantic structure is enough.

## Fresh-Context Restart

- [ ] Read `PLAN.md` from top to bottom before doing anything else.
- [ ] Read `PROGRESS.md`.
- [ ] Read `docs/LIVING_DOCS.md`.
- [ ] Read `docs/ARCHITECTURE.md`.
- [ ] Read `TODO-FEATURES.md`.
- [ ] Read `docs/session-summaries/SESSION_144_SUMMARY.md`.
- [ ] Read the current implementation files:
  - `src/new_repo_template/snapshot_assets/templates/shared/shared_index.ts`
  - `src/new_repo_template/snapshot_assets/templates/fullstack/web_index_route.tsx`
  - `src/new_repo_template/snapshot_assets/templates/desktop/desktop_app.ts`
  - `src/new_repo_template/snapshot_assets/templates/mobile/mobile_app.tsx`
  - `src/new_repo_template/snapshot_assets/templates/tv/tv_app.tsx`
  - `src/new_repo_template/snapshot_assets/templates/ui/ui_button.tsx`
- [ ] Read the most relevant current contracts:
  - `tests/contracts/test_fullstack_auth_wiring_contract.py`
  - `tests/contracts/test_desktop_scaffold_contract.py`
  - `tests/contracts/test_desktop_runtime_smoke_contract.py`
  - `tests/contracts/test_mobile_tv_scaffold_contract.py`
  - `tests/contracts/test_mobile_tv_runtime_smoke_contract.py`
  - `tests/contracts/test_tv_input_hid_contract.py`
  - `tests/contracts/test_shared_react_boundaries_contract.py`
  - `tests/contracts/test_shared_infra_packages_contract.py`
  - `tests/contracts/test_python_lane_contract.py`
  - `tests/contracts/test_python_lib_scaffold_contract.py`
  - `tests/contracts/test_cli_validation_and_python_commands_contract.py`
  - `tests/contracts/test_typescript_cli_scaffold_contract.py`
  - `tests/contracts/test_typescript_cli_runtime_smoke_contract.py`
  - `tests/contracts/test_typescript_lib_scaffold_contract.py`
  - `tests/contracts/test_typescript_lib_runtime_smoke_contract.py`
  - `tests/contracts/test_bun_workspace_install_contract.py`
  - `tests/contracts/test_turbo_command_smoke_contract.py`
- [ ] Run `date "+%Y-%m-%d %I:%M:%S %p"`.
- [ ] Run `btca status`.
- [ ] Run `btca ask -r shadcn-ui -q "Should shadcn stay web only while shared tokens and content support web desktop mobile and tv?" --sub-agent`.
- [ ] If there is any uncertainty about shared-vs-platform boundaries before editing, run `btca ask -r react-docs -r react-native-docs -r react-native-tvos -r expo-docs -q "For a product that ships web desktop mobile and tv apps what should stay shared and what should stay platform specific?" --sub-agent`.
- [ ] Confirm that the roadmap/docs still match the locked decisions in this plan before starting RED.

## YELLOW

- [ ] Confirm the exact gaps between the current feature `12.0` welcome baseline and the locked `Operator Console` structure.
- [ ] Confirm whether `packages/shared` needs a richer data model for hero, sections, actions, and TV detail content.
- [ ] Confirm whether `packages/design-tokens` needs new plain-data roles for panel hierarchy, emphasis, and focus-safe accents.
- [ ] Confirm the minimal owned web component additions required in `packages/ui`.
- [ ] Confirm the target-local desktop/mobile/TV component breakdown without violating the ownership rules.
- [ ] Confirm the validation list and expected test updates before editing.

## RED

- [ ] Update web/fullstack contract coverage to assert the `Operator Console` structure and any new shared content names without overfitting exact prose.
- [ ] Update desktop/mobile/TV scaffold contracts so they assert the new layout/component patterns semantically.
- [ ] Keep `tests/contracts/test_shared_react_boundaries_contract.py` enforcing renderer-safe shared packages and web-only `@generated/ui` ownership.
- [ ] Extend or adjust smoke/contract coverage only where the new component structure changes real template output.
- [ ] Make sure the broader package-matrix validation still covers Python lane, TypeScript CLI, Python lib, TypeScript lib, web, desktop, mobile, and TV confidence.

## GREEN

- [ ] Update `src/new_repo_template/snapshot_assets/templates/shared/shared_index.ts` with the locked `Operator Console` data model.
- [ ] Update the renderer-safe design token package only with plain-data token changes required by the redesign.
- [ ] Expand `src/new_repo_template/snapshot_assets/templates/ui/` with the owned web component set needed by the redesigned web welcome screen.
- [ ] Rework `src/new_repo_template/snapshot_assets/templates/fullstack/web_index_route.tsx` to use the owned web UI components and the new information architecture.
- [ ] Rework `src/new_repo_template/snapshot_assets/templates/desktop/desktop_app.ts` into the target-local desktop equivalent that matches the same system language without importing `@generated/ui`.
- [ ] Rework `src/new_repo_template/snapshot_assets/templates/mobile/mobile_app.tsx` into the target-local React Native equivalent that remains touch-first and native in structure.
- [ ] Rework `src/new_repo_template/snapshot_assets/templates/tv/tv_app.tsx` into the richer focus-first TV equivalent that keeps remote/focus logic target-local.
- [ ] Preserve all feature `11.0` boundary rules while implementing the redesign.

## BLUE

- [ ] Run `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."`.
- [ ] Run targeted frontend validation:
  - `uv run pytest tests/contracts/test_fullstack_auth_wiring_contract.py tests/contracts/test_desktop_scaffold_contract.py tests/contracts/test_desktop_runtime_smoke_contract.py tests/contracts/test_mobile_tv_scaffold_contract.py tests/contracts/test_mobile_tv_runtime_smoke_contract.py tests/contracts/test_tv_input_hid_contract.py tests/contracts/test_shared_react_boundaries_contract.py tests/contracts/test_shared_infra_packages_contract.py tests/contracts/test_bun_workspace_install_contract.py`
- [ ] Run broader package-matrix validation:
  - `uv run pytest tests/contracts/test_python_lane_contract.py tests/contracts/test_python_lib_scaffold_contract.py tests/contracts/test_cli_validation_and_python_commands_contract.py tests/contracts/test_typescript_cli_scaffold_contract.py tests/contracts/test_typescript_cli_runtime_smoke_contract.py tests/contracts/test_typescript_lib_scaffold_contract.py tests/contracts/test_typescript_lib_runtime_smoke_contract.py tests/contracts/test_turbo_command_smoke_contract.py`
- [ ] Run `uv run ruff check src/new_repo_template tests/contracts`.
- [ ] Run full-suite validation with `uv run pytest`.
- [ ] If any validation fails, fix the smallest real issue and rerun the affected command before proceeding.

## Documentation Sync

- [ ] Update `PROGRESS.md`.
- [ ] Update `docs/LIVING_DOCS.md`.
- [ ] Update `docs/ARCHITECTURE.md`.
- [ ] Update `TODO-FEATURES.md` if the feature state or locked decisions changed during implementation.
- [ ] Create a new session summary in `docs/session-summaries/` using the current `date` output.
- [ ] Keep the final docs language aligned so a blank-context restart can continue safely.

## Restart-Safe Notes

- `web` goes first because it is the clearest place to express the owned component strategy, but it is not the only deliverable.
- Desktop should feel visually aligned with `web`, but its implementation remains target-local and Electron-safe.
- Mobile should feel like the same product while still reading as a native touch-first screen.
- TV should stay focus-first and remote-first even if the visual language becomes more premium.
- The shared layer should define what the welcome experience means, not how every target literally renders it.
