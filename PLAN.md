# Interactive TUI Follow-Up

**Last Updated:** 2026-03-12 04:14:59 PM
**Status:** Complete
**Previous Cycle Summary:** `docs/session-summaries/SESSION_78_SUMMARY.md`

---

## Goal

Refine the new `nurt new` wizard so it can collect the project name itself, make backend auth explicit without requiring `web`, simplify the step flow, and align the keyboard/cancel behavior with the updated interaction rules.

---

## YELLOW

- [x] Reread `src/new_repo_template/nurt_cli.py`, `src/new_repo_template/interactive_tui.py`, `src/new_repo_template/interactive_ui.py`, and `src/new_repo_template/scaffold.py` before editing.
- [x] Reread the active interactive/auth contract coverage in `tests/contracts/test_nurt_cli_contract.py`, `tests/contracts/test_interactive_tui_contract.py`, `tests/contracts/test_target_matrix_and_auth_contract.py`, and `tests/contracts/test_cli_validation_and_python_commands_contract.py`.
- [x] Reread `PLAN.md`, `PROGRESS.md`, `docs/LIVING_DOCS.md`, and `docs/ARCHITECTURE.md` before editing.
- [x] Run `btca status` and keep project BTCA resources in sync with `docs/BTCA_RESOURCES.md`.
- [x] Run `btca ask` lookups for Textual input-step validation, Enter/Escape/Ctrl+Q key handling, and screen-navigation patterns before coding.

## RED

- [x] Add failing tests for `nurt new --dry-run` with no project name so the interactive flow collects and normalizes it.
- [x] Add failing tests for backend-driven auth rules, including explicit `none` auth and backend-only auth validity.
- [x] Add failing tests for the new keybinding behavior: Enter to advance, Escape to go back or exit, and Ctrl+Q quit.
- [x] Add failing coverage for the updated friendly wizard-cancel message.

## GREEN

- [x] Make `project_name` optional in `nurt new` and collect it interactively when omitted.
- [x] Normalize interactive project names to kebab-case directory names before scaffold handoff.
- [x] Remove the welcome step and replace it with a project-name step.
- [x] Change auth gating from `web + backend` to `backend`, and support an explicit `none` auth choice.
- [x] Update scaffold validation so backend selections require `--auth clerk`, `--auth better-auth`, or `--auth none` in non-interactive mode.
- [x] Update wizard/plain interactive copy and cancel messaging to match the new UX rules.

## BLUE

- [x] Rework the Textual wizard bindings so Enter advances/confirms, Escape navigates back or exits from the first step, and Ctrl+Q/Ctrl+C quit.
- [x] Keep SelectionList multi-select behavior on Space without letting Enter toggle selections.
- [x] Widen the summary pane slightly so scaffold details breathe more comfortably.
- [x] Re-run targeted tests, then the full suite once the slice is stable.

## Documentation Sync

- [x] Update `PROGRESS.md`.
- [x] Update `docs/LIVING_DOCS.md`.
- [x] Update `docs/ARCHITECTURE.md`.
- [x] Create a new session summary in `docs/session-summaries/` for this execution cycle.
