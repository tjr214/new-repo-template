# Feature 14.0 Live Loop Plan

**Last Updated:** 2026-04-08 02:24:09 PM
**Status:** Live implementation and generated build/export validation are green; end-to-end local approval/runtime validation remains open
**Previous Cycle Summary:** `docs/session-summaries/SESSION_148_SUMMARY.md`
**Latest Planning Summary:** `docs/session-summaries/SESSION_149_SUMMARY.md`

---

## Goal

- [ ] Close the remaining feature `14.0` gap by replacing the current starter review/polling baseline with a real template-owned Convex-backed approval-and-redemption loop for the `web + backend + tv` composition, while keeping the generated repo compose-ready and expecting end users to provide only the required auth/env values.

## Current State Snapshot

- The template now scaffolds the real composition-owned device-link runtime for `web + backend + tv`, including the Convex-backed device/session handlers, composition-specific auth bridge files, and restart-safe TV persistence.
- Repo-level validation is green at `253` passing tests, plus `ruff` and `template-assets validate`.
- Fresh generated repo validation now reaches `bun install --frozen-lockfile`, real web `build:app`, and TV `tv:export` successfully on a `better-auth` local runtime scaffold.
- The remaining gap is now narrower: true end-to-end local approval/runtime validation plus Android TV success/failure-path validation are still open.

## Fresh-Context Restart

- [x] Read `PLAN.md` completely before making edits.
- [x] Read `PROGRESS.md` completely before making edits.
- [x] Read `docs/LIVING_DOCS.md` completely before making edits.
- [x] Read `docs/ARCHITECTURE.md` completely before making edits.
- [x] Read `TODO-FEATURES.md` completely before making edits.
- [x] Read `docs/session-summaries/SESSION_149_SUMMARY.md` completely before making edits.
- [x] Read `docs/BTCA_RESOURCES.md` completely before making edits.
- [x] Read `src/new_repo_template/scaffold.py`, especially `fullstack_tv_device_link_enabled(...)`, `scaffold_fullstack_tv_device_link_assets(...)`, the device-link env render helpers, and the composition-aware path reporting.
- [x] Read `src/new_repo_template/add_mode.py`, especially `inventory_existing_repo(...)` and `_stage_scaffold_content(...)`.
- [x] Read `src/new_repo_template/btca_config_manager.py`, especially the composition-aware QR resource logic.
- [x] Read `src/new_repo_template/snapshot_assets/templates/fullstack/backend_device_link.ts`.
- [x] Read `src/new_repo_template/snapshot_assets/templates/fullstack/backend_http_device_link.ts`.
- [x] Read `src/new_repo_template/snapshot_assets/templates/fullstack/backend_schema_device_link.ts`.
- [x] Read `src/new_repo_template/snapshot_assets/templates/fullstack/backend_readme_device_link.md`.
- [x] Read the device-link web route templates and route-tree output.
- [x] Read `src/new_repo_template/snapshot_assets/templates/tv/tv_app_device_link.tsx`.
- [x] Read `src/new_repo_template/snapshot_assets/templates/tv/tv_readme_device_link.md`.
- [x] Read `src/new_repo_template/snapshot_assets/templates/workspace_packages/tv_package_device_link.json`.
- [x] Read `tests/contracts/test_tv_device_link_flow_contract.py`.
- [x] Read `tests/contracts/test_btca_config_contract.py`.
- [x] Read `tests/contracts/test_fullstack_auth_wiring_contract.py`.
- [x] Read `tests/contracts/test_nurt_add_contract.py`.
- [x] Run `date "+%Y-%m-%d %I:%M:%S %p"`.
- [x] Run `btca status`.
- [x] Run `btca ask -r convex-docs -r better-auth-core -q "For a Convex backed web plus TV device linking flow, should the backend own device link records and final TV session issuance while end users still only provide auth env and secrets?" --sub-agent`.
- [x] Run `btca ask -r expo-docs -r react-native-docs -q "For an Expo React Native TV app, what is the normal local persistence approach for an app session that should survive restarts but not hold upstream provider credentials?" --sub-agent`.
- [x] Run additional `btca ask` lookups needed for the exact Convex/auth/session implementation before editing code.

## Locked Decisions

- [ ] Preserve the scope boundary: feature `14.0` applies to repos that include `web + backend + tv`.
- [ ] Preserve the product boundary: the real live device-link flow is template-owned functionality, not optional end-user custom code.
- [ ] Preserve the generated-repo readiness target: the generated repo should be considered ready once the end user supplies the required auth/env values.
- [ ] Preserve the compose-ready target: the generated repo should boot the parts it owns (`web` plus local backend/Convex) via compose.
- [ ] Preserve the app-boundary rule: keep the generated flow provider-neutral even when the repo uses Clerk and/or Better Auth behind the scenes.
- [ ] Preserve the backend trust boundary: the trusted backend owns device-link records, approval state, redemption semantics, and final TV app-session issuance.
- [ ] Preserve the web role: web owns sign-in and the signed-in approval path.
- [ ] Preserve the TV role: TV acts as a thin polling client, shows QR plus fallback URL/code, and never receives raw upstream provider credentials.
- [ ] Preserve the TV persistence rule: TV app-session persistence is template-owned behavior and should survive app restarts.
- [ ] Preserve the add-mode rule: `nurt add` must retrofit this same composition-owned capability when a repo reaches `web + backend + tv` later.
- [ ] Preserve the auth gating rule: repos with backend auth set to `none` must not pretend the live device-link flow exists.

