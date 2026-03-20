# Feature 6 Implementation Plan

**Last Updated:** 2026-03-19 07:01:28 PM
**Status:** Completed and fully validated
**Latest Completed Implementation Summary:** `docs/session-summaries/SESSION_116_SUMMARY.md`
**Current Planning Summary:** `docs/session-summaries/SESSION_114_SUMMARY.md`
**Latest Plan Archive:** `docs/archive/plans/PLAN_2026-03-19_04-33-30_PM.md`

---

## Goal

Implement feature `6.0` by migrating Python packaging from Hatchling to `uv_build` in the places that are actual Python packages, while keeping generated root Python workspace files as coordinator-only uv workspace roots.

---

## Current State Snapshot

- The live repo root package now uses `uv_build` in `pyproject.toml` with explicit `tool.uv.build-backend` settings for the `new_repo_template` module layout.
- The generated Python app template now uses `uv_build` in `src/new_repo_template/snapshot_assets/templates/python_lane_pyproject.toml`.
- The generated Python library template now uses `uv_build` in `src/new_repo_template/snapshot_assets/templates/python_lib/python_lib_pyproject.toml`.
- Generated root Python workspace files remain separate from package-member `pyproject.toml` files and now explicitly act as coordinator-only roots via `[tool.uv] package = false` and no `[build-system]`.
- The active contract suite now validates both generated-package `uv build` behavior and the live repo root-package `uv build` path alongside the existing generated `uv sync` / `uv run` behavior.
- Bundled snapshot metadata and the template-sync manifest state are refreshed and back in sync after the migration closeout.
- There are no pre-existing nurt-generated repos in the field, so this feature does not need compatibility shims, dual-backend support, or migration helpers for older generated outputs.

---

## YELLOW Findings

The required YELLOW pass for this feature has already been completed before planning was finalized.

### Files Read During YELLOW

- `PLAN.md`
- `PROGRESS.md`
- `docs/LIVING_DOCS.md`
- `docs/ARCHITECTURE.md`
- `TODO-FEATURES.md`
- `docs/session-summaries/SESSION_113_SUMMARY.md`
- `pyproject.toml`
- `src/new_repo_template/snapshot_assets/templates/python_lane_pyproject.toml`
- `src/new_repo_template/snapshot_assets/templates/python_lib/python_lib_pyproject.toml`
- `src/new_repo_template/snapshot_assets/templates/root_python_workspace_pyproject.toml`
- `src/new_repo_template/snapshot_assets/templates/root_pyproject_base.toml`
- `src/new_repo_template/scaffold.py`
- `src/new_repo_template/add_mode.py`
- `src/new_repo_template/snapshot_assets/templates/foundation/AGENTS.md`
- `src/new_repo_template/snapshot_assets/templates/foundation/.agent/rules/general-rules.md`
- `tests/contracts/test_python_lane_contract.py`
- `tests/contracts/test_python_lib_scaffold_contract.py`
- `tests/contracts/test_version_baseline_contract.py`

### BTCA Work Completed During YELLOW

- Ran `btca status`.
- Ran `btca ask -r uv -q "What does uv build do? Does it replace the build backend, or does it invoke the build backend declared in pyproject.toml such as hatchling?" --sub-agent`.
- Ran `btca ask -r uv -q "When should a pure Python project use uv_build instead of hatchling? What are the main limitations or tradeoffs?" --sub-agent`.
- Ran `btca ask -r uv -q "Should uv_build use a bounded version range in build-system requires and should a workspace root that is only a coordinator omit build-system and optionally set tool.uv.package false" --sub-agent`.

### YELLOW Conclusions

- `uv build` is a frontend command. It does not replace the configured backend; it invokes the backend declared in `[build-system]`.
- The real decision is therefore not "Hatchling or uv build" but rather:
  - keep Hatchling as backend and standardize on `uv build` as the frontend command, or
  - migrate packaged Python projects to `uv_build` and still use `uv build` as the frontend command.
- The generated Python app and generated Python library are both strong `uv_build` candidates because they are pure-Python, `src`-layout packages.
- The repo root package is also a viable `uv_build` candidate, but it needs explicit `tool.uv.build-backend` settings because the project name (`nurt-ai`) does not match the actual module path (`src/new_repo_template`).
- A coordinator-only workspace root should omit `[build-system]`; adding `[tool.uv] package = false` is a good explicit intent signal.
- `uv_build` should use a bounded compatible range in `[build-system].requires`.
- Runtime JSON/YAML/data files are compatible with `uv_build` as long as they live inside `src/<module>/...` and are treated as package resources.

---

## Locked Decisions

- Migrate the repo root package from Hatchling to `uv_build`.
- Migrate the generated Python app template from Hatchling to `uv_build`.
- Migrate the generated Python library template from Hatchling to `uv_build`.
- Keep generated root Python workspace files as coordinator-only uv workspace files.
- Generated root Python workspace files must omit `[build-system]`.
- Generated root Python workspace files should explicitly set `[tool.uv] package = false`.
- Standardize on `uv build` as the build frontend command.
- Treat `uv_build` as a special-case versioning exception that uses a bounded compatible range in `[build-system].requires`.
- Runtime Python package data should live inside `src/<module>/...` and be loaded as package resources.
- No backward-compatibility shim is needed for older generated repos because there are no such repos yet.

