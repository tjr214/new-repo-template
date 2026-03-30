# Session 130 Summary

## Date and Time

2026-03-29 10:28:47 PM

## Scope

Locked the planning direction for replacing the current fake web lane with a real TanStack Start scaffold, recorded the maintainer-vs-runtime creator decision, and synced the docs and plan for a fresh-context restart.

## YELLOW Pass

- Re-read `PLAN.md`, `PROGRESS.md`, `docs/LIVING_DOCS.md`, `docs/ARCHITECTURE.md`, `TODO-FEATURES.md`, and `docs/session-summaries/SESSION_129_SUMMARY.md` before editing any docs.
- Re-read the current web scaffold package/template files and the relevant fullstack/auth contract suites.
- Ran `btca status`.
- Used `btca ask` for the real TanStack Start file structure, required Vite plugins, router export shape, client entrypoint expectations, and the maintainer strategy question about mirroring files versus shelling out to the official creator.

## Locked Decisions

- The next implementation slice is the real TanStack Start replacement for the `web` lane.
- `nurt` should own deterministic scaffold templates rather than shelling out to the official TanStack creator at user runtime.
- The official TanStack Start creator and example apps should be treated as maintainer references for updating the template, not as runtime dependencies of `nurt new`.
- The replacement target is a real minimal Start app with `@tanstack/react-start`, the Start Vite plugin, a `getRouter()` export, a Start client entrypoint, and a root document route using `HeadContent`, `Outlet`, and `Scripts`.

## Documentation Sync

- Updated `PROGRESS.md` with the new planning focus and next steps.
- Updated `docs/LIVING_DOCS.md` with the maintainer/reference strategy and the concrete Start replacement target.
- Updated `docs/ARCHITECTURE.md` with the same locked strategy and the expected Start app structure.
- Updated `TODO-FEATURES.md` so feature `10.0` records that the Start fix should be an owned template replacement rather than a runtime creator shell-out.
- Replaced the root `PLAN.md` stub with a comprehensive restart-safe TanStack Start replacement plan in checkbox format.

## Outcome

- The repository now has a restart-safe plan for the real TanStack Start replacement.
- A fresh-context restart can begin directly with RED on the web scaffold contracts and then GREEN on the owned Start template replacement.