## Explicit Non-Goals

- [ ] Do not leave the real live flow for end users to hand-build in their own projects.
- [ ] Do not move provider sign-in UX or provider SDK login flows into the TV runtime.
- [ ] Do not store upstream provider credentials directly on the TV.
- [ ] Do not regress the QR-first pairing screen back to the older operator-console unauthenticated layout.
- [ ] Do not make composition-owned behavior differ depending on whether the repo started with `tv` or reached it later through `nurt add`.
- [ ] Do not treat a starter-only scaffold as sufficient for closing feature `14.0` if the roadmap still requires a real cross-device approval loop.

## Open Design Items To Resolve Early

- [x] Decide the exact TV persistence split between non-sensitive session metadata and any sensitive app-issued token material.
- [x] Decide whether the final TV app session will be an opaque app session identifier, a bearer token, or another backend-issued artifact, while keeping upstream provider credentials off-device.
- [x] Decide whether the real live implementation should use only Convex functions/actions or a small adjacent server endpoint for final session issuance if Better Auth session minting requires it.

## RED

- [x] Add or update contract coverage for the real live device-link loop before replacing the starter implementation.
- [x] Extend `tests/contracts/test_tv_device_link_flow_contract.py` to require the stronger live-loop semantics once the implementation shape is finalized.
- [x] Add or update coverage for TV persistence expectations, including startup recovery and invalid-session handling if that behavior becomes scaffold-visible.
- [x] Add or update contract coverage for auth-disabled backend compositions so they do not emit a fake live device-link flow.
- [x] Add or update add-mode contracts if the real live implementation changes which web/backend/tv files must be retrofitted into existing repos.

## GREEN

- [x] Replace the current backend starter contract layer with the real Convex-backed device-link state machine owned by the generated template.
- [x] Implement the real signed-in web approval path behind the generated provider-neutral auth boundary for the `web + backend + tv` composition.
- [x] Implement the real TV polling/redeem path against backend-owned device-link records.
- [x] Implement template-owned TV app-session persistence for restart-safe behavior.
- [x] Keep the TV persistence split explicit: use normal persistent app-state storage for non-sensitive session metadata, and add separate handling only if a sensitive app-issued token must persist.
- [x] Keep the generated flow provider-neutral at the app boundary so users only plug in their chosen auth env/config/secrets.
- [x] Keep the generated repo compose-ready for the parts it owns at scaffold/build level.
- [x] Keep `nurt add` aligned with the live implementation so older repos that newly reach `web + backend + tv` get the same capability.

## BLUE

- [x] Refactor the live implementation down to the smallest clear structure once the deeper contracts are green.
- [x] Re-check that shared packages remain renderer-safe and that TV runtime behavior stays TV-local.
- [x] Re-check that provider-specific details remain inside the web/backend auth boundary rather than leaking into shared packages or the TV runtime.
- [x] Re-run `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."` after template changes.
- [x] Re-run `uv run ruff check src/new_repo_template tests/contracts`.
- [x] Re-run the targeted feature `14.0` contract suites.
- [x] Re-run `uv run pytest`.

## Runtime Validation

- [x] Generate a fresh `web + backend + tv` repo after the live-loop contracts pass.
- [x] Run `bun install --frozen-lockfile` in the generated repo.
- [ ] Start the generated root compose stack and confirm the local owned services boot cleanly.
- [ ] Confirm the web verification route performs a real signed-in approval path.
- [ ] Confirm the TV pairing screen displays a live QR/code and polls the real backend flow.
- [ ] Confirm the TV receives a real persisted app session/token after approval.
- [ ] Restart the TV app and confirm the persisted app-session behavior works as designed.
- [ ] Exercise at least one failure path such as expiry or denial on Android TV.
- [ ] Use Android TV emulator as the minimum required real validation target.
- [ ] Record physical NVIDIA Shield status only as follow-up unless roadmap scope changes.

## Documentation Sync

- [x] Update `PROGRESS.md` after this implementation slice.
- [x] Update `docs/LIVING_DOCS.md` after this implementation slice.
- [x] Update `docs/ARCHITECTURE.md` after this implementation slice.
- [x] Update `TODO-FEATURES.md` to reflect the completed implementation work and the still-open runtime validation items.
- [x] Create a new session summary in `docs/session-summaries/` for this implementation slice.
- [ ] Keep `docs/BTCA_RESOURCES.md` synchronized immediately if any further project BTCA resources are added or removed.
