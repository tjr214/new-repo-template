# Interactive TUI Stability Fixes

**Last Updated:** 2026-03-12 04:45:09 PM
**Status:** Complete
**Previous Cycle Summary:** `docs/session-summaries/SESSION_80_SUMMARY.md`

---

## Goal

Fix the project-name input instability in the Textual wizard and ensure the project-name step appears only when the project name is not already provided on the command line.

---

## YELLOW

- [x] Reread `src/new_repo_template/interactive_tui.py`, `src/new_repo_template/nurt_cli.py`, and `tests/contracts/test_interactive_tui_contract.py` before editing.
- [x] Reread `PROGRESS.md`, `docs/LIVING_DOCS.md`, and `docs/ARCHITECTURE.md` before editing.
- [x] Run `btca status` and use `btca ask` for Textual guidance on stable `Input.Changed` handling and conditional first-step flow.

## RED

- [x] Add failing tests for stable project-name typing under rapid spacing/special-character-like input.
- [x] Add failing tests so the project-name step is skipped when a project name is already known.

## GREEN

- [x] Stop broad wizard refresh/refocus work on every project-name `Input.Changed` event.
- [x] Keep derived summary/output-path updates live while leaving the active input widget stable.
- [x] Skip the project-name step entirely when `nurt new <project-name>` already supplied a normalized project name.

## BLUE

- [x] Tighten first-step/back-navigation semantics so Escape exits when the first real step is `targets`.
- [x] Re-run targeted tests, then the full suite once the fix is stable.

## Documentation Sync

- [x] Update `PROGRESS.md`.
- [x] Update `docs/LIVING_DOCS.md`.
- [x] Update `docs/ARCHITECTURE.md`.
- [x] Create a new session summary in `docs/session-summaries/` for this execution cycle.