---

## Explicit Non-Goals

- Do not implement feature `7.0` (`nurt upgrade`) as part of this slice.
- Do not redesign the Python workspace topology (`root pyproject.toml` + member packages) beyond the explicit coordinator-root clarification.
- Do not add migration helpers for hypothetical older generated repos.
- Do not change the general Python dependency policy for ordinary runtime/dev dependencies; the bounded-range exception only applies to `uv_build` in `[build-system].requires`.
- Do not move runtime JSON/YAML/data files outside the package tree.
- Do not broaden this slice into packaging changes for TypeScript/Bun targets.

---

## Execution Scope

### Root Package

- Update `pyproject.toml` from Hatchling to `uv_build`.
- Add explicit `tool.uv.build-backend` configuration for the root package because the module name does not match the project name.
- Preserve the current source-distribution intent (including `tests/**`) during the migration.

### Generated Python App Template

- Update `src/new_repo_template/snapshot_assets/templates/python_lane_pyproject.toml` from Hatchling to `uv_build`.
- Keep the current `project.scripts`, dependency groups, and optional workspace-library wiring intact.

### Generated Python Library Template

- Update `src/new_repo_template/snapshot_assets/templates/python_lib/python_lib_pyproject.toml` from Hatchling to `uv_build`.
- Remove now-unnecessary Hatch-specific build-target configuration if `uv_build` defaults cover the package layout.

### Generated Root Python Workspace Template

- Update `src/new_repo_template/snapshot_assets/templates/root_python_workspace_pyproject.toml` so the workspace root explicitly sets `[tool.uv] package = false`.
- Keep this file free of `[build-system]`.

### Supporting Template/Guidance Files

- Update the generated guidance that still says Python projects should use Hatchling as the build backend:
  - `src/new_repo_template/snapshot_assets/templates/foundation/AGENTS.md`
  - `src/new_repo_template/snapshot_assets/templates/foundation/.agent/rules/general-rules.md`
- Update the live root `AGENTS.md` if the same guidance is present there and should stay aligned with the new repo policy.

### Contracts and Validation Coverage

- Update existing Python contract expectations from Hatchling to `uv_build` where appropriate.
- Add or extend contract coverage for generated root Python workspace files to assert `[tool.uv] package = false` and no `[build-system]`.
- Add build-oriented coverage so generated Python packages are validated with `uv build`, not only `uv sync` / `uv run`.
- Update version-baseline fixtures that currently hardcode Hatchling build-system blocks.

### Snapshot Metadata

- After template changes, rerun `nurt template-assets validate` so bundled snapshot metadata stays aligned with the edited packaged template files.

---

## RED

Update or add contract coverage before implementation.

### Existing Tests To Update

- `tests/contracts/test_python_lane_contract.py`
  - Keep existing `uv sync` / `uv run` assertions.
  - Add or extend assertions so generated app package metadata reflects `uv_build`.
  - Add a build-success path for `uv build --package python-app`.
- `tests/contracts/test_python_lib_scaffold_contract.py`
  - Keep workspace/dependency/runtime assertions.
  - Add or extend assertions so generated library package metadata reflects `uv_build`.
  - Add a build-success path for `uv build --package python-lib`.
- `tests/contracts/test_version_baseline_contract.py`
  - Replace Hatchling-based sample `pyproject.toml` fixtures with `uv_build`-based or otherwise feature-6-aligned fixtures.

### New Or Expanded Assertions Needed

- Generated root Python workspace `pyproject.toml` contains `[tool.uv] package = false`.
- Generated root Python workspace `pyproject.toml` does not declare a `[build-system]` table.
- Repo root `pyproject.toml` build-system uses `uv_build` with a bounded compatible range.
- Repo root `pyproject.toml` includes explicit `tool.uv.build-backend` settings sufficient for the `new_repo_template` module layout.
- `uv build` succeeds at the repo root.

---

## GREEN

Implement the smallest coherent change set that satisfies the updated contracts.

### Planned Edits

- `pyproject.toml`
  - switch `[build-system]` to `uv_build`
  - add bounded compatible requirement
  - add `tool.uv.build-backend` settings for `module-name`, `module-root`, and source include behavior
- `src/new_repo_template/snapshot_assets/templates/python_lane_pyproject.toml`
  - switch `[build-system]` to `uv_build`
  - use bounded compatible requirement
- `src/new_repo_template/snapshot_assets/templates/python_lib/python_lib_pyproject.toml`
  - switch `[build-system]` to `uv_build`
  - use bounded compatible requirement
  - remove Hatch-only package-target config if redundant
- `src/new_repo_template/snapshot_assets/templates/root_python_workspace_pyproject.toml`
  - add `[tool.uv] package = false`
- `src/new_repo_template/snapshot_assets/templates/root_pyproject_base.toml`
  - update if it still participates in active scaffold/runtime expectations
