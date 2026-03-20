# Session 111 Summary

## Date and Time

2026-03-18 07:54:25 PM

## Scope

Fixed the `nurt add` Textual wizard so existing project-name collisions are caught inline during the naming step instead of failing only after the wizard returns control to the CLI.

## Inputs

- `src/new_repo_template/interactive_tui.py`
- `src/new_repo_template/nurt_cli.py`
- `src/new_repo_template/add_mode.py`
- `tests/contracts/test_interactive_tui_contract.py`
- `tests/contracts/test_nurt_add_contract.py`
- `PROGRESS.md`
- `docs/LIVING_DOCS.md`
- `docs/ARCHITECTURE.md`

## Implementation

- Ran a focused YELLOW pass by rereading the add-wizard state machine and add-mode inventory logic.
- Used `btca ask -r textual` to confirm the wizard should treat this as step-local inline validation and block advancement until the input becomes valid.
- Extended the add wizard state to carry the live repo project inventory and compute step-local project-name collision errors.
- Updated the add wizard UI so the naming step now surfaces collision feedback inline, disables Next while the collision remains, and keeps the user on the same step until the name is corrected.
- Wired `nurt add` CLI orchestration to pass the existing repo project keys into the Textual add wizard.
- Added regression coverage proving that a colliding default name is blocked in place and that advancing works again once the user enters a unique name.

## Verification

- `uv run pytest tests/contracts/test_interactive_tui_contract.py tests/contracts/test_nurt_add_contract.py`
- `uv run ruff check src/new_repo_template tests/contracts`
- `uv run pytest`

## Documentation Sync

- Updated `PROGRESS.md`.
- Updated `docs/LIVING_DOCS.md`.
- Updated `docs/ARCHITECTURE.md`.

## Outcome

- Add-mode name collisions are now resolved inside the TUI, so users do not have to restart `nurt add` just to correct a project name.
