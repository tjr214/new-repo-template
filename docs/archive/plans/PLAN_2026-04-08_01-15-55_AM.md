# Feature 14.0 Follow-Up Plan

**Last Updated:** 2026-04-08 12:53:21 AM
**Status:** Starter Implementation Complete / End-To-End Closeout Pending
**Previous Cycle Summary:** `docs/session-summaries/SESSION_147_SUMMARY.md`
**Latest Implementation Summary:** `docs/session-summaries/SESSION_148_SUMMARY.md`

---

## Goal

- [ ] Close the remaining feature `14.0` gap by replacing the current starter review/polling behavior with a stronger real cross-device approval-and-redemption loop and by validating that the Android TV app can complete the full account-linking flow successfully before RC1.

## Fresh-Context Restart

- [ ] Read `PLAN.md` completely before making edits.
- [ ] Read `PROGRESS.md` completely before making edits.
- [ ] Read `docs/LIVING_DOCS.md` completely before making edits.
- [ ] Read `docs/ARCHITECTURE.md` completely before making edits.
- [ ] Read `TODO-FEATURES.md` completely before making edits.
- [ ] Read `docs/session-summaries/SESSION_148_SUMMARY.md` completely before making edits.
- [ ] Read `src/new_repo_template/scaffold.py`, especially the new `fullstack_tv_device_link_enabled(...)` and `scaffold_fullstack_tv_device_link_assets(...)` helpers.
- [ ] Read `src/new_repo_template/add_mode.py`, especially `_stage_scaffold_content(...)` and `inventory_existing_repo(...)`.
- [ ] Read `src/new_repo_template/btca_config_manager.py` for the new composition-aware QR BTCA resource logic.
- [ ] Read the new feature `14.0` template files under `src/new_repo_template/snapshot_assets/templates/fullstack/` and `src/new_repo_template/snapshot_assets/templates/tv/`.
- [ ] Read `tests/contracts/test_tv_device_link_flow_contract.py` and `tests/contracts/test_btca_config_contract.py`.
- [ ] Run `date "+%Y-%m-%d %I:%M:%S %p"`.
- [ ] Run `btca status`.
- [ ] Run any new `btca ask` lookups needed for the remaining real backend approval/redeem implementation before editing that deeper runtime path.

## Completed In This Cycle

- [x] Completed the restart-safe YELLOW pass, including file rereads, `btca status`, and `btca ask` lookups.
- [x] Added the approved project BTCA resources `react-native-qrcode-svg` and `react-native-svg` and synced `docs/BTCA_RESOURCES.md`.
- [x] Added RED contracts for feature `14.0` scaffold output, add-mode retrofit behavior, and composition-aware BTCA generation.
- [x] Implemented the starter `web + backend + tv` device-link baseline in the scaffold templates.
- [x] Implemented the matching add-mode retrofit path so existing repos can receive the same baseline.
- [x] Revalidated the repo with targeted contract passes, `ruff`, `template-assets validate`, and the full suite at `252` passing tests.
- [x] Performed generated-repo validation covering install, web build, TV export, live `/device` fetches, and root Docker Compose startup.

## Locked Decisions

- [ ] Preserve the scope boundary: feature `14.0` applies to repos that include `web + backend + tv`.
- [ ] Preserve the app-boundary rule: keep the generated flow provider-neutral even when the repo uses Clerk and/or Better Auth behind the scenes.
- [ ] Preserve the backend trust boundary: the backend owns short-lived device-link records, approval state, polling semantics, and final redemption into a TV app session/token.
- [ ] Preserve the web role: web owns verification UI plus sign-in through the configured provider path.
- [ ] Preserve the TV role: TV acts as a thin polling client and does not receive raw Clerk or Better Auth provider credentials.
- [ ] Preserve the QR rule: TV QR encodes `verification_uri_complete`.
- [ ] Preserve the fallback rule: the TV screen must also show visible `verification_uri` and `user_code` fallback text.
- [ ] Preserve the UX rule: the unauthenticated TV state remains a simple pairing screen with zero or one focusable control.
- [ ] Preserve the add-mode rule: repos that newly reach `web + backend + tv` through `nurt add` must receive the same baseline.

## Remaining Gap

- [ ] Replace the current starter review state in the web verification route with a stronger real approval path.
- [ ] Replace the current starter backend route inventory/contract layer with real backend approval-and-redemption behavior if the roadmap still requires a truly completed device-link loop before closing feature `14.0`.
- [ ] Replace the current TV starter polling behavior with a live backend-linked completion path and real app-session persistence.
- [ ] Re-run a stronger real cross-device validation that proves the Android TV app can actually complete the full account-linking flow, not only serve/build/export the starter surfaces.

## Next Execution Steps

- [ ] Decide whether the roadmap still requires a truly live backend-linked approval loop before feature `14.0` can be closed, or whether the current starter baseline is sufficient for this phase.
- [ ] If a live loop is still required, design the smallest real backend implementation that preserves the provider-neutral boundary while giving the TV app a real approval-and-redemption path.
- [ ] Add RED coverage for that deeper runtime behavior before editing the starter route/backend/TV code again.
- [ ] Re-run the generated-repo validation with a real approval success path once it exists.

## Documentation Sync

- [ ] Update `PROGRESS.md` again when the remaining end-to-end closeout work completes.
- [ ] Update `docs/LIVING_DOCS.md` again when the remaining end-to-end closeout work completes.
- [ ] Update `docs/ARCHITECTURE.md` again when the remaining end-to-end closeout work completes.
- [ ] Update `TODO-FEATURES.md` to close the final feature `14.0` validation item when it is actually done.
- [ ] Create a new session summary in `docs/session-summaries/` when that remaining closeout work completes.
- [ ] Keep `docs/BTCA_RESOURCES.md` synchronized immediately if any further project BTCA resources are added or removed.
