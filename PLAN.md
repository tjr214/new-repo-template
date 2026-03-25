# Feature 8.0 Plan - Native `nurt ralph`

**Last Updated:** 2026-03-24 08:20:57 PM
**Status:** Ready for implementation
**Roadmap Anchor:** `TODO-FEATURES.md` feature `8.0` remaining slice (`nurt ralph`)
**Previous Cycle Archive:** `docs/archive/plans/PLAN_2026-03-24_07-40-56_PM.md`
**Previous Cycle Summary:** `docs/session-summaries/SESSION_117_SUMMARY.md`

---

## Goal

Replace the remaining legacy RALPH shell/Python scripts with a native `nurt ralph` command family, including a fullscreen Textual TUI, config-driven model selection and loop limits, framework-aware task execution (`bmad` vs `standalone`), native validate/visualize commands, and the required template/workflow/schema updates so generated repos use the new supported path.

This plan is intentionally restart-safe. A future agent resuming from a blank context should treat the decisions in this file as the locked implementation brief unless the user explicitly changes them.

---

## Locked Decisions From Discussion

### 1. Primary UX / Command Surface

- `nurt ralph` with no extra args opens a fullscreen graphical Textual TUI.
- That TUI must detect currently available task files and allow interactive selection from them.
- `nurt ralph run <task-file>` remains available as a direct non-TUI execution path.
- `nurt ralph validate <task-file>` replaces the legacy `scripts/validate_template.py` behavior.
- `nurt ralph visualize <task-file>` replaces the legacy `scripts/visualize_plan.py` behavior.

### 2. TUI Direction

- The RALPH surface should be a dedicated fullscreen TUI, closer in spirit to `nurt sync tools` than to a minimal linear wizard.
- The TUI must expose interactive task selection, interactive model selection, and interactive configuration of maximum loop count.
- The TUI must display the following runtime fields clearly:
  - `Task`
  - `Framework`
  - `Agent`
  - `Current Loop`
  - `Max Loops`
  - `BMAD Closeout`
- `BMAD Closeout` must read `enabled` for BMAD tasks and `disabled` for standalone tasks.
- `Current Loop` starts at `0` before execution and updates live during the loop.
- `Max Loops` defaults to `20`, can be adjusted before a run starts, and becomes read-only during an active run.

### 3. Config File

- The first implementation slice must include a `ralph.config.yaml` config file.
- Config lookup order is locked as:
  1. `./ralph.config.yaml` from the current working directory
  2. user-level app-scoped config file in the platform-appropriate config directory for `nurt`
  3. built-in defaults if no file exists
- Recommended user-level path model:
  - Linux: `~/.config/nurt/ralph.config.yaml`
  - macOS: `~/Library/Application Support/nurt/ralph.config.yaml`
  - Windows: `%APPDATA%/nurt/ralph.config.yaml`
- Config must define:
  - `default_model`
  - `max_loops`
  - `models`
- Default `max_loops` is locked at `20`.
- Models must be data-driven from config, not hardcoded in code.

### 4. Task Framework Mode

- Task YAML files must explicitly declare whether they are BMAD-driven or standalone.
- This must be represented by a required schema field at `metadata.framework`.
- Allowed values are locked as:
  - `bmad`
  - `standalone`
- No implicit default is allowed. Every task file must declare the framework explicitly.

### 5. Agent / Closeout Behavior

- If `metadata.framework: bmad`:
  - main execution agent is `bmad-master`
  - BMAD context is included in loop prompts
  - BMAD closeout prompt runs when the task reaches `done`
- If `metadata.framework: standalone`:
  - main execution agent is `build`
  - BMAD context is not included in implementation prompts
  - no BMAD closeout prompt is run
- Preserve the general task-archiving behavior from the existing RALPH flow unless implementation evidence forces a change.

### 6. Workflow / Template Implications

- The BMAD export-to-RALPH workflow must be updated so exported files always declare `metadata.framework: bmad`.
- Non-BMAD task creation paths must use `metadata.framework: standalone`.
- Generated repos should stop instructing users to run `./scripts/RALPH.sh ...` and should instead point users to `nurt ralph`.
- The legacy live scripts are expected to be removed after native parity is in place:
  - `scripts/RALPH.sh`
  - `scripts/validate_template.py`
  - `scripts/visualize_plan.py`

