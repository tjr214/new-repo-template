# Feature 14.0 Runtime Closeout Plan

**Last Updated:** 2026-04-11 04:14:00 PM
**Status:** Ready For Runtime-Orchestration YELLOW Pass
**Previous Cycle Summary:** `docs/session-summaries/SESSION_150_SUMMARY.md`

---

## Goal

- [ ] Close the remaining feature `14.0` runtime gap by proving the real local approval-and-redemption loop works end to end for a generated `web + backend + tv` repo and by validating the Android TV success/failure path at the minimum emulator target.

## Current State Snapshot

- [x] The template implementation is green at `253` passing tests.
- [x] The generated live-loop scaffold now includes backend-owned device-code/session logic, signed-in web approval runtime, and restart-safe TV session persistence.
- [x] Fresh generated-repo validation already reaches `bun install --frozen-lockfile`, web `build:app`, and TV `tv:export` successfully on a `better-auth` local runtime repo.
- [ ] The remaining gap is runtime orchestration and validation, not baseline scaffold generation.

## YELLOW

- [ ] Read `PLAN.md`, `PROGRESS.md`, `docs/LIVING_DOCS.md`, `docs/ARCHITECTURE.md`, `TODO-FEATURES.md`, and `docs/session-summaries/SESSION_150_SUMMARY.md` before editing.
- [ ] Read the runtime-critical implementation files before editing:
  - `src/new_repo_template/scaffold.py`
  - `src/new_repo_template/add_mode.py`
  - `src/new_repo_template/snapshot_assets/templates/fullstack/backend_http_device_link.ts`
  - `src/new_repo_template/snapshot_assets/templates/fullstack/backend_schema_device_link.ts`
  - `src/new_repo_template/snapshot_assets/templates/fullstack/backend_auth.ts`
  - `src/new_repo_template/snapshot_assets/templates/fullstack/backend_convex.config.ts`
  - `src/new_repo_template/snapshot_assets/templates/fullstack/backend_readme_device_link.md`
  - `src/new_repo_template/snapshot_assets/templates/fullstack/web_device_route_better_auth.tsx`
  - `src/new_repo_template/snapshot_assets/templates/fullstack/web_device_route_clerk.tsx`
  - `src/new_repo_template/snapshot_assets/templates/fullstack/web_device_route_mixed.tsx`
  - `src/new_repo_template/snapshot_assets/templates/tv/tv_app_device_link.tsx`
  - `src/new_repo_template/snapshot_assets/templates/tv/tv_readme_device_link.md`
- [ ] Read the runtime-validation contracts before editing:
  - `tests/contracts/test_tv_device_link_flow_contract.py`
  - `tests/contracts/test_fullstack_auth_wiring_contract.py`
  - `tests/contracts/test_mobile_tv_runtime_smoke_contract.py`
- [ ] Run `date "+%Y-%m-%d %I:%M:%S %p"`.
- [ ] Run `btca status`.
- [ ] Run `btca ask -r convex-docs -q "For a self hosted local Convex setup, what is the normal way to push local convex functions and schema so the running backend serves the app code?" --sub-agent`.
- [ ] Run `btca ask -r convex-better-auth -r better-auth-core -q "For a local Convex Better Auth app, what is the normal runtime sequence to boot auth routes and then sign in from the web app against a self hosted backend?" --sub-agent`.
- [ ] Run `btca ask -r expo-docs -r react-native-docs -q "For an Expo Android TV app, what is the normal minimal validation path for a real emulator success case plus one failure path after app export works?" --sub-agent`.
- [ ] Confirm the exact runtime gap after the YELLOW pass:
  - whether the generated repo is missing a deterministic local backend deploy/sync command
  - whether compose should own that step or whether the repo should expose a documented operator command sequence

## RED

- [ ] Add or update contracts for the runtime/orchestration fix before implementation.
- [ ] If a new repo-root/backend command is needed for local backend deployment, add contract coverage for its scaffold presence and expected command shape.
- [ ] If compose wiring changes, add or update contract coverage for the generated files/docs/env expectations.

## GREEN

- [ ] Implement the smallest runtime-orchestration fix needed for a deterministic local approval flow.
- [ ] Regenerate a fresh `web + backend + tv` repo after the fix.
- [ ] Provide the minimum required local env values for the chosen validation path.
- [ ] Start the generated local owned services and deploy/load the backend code into the self-hosted Convex runtime.
- [ ] Exercise the real web approval path end to end.
- [ ] Exercise the real TV redemption path end to end.
- [ ] Confirm TV restart restores the persisted app session.
- [ ] Exercise at least one real failure path such as expiry or denial.

## BLUE

- [ ] Refactor the runtime/orchestration change down to the smallest clear structure.
- [ ] Re-run `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."`.
- [ ] Re-run `uv run ruff check src/new_repo_template tests/contracts`.
- [ ] Re-run targeted contracts.
- [ ] Re-run `uv run pytest`.
- [ ] Re-run the generated-repo validation path after the final change.

## Runtime Validation Target

- [ ] Better Auth local runtime path is the minimum required proof target.
- [ ] Required generated repo checks:
  - `bun install --frozen-lockfile`
  - local backend/app boot with deployed Convex code
  - web `/device` signed-in approval success
  - TV receipt of real persisted app session/token
  - TV restart restores session
  - one failure-path validation
- [ ] Android TV emulator is the minimum required TV runtime target.
- [ ] Physical NVIDIA Shield remains follow-up only unless roadmap scope changes.

## Documentation Sync

- [ ] Update `PROGRESS.md`.
- [ ] Update `docs/LIVING_DOCS.md`.
- [ ] Update `docs/ARCHITECTURE.md`.
- [ ] Update `TODO-FEATURES.md` only for items truly completed by the runtime pass.
- [ ] Create a new session summary in `docs/session-summaries/`.
