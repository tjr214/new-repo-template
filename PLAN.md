# Feature 10.0 TanStack Start Replacement Plan

**Last Updated:** 2026-03-29 10:28:47 PM
**Status:** Planning locked / ready for implementation YELLOW
**Previous Session Summary:** `docs/session-summaries/SESSION_129_SUMMARY.md`
**Current Planning Summary:** `docs/session-summaries/SESSION_130_SUMMARY.md`

---

## Goal

Replace the current fake `web` lane with a real TanStack Start scaffold while preserving the rest of the feature `10.0` local-dev/auth work.

This plan exists so a fresh-context restart can resume directly into implementation without losing the decisions and research from the runtime validation and TanStack Start planning discussion.

---

## Why This Slice Exists

- Runtime validation proved the current generated web lane is still plain Vite + TanStack Router, not a real TanStack Start app.
- Feature `10.0` explicitly requires that the web package type correctly initialize TanStack Start and actually run.
- The current runtime/manual matrix should not continue until the web baseline is corrected, because any further auth/runtime findings would be built on top of the wrong frontend stack.

---

## YELLOW Pass Completed In This Session

- [x] Read `PLAN.md`.
- [x] Read `PROGRESS.md`.
- [x] Read `docs/LIVING_DOCS.md`.
- [x] Read `docs/ARCHITECTURE.md`.
- [x] Read `TODO-FEATURES.md`.
- [x] Read `docs/session-summaries/SESSION_129_SUMMARY.md`.
- [x] Read `src/new_repo_template/scaffold.py`.
- [x] Read `src/new_repo_template/snapshot_assets/templates/workspace_packages/web_package.json`.
- [x] Read `src/new_repo_template/snapshot_assets/templates/fullstack/web_main.tsx`.
- [x] Read `src/new_repo_template/snapshot_assets/templates/fullstack/web_router.tsx`.
- [x] Read `src/new_repo_template/snapshot_assets/templates/fullstack/web_root_route.tsx`.
- [x] Read `src/new_repo_template/snapshot_assets/templates/fullstack/web_index_route.tsx`.
- [x] Read `src/new_repo_template/snapshot_assets/templates/fullstack/web_app.config.ts`.
- [x] Read `tests/contracts/test_fullstack_auth_wiring_contract.py`.
- [x] Read `tests/contracts/test_target_matrix_and_auth_contract.py`.
- [x] Run `date "+%Y-%m-%d %I:%M:%S %p"`.
- [x] Run `btca status`.
- [x] Use `btca ask -r tanstack-router-start -q "What Vite config and plugins does TanStack Start require in a React app" --sub-agent`.
- [x] Use `btca ask -r tanstack-router-start -q "What files does a minimal TanStack Start app use for root document router and index route" --sub-agent`.
- [x] Use `btca ask -r tanstack-router-start -q "What is the minimal TanStack Start entrypoint and how is the router exported in a React app" --sub-agent`.
- [x] Use `btca ask -r tanstack-router-start -q "Should a custom monorepo scaffold shell out to the official TanStack Start creator at runtime or mirror the required Start files directly" --sub-agent`.

---

## Locked Decisions

- [x] The next implementation slice is the TanStack Start replacement for the `web` lane.
- [x] `nurt` should continue to own deterministic scaffold templates.
- [x] `nurt new` should not shell out to the official TanStack creator at end-user runtime.
- [x] The official TanStack Start creator/examples should be used as maintainer reference material only.
- [x] The replacement target is a real minimal TanStack Start app, not another “Start-like” approximation.
- [x] The local/prod auth matrix work from feature `10.0` slice 1 remains in place and must continue to work after the web replacement.
- [x] The corrected compose baseline/override split remains in place and should not be reverted.

---

## Explicit Non-Goals

- [x] Do not invoke `npx @tanstack/cli create` during normal `nurt new` execution.
- [x] Do not add a second dynamic upstream generator dependency to end-user scaffold runs.
- [x] Do not continue the remaining RC1 runtime matrix before the real TanStack Start replacement is in place.
- [x] Do not treat the current fake `app.config.ts` plus `main.tsx` pattern as sufficient for feature `10.0`.
- [x] Do not expand this slice into broad auth redesign, backend runtime redesign, or desktop/mobile/TV changes.
- [x] Do not over-copy large example/demo assets from upstream TanStack examples when a smaller Start baseline is enough.

---

## Current Gap Summary

- [x] The current web lane depends on `@tanstack/react-router`, `vite`, `react`, and `react-dom`, but not `@tanstack/react-start`.
- [x] The current web lane uses a client-only `src/main.tsx` entry rather than a Start client entrypoint.
- [x] The current `src/router.tsx` exports a singleton router instead of a `getRouter()` pattern.
- [x] The current `src/routes/__root.tsx` is not a Start document shell and does not render `HeadContent` / `Scripts`.
- [x] The current `src/routes/index.tsx` and surrounding structure are part of a plain TanStack Router setup, not a verified Start setup.
- [x] The current `app.config.ts` is effectively a fake placeholder and should not be treated as proof of TanStack Start support.

---

## Replacement Target

- [x] Add `@tanstack/react-start` to the web package dependencies.
- [x] Add the Start Vite plugin to the web Vite config.
- [x] Replace the current client-only entry with a Start client entrypoint.
- [x] Replace singleton router export with `getRouter()`.
- [x] Replace the root route with a real Start document shell.
- [x] Replace the current route/file assumptions with a real minimal file-based Start route baseline.
- [x] Update web scripts/package wiring to match the real Start stack.
- [x] Update the contract suite so it asserts real Start signals instead of the current placeholder signals.

---

## Expected Minimal File Set After Replacement

