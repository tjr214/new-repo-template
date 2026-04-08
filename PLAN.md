# Feature 14.0 Execution Plan

**Last Updated:** 2026-04-07 11:53:54 PM
**Status:** Planning Locked / Ready For RED
**Previous Cycle Summary:** `docs/session-summaries/SESSION_146_SUMMARY.md`
**Latest Planning Summary:** `docs/session-summaries/SESSION_147_SUMMARY.md`

---

## Goal

- [ ] Implement feature `14.0` end to end for repos that include `web + backend + tv`: backend-issued short-lived device-link records, web verification/approval flow, TV QR-first pairing screen, TV app-session redemption, and validation that the Android TV app can complete the linking flow successfully.

## Fresh-Context Restart

- [ ] Read `PLAN.md` completely before making edits.
- [ ] Read `PROGRESS.md` completely before making edits.
- [ ] Read `docs/LIVING_DOCS.md` completely before making edits.
- [ ] Read `docs/ARCHITECTURE.md` completely before making edits.
- [ ] Read `TODO-FEATURES.md` completely before making edits.
- [ ] Read `docs/session-summaries/SESSION_147_SUMMARY.md` completely before making edits.
- [ ] Read `src/new_repo_template/scaffold.py` with attention to current auth-matrix handling, target composition, template mappings, and any existing TV/fullstack wiring.
- [ ] Read `src/new_repo_template/snapshot_assets/templates/tv/tv_app.tsx` and `src/new_repo_template/snapshot_assets/templates/tv/tv_readme.md` to understand the current unauthenticated TV baseline and validation story.
- [ ] Read `src/new_repo_template/snapshot_assets/templates/workspace_packages/tv_package.json` to understand current TV dependency and script wiring.
- [ ] Read the existing auth template files under `src/new_repo_template/snapshot_assets/templates/wiring/`: `backend_auth_config.ts`, `web_app_auth.ts`, `web_auth_runtime.ts`, `web_auth_provider_clerk.ts`, and `web_auth_client_better_auth.ts`.
- [ ] Read the current fullstack template files under `src/new_repo_template/snapshot_assets/templates/fullstack/`, especially `backend_readme.md`, `backend_http.ts`, `backend_schema.ts`, `web_root_route.tsx`, and `web_index_route.tsx`.
- [ ] Read the current contract files most likely to change: `tests/contracts/test_fullstack_auth_wiring_contract.py`, `tests/contracts/test_mobile_tv_scaffold_contract.py`, `tests/contracts/test_mobile_tv_runtime_smoke_contract.py`, `tests/contracts/test_target_matrix_and_auth_contract.py`, `tests/contracts/test_shared_react_boundaries_contract.py`, `tests/contracts/test_tv_input_hid_contract.py`, and `tests/contracts/test_tv_android_build_profile_contract.py`.
- [ ] Run `date "+%Y-%m-%d %I:%M:%S %p"`.
- [ ] Run `btca status`.
- [ ] Run `btca ask -r better-auth-core -q "For a device authorization flow, should the device UI prefer verification_uri_complete while also showing verification_uri and user_code, and what polling states should it handle?" --sub-agent`.
- [ ] Run `btca ask -r expo-docs -r react-native-docs -q "For an Expo React Native Android TV app, what is the cleanest way to display a QR code for a verification URL while keeping the screen simple for remote users?" --sub-agent`.
- [ ] If the chosen QR library is still missing from project BTCA resources, ask the user for explicit confirmation before adding that BTCA resource, then add it and sync `docs/BTCA_RESOURCES.md` before relying on it as maintained dependency context.

## Locked Decisions

- [ ] Preserve the scope boundary: feature `14.0` applies to repos that include `web + backend + tv`.
- [ ] Preserve the app-boundary rule: keep the generated flow provider-neutral even when the repo uses Clerk and/or Better Auth behind the scenes.
- [ ] Preserve the backend trust boundary: the backend owns short-lived device-link records, approval state, polling semantics, and final redemption into a TV app session/token.
- [ ] Preserve the web role: web owns verification UI plus sign-in through the configured provider path.
- [ ] Preserve the TV role: TV acts as a thin polling client and does not receive raw Clerk or Better Auth provider credentials.
- [ ] Preserve the QR rule: TV QR encodes `verification_uri_complete`.
- [ ] Preserve the fallback rule: the TV screen must also show visible `verification_uri` and `user_code` fallback text.
- [ ] Preserve the UX rule: replace the current unauthenticated multi-card `Operator Console` state with a simple mostly-passive pairing screen that has zero or one focusable control.
- [ ] Preserve the polling/error-state contract: handle `authorization_pending`, `slow_down`, `access_denied`, `expired_token`, `invalid_grant`, and `invalid_request`.
- [ ] Preserve the likely QR implementation direction unless YELLOW proves otherwise: use `react-native-qrcode-svg` plus `react-native-svg` for local QR generation in the TV app.

## Explicit Non-Goals

- [ ] Do not put provider-specific sign-in UX or provider SDK login flows directly into the TV runtime.
- [ ] Do not store raw provider access tokens or refresh tokens on the TV.
- [ ] Do not widen this slice to desktop or mobile beyond any incidental shared-contract changes.
- [ ] Do not preserve the current TV focus-rail/detail-panel operator-console layout for the unauthenticated pairing state.
- [ ] Do not skip BTCA governance for any newly introduced QR or persistence dependency.

