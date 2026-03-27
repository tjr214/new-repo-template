# Session 119 Summary

## Date and Time

2026-03-24 08:53:17 PM

## Scope

Completed the remaining feature `8.0` work by replacing the legacy Ralph shell/Python wrappers with a native `nurt ralph` command family, adding framework-aware task metadata and config-driven runtime behavior, shipping a fullscreen Textual Ralph TUI, and syncing the scaffold/workflow/docs baseline to the new native path.

## Inputs

- `TODO-FEATURES.md`
- `PLAN.md`
- `PROGRESS.md`
- `docs/LIVING_DOCS.md`
- `docs/ARCHITECTURE.md`
- `README.RALPH.md`
- `docs/tasks/task-template-schema.json`
- `docs/tasks/task-template.yaml`
- `docs/tasks/task-template-example.yaml`
- `docs/workflows/export-to-ralph/workflow.md`
- `docs/workflows/export-to-ralph/steps/step-03-transform.md`
- `docs/workflows/export-to-ralph/steps/step-04-write-file.md`
- `src/new_repo_template/nurt_cli.py`
- `src/new_repo_template/interactive_tui.py`
- `src/new_repo_template/tool_sync_tui.py`
- `src/new_repo_template/scaffold.py`
- `src/new_repo_template/foundation_manifest.py`
- `src/new_repo_template/snapshot_assets/source_manifest.json`
- `pyproject.toml`
- `ralph.config.yaml`
- `tests/contracts/test_nurt_cli_contract.py`
- `tests/contracts/test_ralph_runner_contract.py`
- `tests/contracts/test_ralph_tui_contract.py`
- `tests/contracts/test_root_workspace_contract.py`
- `tests/contracts/test_snapshot_assets_contract.py`
- `tests/contracts/test_installer_scripts_dry_run_contract.py`

## YELLOW Pass

- Re-read the roadmap, active plan, live progress/docs trackers, `README.RALPH.md`, task-template/schema/workflow docs, the current CLI entrypoint, the existing Textual wizard and tools-sync TUI implementations, scaffold/snapshot plumbing, and the legacy Ralph shell/Python scripts before editing.
- Ran `btca status` and `btca resources`, then used `btca ask -r textual` and `btca ask -r rich-docs` to confirm the recommended Textual state-sync/background-worker patterns and compact Rich status-summary renderables for the fullscreen Ralph control surface.
- Locked the implementation scope to the discussed design: `nurt ralph` opens a fullscreen TUI, `ralph.config.yaml` controls models/default/max loops, task files require `metadata.framework`, BMAD tasks use `bmad-master` plus BMAD closeout, standalone tasks use `build` without BMAD closeout, and the legacy Ralph wrappers are removed from both the live repo and the scaffold baseline.

## Changes

- Added `src/new_repo_template/ralph_config.py`, `src/new_repo_template/ralph_tasks.py`, `src/new_repo_template/ralph_runner.py`, and `src/new_repo_template/ralph_tui.py` to own Ralph config resolution, task/schema handling, loop execution, and the fullscreen Textual UI.
- Extended `src/new_repo_template/nurt_cli.py` with the new native command family: `nurt ralph`, `nurt ralph run`, `nurt ralph validate`, and `nurt ralph visualize`.
- Added root/scaffold baseline `ralph.config.yaml`, moved `pyyaml` and `jsonschema` into runtime dependencies in `pyproject.toml`, and updated `src/new_repo_template/scaffold.py` plus `src/new_repo_template/snapshot_assets/source_manifest.json` so generated foundations ship the config file and no longer ship the obsolete Ralph wrappers.
- Updated `docs/tasks/task-template-schema.json`, `docs/tasks/task-template.yaml`, and `docs/tasks/task-template-example.yaml` so Ralph task files now require `metadata.framework` with `bmad` / `standalone` values.
- Updated `README.RALPH.md` and the export-to-RALPH workflow docs so the supported path is now `nurt ralph`, BMAD exports emit `framework: bmad`, and standalone tasks are modeled explicitly.
- Removed `scripts/RALPH.sh`, `scripts/validate_template.py`, and `scripts/visualize_plan.py` from the live repo while keeping only `scripts/synthetic-quotas.sh` in the remaining scripts baseline.
- Added/updated contract coverage in `tests/contracts/test_ralph_runner_contract.py`, `tests/contracts/test_ralph_tui_contract.py`, `tests/contracts/test_nurt_cli_contract.py`, `tests/contracts/test_root_workspace_contract.py`, `tests/contracts/test_snapshot_assets_contract.py`, and `tests/contracts/test_installer_scripts_dry_run_contract.py`.
- Regenerated bundled snapshot metadata with `nurt template-assets validate` so `src/new_repo_template/snapshot_assets/{manifest.json,metadata.json}` match the native Ralph baseline.

## Validation

- `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."` -> passed
- `uv run pytest tests/contracts/test_ralph_runner_contract.py tests/contracts/test_ralph_tui_contract.py tests/contracts/test_nurt_cli_contract.py tests/contracts/test_root_workspace_contract.py tests/contracts/test_snapshot_assets_contract.py tests/contracts/test_installer_scripts_dry_run_contract.py -q` -> 58 passed
- `uv run ruff check src/new_repo_template tests/contracts` -> passed
- `uv run pytest` -> passed

## Outcome

- The supported Ralph runtime surface is now native `nurt`, not scaffolded shell/Python wrapper scripts.
- Generated repos now ship `ralph.config.yaml`, framework-aware task templates, and the updated workflow/docs baseline instead of `scripts/RALPH.sh` and the old helper scripts.
- Feature `8.0` is now fully complete; the next roadmap discussion target is feature `9.0` (`btca.config.jsonc` customization by monorepo composition).