---

## Recommended Config Shape

```yaml
default_model: openai/gpt-5.4
max_loops: 20

models:
  - id: openai/gpt-5.4
    label: GPT-5.4
  - id: synthetic/hf:nvidia/Kimi-K2.5-NVFP4
    label: Kimi K2.5 NVIDIA
```

Implementation note:
- validate that `default_model` exists in `models`
- validate that `max_loops` is a positive integer
- provide sensible built-in defaults when no config file exists

---

## Required File Inventory

### Existing Files Already Identified As Relevant

- `TODO-FEATURES.md`
- `PLAN.md`
- `PROGRESS.md`
- `docs/ARCHITECTURE.md`
- `README.RALPH.md`
- `src/new_repo_template/nurt_cli.py`
- `src/new_repo_template/interactive_tui.py`
- `src/new_repo_template/tool_sync_tui.py`
- `scripts/RALPH.sh`
- `scripts/validate_template.py`
- `scripts/visualize_plan.py`
- `docs/tasks/task-template-schema.json`
- `src/new_repo_template/snapshot_assets/templates/foundation/docs/tasks/task-template-schema.json`
- `src/new_repo_template/snapshot_assets/templates/foundation/docs/workflows/export-to-ralph/workflow.md`
- `src/new_repo_template/snapshot_assets/templates/foundation/docs/workflows/export-to-ralph/steps/step-03-transform.md`
- `src/new_repo_template/snapshot_assets/templates/foundation/docs/workflows/export-to-ralph/steps/step-04-write-file.md`
- `src/new_repo_template/snapshot_assets/templates/foundation/scripts/RALPH.sh`
- `src/new_repo_template/snapshot_assets/templates/foundation/scripts/validate_template.py`
- `src/new_repo_template/snapshot_assets/templates/foundation/scripts/visualize_plan.py`

### Likely Files To Add

- `src/new_repo_template/ralph_config.py`
- `src/new_repo_template/ralph_runner.py`
- `src/new_repo_template/ralph_tui.py`
- `src/new_repo_template/ralph_tasks.py` or equivalent helper module if task discovery/schema helpers need separation
- `ralph.config.yaml` at repo root as the live baseline config
- `src/new_repo_template/snapshot_assets/templates/foundation/ralph.config.yaml`
- new or expanded contract tests under `tests/contracts/`

### Likely Files To Update For Scaffold / Snapshot Sync

- `src/new_repo_template/scaffold.py`
- `src/new_repo_template/foundation_manifest.py`
- `src/new_repo_template/snapshot_assets/source_manifest.json`
- `src/new_repo_template/snapshot_assets/manifest.json` (regenerated via `nurt template-assets validate`)
- `src/new_repo_template/snapshot_assets/metadata.json` (regenerated via `nurt template-assets validate`)

---

## Implementation Strategy

## YELLOW

Before writing tests or code, complete the full YELLOW pass. This is mandatory.

### YELLOW Read Pass

- Re-read all CLI/TUI entrypoints involved in current native command routing.
- Re-read all legacy RALPH scripts to preserve behavior where intended and intentionally replace behavior where locked decisions differ.
- Re-read the task schema and all export-to-RALPH workflow docs/step files that currently assume BMAD-only execution.
- Re-read the existing Textual implementations for `nurt new`, `nurt add`, and `nurt sync tools` to match house style and reuse patterns.
- Re-read current docs so user-facing guidance and architecture notes stay aligned.

### YELLOW BTCA Pass

- Run `btca status`.
- Run `btca resources`.
- Use `btca ask` for the exact dependency/framework guidance needed before RED. At minimum:
  - Textual fullscreen layout and background-worker patterns for selection + live log streaming + long-running tasks
  - Rich/Textual presentation guidance for concise runtime status panes and log rendering
- If implementation adds another dependency not already covered by BTCA resources, stop and get explicit user confirmation before adding the BTCA resource.

### YELLOW Scope / Behavior Lock