## Open Execution Detail To Resolve Early

- [ ] Confirm the TV app-session persistence strategy during the next YELLOW pass before coding beyond the initial contracts. If persistence requires a new dependency (for example AsyncStorage or another Expo/RN-safe store), treat that dependency exactly like the QR dependency from a BTCA-governance perspective before adding it.
- [ ] Confirm whether feature `14.0` also needs explicit `nurt add` retrofit support when an existing repo newly reaches the `web + backend + tv` composition; if yes, include add-mode contract and implementation work in the same slice.

## RED

- [ ] Add or update contract coverage for the new `web + backend + tv` device-link baseline before implementation.
- [ ] Create a dedicated contract for the TV device-link screen semantics (new test file is acceptable, for example `tests/contracts/test_tv_device_link_flow_contract.py`).
- [ ] Update `tests/contracts/test_mobile_tv_scaffold_contract.py` to stop expecting the unauthenticated TV baseline to be the current focus-rail/operator-console layout once feature `14.0` lands.
- [ ] Update `tests/contracts/test_fullstack_auth_wiring_contract.py` to lock the presence of the new backend/web device-link files and generated route wiring.
- [ ] Update `tests/contracts/test_target_matrix_and_auth_contract.py` if the scaffold selection rules or composition requirements need new validation for `web + backend + tv` device-link support.
- [ ] Add or update runtime-smoke/structural coverage so the scaffolded TV app contains QR, URL, code, and polling-state semantics even before full manual device testing.
- [ ] If add-mode is confirmed in scope, update the relevant add-mode contracts so existing repos can receive the same device-link baseline when they newly compose into `web + backend + tv`.

## GREEN

- [ ] Extend `src/new_repo_template/scaffold.py` so feature `14.0` template output is composed correctly for `web + backend + tv` selections.
- [ ] Add the chosen QR dependency wiring to `src/new_repo_template/snapshot_assets/templates/workspace_packages/tv_package.json`.
- [ ] Replace the unauthenticated TV baseline in `src/new_repo_template/snapshot_assets/templates/tv/tv_app.tsx` with a simple pairing flow surface that shows QR, fallback URL, fallback code, status, expiry, and minimal focus behavior.
- [ ] Update `src/new_repo_template/snapshot_assets/templates/tv/tv_readme.md` so the generated TV docs describe the pairing flow and the intended Android TV validation path.
- [ ] Add the backend device-link baseline templates under `src/new_repo_template/snapshot_assets/templates/fullstack/` for link creation, approval, polling, and redemption as needed by the scaffold architecture.
- [ ] Add the web verification/approval route baseline under `src/new_repo_template/snapshot_assets/templates/fullstack/` so the generated web app supports both QR-driven and manual-code entry flows.
- [ ] Keep the generated app-boundary auth provider-neutral: Clerk and Better Auth details should stay inside existing auth boundary files and backend validation paths rather than leaking into the TV app surface.
- [ ] Implement the TV success-path handoff so the device stores an app-level session/token rather than upstream provider credentials.
- [ ] If add-mode is confirmed in scope, update add-mode implementation so existing repos can gain the feature `14.0` baseline when they reach the required composition.

## BLUE

- [ ] Refactor the feature `14.0` implementation down to the smallest clear structure once the contracts are green.
- [ ] Keep TV-specific focus/input behavior local to the TV app; do not push rendered UI behavior into shared packages.
- [ ] Re-check that shared packages remain renderer-safe and that `packages/ui` stays web-owned.
- [ ] Re-run `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."` after template changes.
- [ ] Re-run `uv run ruff check src/new_repo_template tests/contracts`.
- [ ] Re-run targeted contract suites for auth/fullstack/TV.
- [ ] Re-run `uv run pytest`.

## Runtime Validation

- [ ] Generate a fresh `web + backend + tv` repo after the contracts pass.
- [ ] Run `bun install --frozen-lockfile` in the generated repo.
- [ ] Run any required Python workspace sync if the generated validation repo includes Python lanes.
- [ ] Start the local web/backend stack with the generated Docker/Convex workflow and confirm the verification page is reachable.
- [ ] Confirm the web verification route supports both QR-driven prefilling and manual URL + code entry.
- [ ] Confirm the TV app shows the QR, fallback URL, fallback code, and polling status correctly on Android TV.
- [ ] Confirm the TV can complete approval and receive an app-level session/token successfully.
- [ ] Exercise at least one non-success polling path (`expired_token` and/or `access_denied`) and confirm the TV UX responds correctly.
- [ ] Record the Android TV emulator result and, if feasible in this slice, the physical NVIDIA Shield follow-up status in the generated validation notes.

## Documentation Sync

- [ ] Update `PROGRESS.md` after RED/GREEN/BLUE work completes.
- [ ] Update `docs/LIVING_DOCS.md` after RED/GREEN/BLUE work completes.
- [ ] Update `docs/ARCHITECTURE.md` after RED/GREEN/BLUE work completes.
- [ ] Update `TODO-FEATURES.md` to close feature `14.0` items as they actually complete.
- [ ] Create a new session summary in `docs/session-summaries/` when implementation work closes.
- [ ] Keep `docs/BTCA_RESOURCES.md` synchronized immediately if any project BTCA resources are added or removed during implementation.
