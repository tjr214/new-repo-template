# Session 85 Summary

## Date and Time

2026-03-12 06:18:18 PM

## Scope

Implemented the full post-create automation slice for `nurt`: optional BMAD install, generated-project git initialization and initial commit, and a native core-tools updater TUI with standalone CLI entrypoints.

## Inputs

- `PLAN.md`
- `PROGRESS.md`
- `docs/LIVING_DOCS.md`
- `docs/ARCHITECTURE.md`
- `src/new_repo_template/nurt_cli.py`
- `src/new_repo_template/interactive_ui.py`
- `src/new_repo_template/interactive_tui.py`
- `src/new_repo_template/sync_ops.py`
- `.template_scripts/update-opencode.sh`
- `.template_scripts/update-bmad-method.sh`
- `tests/contracts/`

## Implementation

- Added native post-create orchestration in `src/new_repo_template/post_create.py` so scaffolded projects now follow the requested lifecycle: optional BMAD -> lockfiles/revalidation -> `git init` -> `git add .` -> `git commit -m "Initial Commit"` -> optional core-tools updater.
- Added `src/new_repo_template/bmad_runner.py` and a new `nurt bmad sync` command for standalone BMAD install/update flows, with explicit external-process handoff instead of re-rendering the BMAD installer UI.
- Extended `src/new_repo_template/nurt_cli.py`, `src/new_repo_template/interactive_ui.py`, and `src/new_repo_template/interactive_tui.py` so both the Textual wizard and the plain fallback flow collect optional core-tools and BMAD decisions, while non-interactive CLI usage can drive the same behavior with flags.
- Refactored native tool syncing into `src/new_repo_template/tool_sync_runner.py` plus `src/new_repo_template/tool_sync_tui.py`, then wired `src/new_repo_template/sync_ops.py` so `nurt tools sync` uses the Textual status-table/log UI in rich TTY sessions and deterministic text output elsewhere.
- Brought native core-tools sync coverage up to the managed set from the legacy updater reference: `uv`, `bun`, `turbo`, `opencode`, `btca`, `gh`, and `ripgrep`.
- Added RED/GREEN contract coverage for the new wizard state, CLI dry-run reporting, post-create orchestration, BMAD runner, reusable tool-sync runner, and the new updater TUI.

## Verification

- `uv run pytest tests/contracts/test_interactive_tui_contract.py tests/contracts/test_nurt_cli_contract.py tests/contracts/test_post_create_contract.py tests/contracts/test_bmad_runner_contract.py tests/contracts/test_tool_sync_runner_contract.py tests/contracts/test_tool_sync_tui_contract.py -q`
- `uv run pytest`

## Documentation Sync

- Updated `PLAN.md`.
- Updated `PROGRESS.md`.
- Updated `docs/LIVING_DOCS.md`.
- Updated `docs/ARCHITECTURE.md`.

## Outcome

- `nurt new` now owns the requested end-to-end post-create lifecycle, generated projects receive an initial git commit automatically, BMAD has a standalone native entrypoint, and core-tools sync now has a real native Textual updater UI plus shared execution engine.