- Confirm native `nurt ralph` command routing shape and help text.
- Confirm the task framework branch behavior (`bmad` vs `standalone`).
- Confirm config lookup precedence and platform-specific fallback paths.
- Confirm task discovery behavior for `nurt ralph` with no args.
- Confirm whether `nurt ralph run <task-file>` should accept overrides such as `--model` and `--max-loops` if needed for parity/usability.
- Confirm how missing task files, invalid config, invalid schema, and no-TTY fallback should be surfaced.

## RED

Add or update failing contract coverage before implementation.

### CLI / Config / Runner Contracts

- Add coverage for `nurt ralph` command routing.
- Add coverage for `nurt ralph run <task-file>`.
- Add coverage for `nurt ralph validate <task-file>` parity with the legacy validator.
- Add coverage for `nurt ralph visualize <task-file>` parity with the legacy visualizer.
- Add coverage for config resolution precedence:
  - project-local config wins
  - user-level config is used when local config is absent
  - built-in defaults are used when both are absent
- Add coverage for config validation:
  - invalid/missing `default_model`
  - empty models list
  - malformed model entries
  - non-positive `max_loops`

### Schema / Framework Contracts

- Update schema contract expectations so `metadata.framework` is required.
- Add coverage that valid values are `bmad` and `standalone` only.
- Add coverage that BMAD-exported task fixtures include `metadata.framework: bmad`.
- Add coverage that standalone task fixtures execute without BMAD closeout behavior.

### TUI Contracts

- Add semantic TUI coverage for:
  - detected task-file selection
  - model selection from config data
  - max-loop editing before execution
  - live display of `Current Loop`
  - live display of `Max Loops`
  - live display of `BMAD Closeout`
  - run-state transition once execution starts
  - empty-state behavior when no task files exist
- Avoid overfitting on exact copy or layout geometry unless necessary; prefer semantic state assertions as established elsewhere in the repo.

### Snapshot / Scaffold / Docs Contracts

- Add or update contract coverage so the scaffold baseline includes `ralph.config.yaml`.
- Add or update coverage so generated docs/workflows reference `nurt ralph` instead of `./scripts/RALPH.sh`.
- Add or update coverage so the legacy RALPH scripts are removed from the live repo and scaffold baseline once native parity is complete.

## GREEN

Implement the smallest coherent native feature set that satisfies the RED contracts.

### Native Config + Task Model

- Implement config loading and validation for `ralph.config.yaml`.
- Implement user-level config path resolution without reaching outside approved project operations during code changes.
- Implement task file discovery for the current repo.
- Implement task YAML loading and framework-aware execution planning.

### Native CLI Surface

- Add `ralph` command routing in `src/new_repo_template/nurt_cli.py`.
- Support:
  - `nurt ralph`
  - `nurt ralph run <task-file>`
  - `nurt ralph validate <task-file>`
  - `nurt ralph visualize <task-file>`
- Decide whether direct-run overrides such as `--model` / `--max-loops` are needed during implementation; if added, keep them aligned with config semantics.

### Native Validate / Visualize

- Move validator behavior from `scripts/validate_template.py` into a native module/function.
- Move visualizer behavior from `scripts/visualize_plan.py` into a native module/function.
- Keep output behavior close enough to the legacy scripts that workflow docs and operators retain confidence.

### Native Fullscreen TUI

- Build a dedicated Textual TUI for `nurt ralph`.
- Use established Textual patterns already present in the repo for bindings, background workers, status tables, and log panes.
- Ensure the TUI can:
  - select a task file
  - inspect detected framework
  - derive the correct execution agent
  - select a model from config
  - adjust `Max Loops`
  - display `Current Loop`
  - display `BMAD Closeout`
  - stream logs live during execution
  - surface success/failure/final state clearly

### Framework-Aware Loop Execution

- Reimplement the RALPH loop behavior natively.
- For `bmad` tasks:
  - build prompts with BMAD context included
  - run BMAD closeout after successful completion
- For `standalone` tasks:
  - use `build` as the agent
  - omit BMAD context from prompts
  - skip BMAD closeout entirely
- Keep loop count enforcement aligned with `max_loops`.

### Workflow / Template / Schema Updates