- [ ] `apps/web/web/package.json` should include `@tanstack/react-start`.
- [ ] `apps/web/web/vite.config.ts` should include `tanstackStart()` and `viteReact()`.
- [ ] `apps/web/web/src/client.tsx` should hydrate `StartClient`.
- [ ] `apps/web/web/src/router.tsx` should export `getRouter()`.
- [ ] `apps/web/web/src/routes/__root.tsx` should render a real document shell with `HeadContent`, `Outlet`, and `Scripts`.
- [ ] `apps/web/web/src/routes/index.tsx` should use `createFileRoute("/")`.
- [ ] `apps/web/web/src/routeTree.gen.ts` should remain part of the generated structure and be valid for the Start route setup.

---

## RED

- [ ] Update `tests/contracts/test_fullstack_auth_wiring_contract.py` so the web assertions require real Start signals:
- [ ] Assert `@tanstack/react-start` is present in the web package manifest.
- [ ] Assert `@tanstack/react-start/plugin/vite` is present in `vite.config.ts`.
- [ ] Assert `src/client.tsx` exists and references `StartClient`.
- [ ] Assert `src/router.tsx` exports `getRouter()`.
- [ ] Assert `src/routes/__root.tsx` uses `HeadContent` and `Scripts`.
- [ ] Assert `src/routes/index.tsx` uses `createFileRoute("/")`.
- [ ] Update any dry-run path expectations so they reference the real Start file set.
- [ ] Update any older tests that still treat `app.config.ts` or `main.tsx` as Start proof.

---

## GREEN

- [ ] Update `src/new_repo_template/snapshot_assets/templates/workspace_packages/web_package.json` to use real Start dependencies and scripts.
- [ ] Replace `src/new_repo_template/snapshot_assets/templates/fullstack/web_main.tsx` with a real Start client entry template or rename it to the correct Start file.
- [ ] Update `src/new_repo_template/snapshot_assets/templates/fullstack/web_router.tsx` to export `getRouter()`.
- [ ] Replace `src/new_repo_template/snapshot_assets/templates/fullstack/web_root_route.tsx` with a real Start document shell.
- [ ] Replace `src/new_repo_template/snapshot_assets/templates/fullstack/web_index_route.tsx` with a real Start file route baseline.
- [ ] Update `src/new_repo_template/snapshot_assets/templates/fullstack/web_vite.config.ts` to use `tanstackStart()` and `viteReact()`.
- [ ] Remove or replace the fake `web_app.config.ts` template if it is not part of the real Start baseline.
- [ ] Update `src/new_repo_template/scaffold.py` so the web path list and file writers match the new Start file set.
- [ ] Keep the current auth-boundary files (`app-auth.ts`, `auth-runtime.ts`, provider-specific placeholders) wired into the corrected Start-based web app layout.

---

## BLUE

- [ ] Re-check the minimal Start baseline against the BTCA-backed guidance before closeout.
- [ ] Keep the replacement as small as possible; avoid copying unnecessary demo/example files.
- [ ] Re-run targeted contracts.
- [ ] Re-run `uv run ruff check src/new_repo_template tests/contracts`.
- [ ] Refresh snapshot metadata with `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."`.
- [ ] Re-run `uv run pytest`.

---

## Runtime Revalidation After Implementation

- [ ] Regenerate `local=better-auth`, `prod=clerk` from the updated scaffold.
- [ ] Run `bun install --frozen-lockfile` in the generated repo.
- [ ] Run the built-in smoke commands again.
- [ ] Run `docker compose up` for the regenerated repo.
- [ ] Verify `http://127.0.0.1:3000` renders real app content under the Start-based scaffold.
- [ ] Only after that revalidation passes, continue the remaining auth combinations.

---

## Fresh-Context Restart Checklist

- [ ] Read `PLAN.md`.
- [ ] Read `PROGRESS.md`.
- [ ] Read `docs/LIVING_DOCS.md`.
- [ ] Read `docs/ARCHITECTURE.md`.
- [ ] Read `TODO-FEATURES.md`.
- [ ] Read `docs/session-summaries/SESSION_130_SUMMARY.md`.
- [ ] Re-read `src/new_repo_template/scaffold.py`.
- [ ] Re-read `src/new_repo_template/snapshot_assets/templates/workspace_packages/web_package.json`.
- [ ] Re-read `src/new_repo_template/snapshot_assets/templates/fullstack/web_main.tsx` or its replacement file.
- [ ] Re-read `src/new_repo_template/snapshot_assets/templates/fullstack/web_router.tsx`.
- [ ] Re-read `src/new_repo_template/snapshot_assets/templates/fullstack/web_root_route.tsx`.
- [ ] Re-read `src/new_repo_template/snapshot_assets/templates/fullstack/web_index_route.tsx`.
- [ ] Re-read `src/new_repo_template/snapshot_assets/templates/fullstack/web_vite.config.ts`.
- [ ] Re-read `tests/contracts/test_fullstack_auth_wiring_contract.py`.
- [ ] Re-read `tests/contracts/test_target_matrix_and_auth_contract.py`.
- [ ] Run `date "+%Y-%m-%d %I:%M:%S %p"`.
- [ ] Run `btca status`.
- [ ] Re-run the TanStack Start BTCA guidance queries before changing the templates.
- [ ] Start RED only after the above is complete.

---

## Notes For The Next Session

- [ ] Mention explicitly that the YELLOW pass included file reads, `btca status`, and `btca ask` usage.
- [ ] Keep the TanStack Start replacement small and deterministic.
- [ ] Use the official creator/examples as maintainer references, not runtime scaffold dependencies.
- [ ] Do not overwrite `docs/session-summaries/SESSION_130_SUMMARY.md`; create a newer session summary when implementation begins.