- `src/new_repo_template/snapshot_assets/templates/foundation/AGENTS.md`
  - replace the old Python build-backend guidance
- `src/new_repo_template/snapshot_assets/templates/foundation/.agent/rules/general-rules.md`
  - replace the old Python build-backend guidance
- `AGENTS.md`
  - update if needed to keep the live repo policy aligned with the generated guidance

### Keep Intact

- Current Python app/library directory layout
- Current Python dependency-group strategy
- Current app-to-library workspace dependency wiring via `[tool.uv.sources]`
- Current root uv workspace membership rendering in `src/new_repo_template/scaffold.py` / `src/new_repo_template/add_mode.py`

---

## BLUE

After GREEN passes, harden and synchronize.

- Remove any stale active-path references to Hatchling in docs/guidance/templates that should now describe the new policy.
- Confirm the generated root workspace model stays clearly separated from package-member build metadata.
- Confirm root-package `uv_build` config is explicit and minimal, not over-configured.
- Regenerate bundled snapshot metadata after template edits.
- Sync `PROGRESS.md`, `docs/LIVING_DOCS.md`, and `docs/ARCHITECTURE.md` with the completed implementation state.
- Create a new post-implementation session summary after the implementation slice is complete.

---

## Validation Plan

Run these validations during or after implementation.

### Targeted Contracts

```bash
uv run pytest tests/contracts/test_python_lane_contract.py tests/contracts/test_python_lib_scaffold_contract.py tests/contracts/test_version_baseline_contract.py
```

### Snapshot Metadata Refresh

```bash
uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."
```

### Root Package Build

```bash
uv build
```

### Generated Python Package Build Checks

Generate temporary Python outputs and verify:

```bash
uv build --package python-app
uv build --package python-lib
```

### Lint And Full Suite

```bash
uv run ruff check src/new_repo_template tests/contracts
uv run pytest
```

---

## Risks And Watchpoints

- The repo root package name (`nurt-ai`) does not match its importable module (`new_repo_template`), so explicit `tool.uv.build-backend` config is required.
- The current root package includes bundled snapshot assets under `src/new_repo_template/snapshot_assets/**`; verify those remain included correctly after the backend migration.
- If any active contract or helper assumes Hatch-specific config tables, update it during RED rather than papering over failures in GREEN.
- Keep the coordinator-root rule clear: generated root Python workspace files are not publishable packages and should not gain a `[build-system]` table during this slice.

---

## Fresh-Context Restart

If context is cleared before implementation begins, use this exact restart sequence.

### Step 1: Read These Files In Order

1. `PLAN.md`
2. `PROGRESS.md`
3. `docs/LIVING_DOCS.md`
4. `docs/ARCHITECTURE.md`
5. `TODO-FEATURES.md`
6. `docs/session-summaries/SESSION_114_SUMMARY.md`
7. `pyproject.toml`
8. `src/new_repo_template/snapshot_assets/templates/python_lane_pyproject.toml`
9. `src/new_repo_template/snapshot_assets/templates/python_lib/python_lib_pyproject.toml`
10. `src/new_repo_template/snapshot_assets/templates/root_python_workspace_pyproject.toml`
11. `src/new_repo_template/snapshot_assets/templates/root_pyproject_base.toml`
12. `src/new_repo_template/scaffold.py`
13. `src/new_repo_template/add_mode.py`
14. `src/new_repo_template/snapshot_assets/templates/foundation/AGENTS.md`
15. `src/new_repo_template/snapshot_assets/templates/foundation/.agent/rules/general-rules.md`
16. `tests/contracts/test_python_lane_contract.py`
17. `tests/contracts/test_python_lib_scaffold_contract.py`
18. `tests/contracts/test_version_baseline_contract.py`

### Step 2: Re-Run YELLOW Tooling Checks

```bash
btca status
```

```bash
btca ask -r uv -q "Should uv_build use a bounded version range in build-system requires and should a workspace root that is only a coordinator omit build-system and optionally set tool.uv.package false" --sub-agent
```

If needed, also re-run:

```bash
btca ask -r uv -q "What does uv build do? Does it replace the build backend, or does it invoke the build backend declared in pyproject.toml such as hatchling?" --sub-agent
```

### Step 3: Resume Execution In Order

1. Update/add RED contract coverage.
2. Implement GREEN packaging/template edits.
3. Refresh bundled snapshot metadata.
4. Run targeted validation.
5. Run `uv build` and generated-package build checks.
6. Run lint and the full test suite.
7. Sync docs and write the post-implementation session summary.

---

## Immediate Next Execution Steps

1. Edit the Python/package-related contracts first.
2. Migrate the root package to `uv_build`.
3. Migrate the generated Python app/library templates to `uv_build`.
4. Add `[tool.uv] package = false` to the generated root Python workspace template.
5. Update generated/live guidance that still says Python projects must use Hatchling.
6. Refresh bundled snapshot metadata.
7. Run targeted tests, then `uv build`, then lint, then full `uv run pytest`.
8. Sync docs to the implemented state and write the post-implementation session summary.