- Update `docs/tasks/task-template-schema.json` and the foundation snapshot copy to require `metadata.framework`.
- Update the export-to-RALPH workflow so BMAD exports write `framework: bmad`.
- Update generated instructions/docs/examples to call `nurt ralph`.
- Add `ralph.config.yaml` to the live repo baseline and the scaffolded foundation baseline.
- Remove the legacy RALPH scripts from the live repo and scaffold baseline after native replacements are fully wired.

## BLUE

Refactor, harden, and align the final implementation.

### Hardening

- Consolidate duplicated task/config parsing helpers if they emerge.
- Improve error handling for:
  - missing task files
  - empty task directory
  - malformed YAML
  - invalid framework values
  - invalid config values
  - missing `opencode`
  - interrupted runs / cancelled TUI sessions
- Ensure live loop state is reflected accurately in the TUI while background work runs.

### UX Polish

- Keep the TUI readable on normal laptop terminal sizes.
- Ensure footer bindings are discoverable and consistent with existing native TUIs.
- Keep the runtime status language explicit and operator-friendly.
- Prefer semantic status cues and compact summaries over noisy terminal output.

### Validation / Cleanup

- Regenerate bundled snapshot artifacts with `nurt template-assets validate` after template/baseline changes.
- Confirm no stale docs or scaffold manifests still reference removed RALPH scripts.
- Confirm the framework-aware behavior is consistent across CLI, TUI, docs, schema, and workflow files.

---

## Validation Plan

### Targeted Validation

- `uv run pytest tests/contracts/test_nurt_cli_contract.py`
- `uv run pytest` for any new RALPH-specific contract files added during RED
- `uv run ruff check src/new_repo_template tests/contracts`
- `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."`

### Full Validation

- `uv run pytest`

### Manual / Behavioral Validation Expectations

- `nurt ralph` launches the fullscreen TUI.
- The TUI detects available task files.
- The TUI reads models from config instead of a hardcoded list.
- The TUI shows framework-derived `Agent` and `BMAD Closeout` values correctly.
- `Max Loops` defaults to `20` and can be changed before run.
- `Current Loop` updates during execution.
- `nurt ralph validate <task-file>` reports schema status correctly.
- `nurt ralph visualize <task-file>` renders the plan summary/structure correctly.
- BMAD-exported tasks use BMAD mode; standalone tasks use build mode.

---

## Documentation Sync Requirements

These updates are mandatory as implementation sections complete:

- Update `PROGRESS.md`.
- Update `docs/LIVING_DOCS.md`.
- Update `docs/ARCHITECTURE.md`.
- Create a new session summary in `docs/session-summaries/`.
- Update `README.RALPH.md`.
- Update any affected export-to-RALPH workflow docs and generated baseline docs.

Never overwrite an existing session summary. Create a new one with a fresh timestamped record.

---

## Definition Of Done

- `nurt ralph` is the supported native entrypoint for the RALPH loop.
- The fullscreen RALPH TUI is implemented and usable.
- Models and loop limits are config-driven through `ralph.config.yaml`.
- Task files require explicit `metadata.framework` values.
- Framework-aware branching between BMAD and standalone execution is working.
- Native `validate` and `visualize` commands replace the legacy scripts.
- Live repo docs, scaffold baseline, snapshot assets, and workflow docs all point to `nurt ralph`.
- Legacy RALPH scripts are removed from the live repo and scaffold baseline.
- Targeted and full validation are green.
- `PROGRESS.md`, `docs/LIVING_DOCS.md`, `docs/ARCHITECTURE.md`, and a new session summary are synchronized with the implementation outcome.

---

## Resume Notes

If resuming from a fresh context, do not re-decide the following unless the user explicitly asks to change them:

- `nurt ralph` with no args opens a fullscreen TUI
- task YAML requires `metadata.framework`
- framework enum is `bmad | standalone`
- BMAD tasks use `bmad-master` plus BMAD closeout
- standalone tasks use `build` and no BMAD closeout
- config file name is `ralph.config.yaml`
- config lookup order is local file -> user-level app config -> built-in defaults
- config includes `default_model`, `models`, and `max_loops`
- default `max_loops` is `20`
- runtime status field is named `BMAD Closeout`

Resume from YELLOW if the code has not been changed yet. Resume from the first incomplete RED/GREEN/BLUE item if implementation has already begun.
