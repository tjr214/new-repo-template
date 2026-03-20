# Python and TypeScript CLI/TUI Plan

**Last Updated:** 2026-03-13 04:47:07 PM
**Status:** Complete
**Previous Cycle Archive:** `docs/archive/plans/PLAN_2026-03-12_06-50-03_PM.md`
**Previous Cycle Summary:** `docs/session-summaries/SESSION_87_SUMMARY.md`

---

## Goal

Complete the Python CLI/TUI scaffold upgrade and add the new Bun-native TypeScript CLI scaffold.

---

## YELLOW

- [x] Read the repo files, tests, and documentation relevant to the next slice before editing.
- [x] Run `btca status`, `btca resources`, and `btca ask` for dependency guidance affecting the next slice.
- [x] Add the missing project BTCA resource for `uv` and sync `docs/BTCA_RESOURCES.md`.
- [x] Confirm scope, constraints, and validation targets for the Python lane upgrade plus the new `typescript-cli` target.

## RED

- [x] Add or update failing tests/contracts for the Python CLI/TUI lane, the new `typescript-cli` target, CLI validation, security/env coverage, preset-matrix coverage, and interactive `nurt` flows.

## GREEN

- [x] Upgrade the `python` scaffold into a real Rich + Textual lane with packaged entry points, starter modules, and stronger docs/tests.
- [x] Add the Bun-native `typescript-cli` scaffold target with workspace-linked `bin`, starter source files, README guidance, and runtime smoke coverage.

## BLUE

- [x] Refactor and harden the implementation, rerun targeted contracts, refresh bundled snapshot metadata with `nurt template-assets validate`, and rerun repo-wide validation.

## Documentation Sync

- [x] Update `PROGRESS.md`.
- [x] Update `docs/LIVING_DOCS.md`.
- [x] Update `docs/ARCHITECTURE.md`.
- [x] Create a new session summary in `docs/session-summaries/`.
