# Session 120 Summary

## Date and Time

2026-03-24 10:12:01 PM

## Scope

Hardened the native Ralph TUI lifecycle so the agent loop only starts on explicit user action, the active model cannot change mid-run, long `opencode` output wraps in the log pane, and exiting or terminating `nurt` force-stops the running `opencode` process instead of orphaning it.

## Inputs

- `src/new_repo_template/ralph_tui.py`
- `src/new_repo_template/ralph_runner.py`
- `tests/contracts/test_ralph_tui_contract.py`
- `tests/contracts/test_ralph_runner_contract.py`
- `tests/contracts/test_nurt_cli_contract.py`
- `PROGRESS.md`
- `docs/LIVING_DOCS.md`
- `docs/ARCHITECTURE.md`

## YELLOW Pass

- Re-read the active Ralph TUI and runner implementations before editing, then checked `opencode --help` and `opencode run --help` to confirm the CLI invocation shape.
- Reproduced the reported bug in a Textual test harness and confirmed the original symptoms were not caused by `opencode` startup semantics alone.
- Ran `btca status`, `btca resources`, and `btca ask -r textual` for the recommended Textual pattern for background workers that own subprocesses and need explicit terminate/cleanup behavior on app exit.

## Changes

- Added process-group-aware Ralph run control in `src/new_repo_template/ralph_runner.py` via `RalphRunController`, explicit stop requests, and best-effort process-group termination for active `opencode` runs.
- Updated `src/new_repo_template/ralph_tui.py` so active runs lock the task/model/max-loop widgets, expose a dedicated `Terminate` button, wrap the `RichLog` output, and kill the active run on both manual termination and app shutdown.
- Preserved the launch/run status messaging (`Launching Agent Loop...` -> `Agent Loop Running...`) while making termination surface as a distinct final state.
- Expanded contract coverage in `tests/contracts/test_ralph_runner_contract.py` and `tests/contracts/test_ralph_tui_contract.py` to cover active-process termination, run-time control locking, wrapped logs, and terminate-button behavior.

## Validation

- `uv run pytest tests/contracts/test_ralph_runner_contract.py tests/contracts/test_ralph_tui_contract.py tests/contracts/test_nurt_cli_contract.py -q` -> 42 passed
- `uv run ruff check src/new_repo_template tests/contracts` -> passed

## Outcome

- Native Ralph runs now require an explicit start, prevent model changes mid-flight, and no longer leave `opencode` alive after a terminate action or app exit.
