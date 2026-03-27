# Session 126 Summary

## Date and Time

2026-03-26 09:21:21 PM

## Scope

Linked `nurt sync tools` to the repo's version-governance metadata so Bun/Turbo upgrades now refresh `version-baseline.json` automatically.

## YELLOW Pass

- Re-read `src/new_repo_template/{tool_sync_runner.py,sync_ops.py,tool_sync_tui.py,version_baseline.py}` plus the current tool-sync and version-baseline contracts before editing.
- Reviewed the existing `version-baseline.json` shape and the current maintainer-policy docs to confirm the baseline file is the source of truth for tracked tool versions.
- Used `btca ask -r bun -r turborepo` to confirm the script-friendly installed-version commands (`bun --version` / `bun -v` and `turbo --version`) and keep the version-capture assumptions grounded in official behavior.

## Implementation

- Added reusable baseline-application helpers in `src/new_repo_template/version_baseline.py` so targeted managed-tool versions can be written back to `version-baseline.json` without rerunning the full latest-version update flow.
- Updated `src/new_repo_template/tool_sync_runner.py` so non-dry-run tool syncs now extract the post-sync Bun/Turbo versions from successful `INSTALLED` / `UPDATED` results, refresh `version-baseline.json` when present, and carry the resulting diffs in `ToolSyncSummary`.
- Updated `src/new_repo_template/sync_ops.py` and `src/new_repo_template/tool_sync_tui.py` so plain and TUI `nurt sync tools` flows both surface the baseline refresh diff after a successful Bun/Turbo upgrade.
- Synced the maintainer-governance note across `PROGRESS.md`, `docs/LIVING_DOCS.md`, `docs/ARCHITECTURE.md`, and `docs/DEPENDENCY_UPGRADE_POLICY.md`.

## RED / BLUE Coverage

- Expanded `tests/contracts/test_tool_sync_runner_contract.py` so the runner contract now verifies that Bun/Turbo tool-sync updates rewrite the matching `version-baseline.json` entries and return the expected baseline diffs.

## Validation

- `uv run pytest tests/contracts/test_tool_sync_runner_contract.py tests/contracts/test_version_baseline_contract.py`
- `uv run pytest tests/contracts/test_tool_sync_tui_contract.py tests/contracts/test_nurt_cli_contract.py`

## Outcome

- `nurt sync tools` now keeps Bun/Turbo baseline metadata aligned with real maintainer tool upgrades instead of leaving `version-baseline.json` stale until a separate manual `nurt versions update` run.
