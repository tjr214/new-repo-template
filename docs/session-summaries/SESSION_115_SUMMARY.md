# Session 115 Summary

## Date and Time

2026-03-19 06:51:00 PM

## Scope

Implemented feature `6.0` end to end: migrated the live repo root package and generated Python package templates from Hatchling to `uv_build`, kept generated root Python workspace files coordinator-only, refreshed bundled snapshot metadata, resolved the manifest-driven template-sync allowlist mismatch exposed during BLUE validation, and synchronized the live planning/docs trackers.

## Inputs

- `PLAN.md`
- `PROGRESS.md`
- `TODO-FEATURES.md`
- `docs/LIVING_DOCS.md`
- `docs/ARCHITECTURE.md`
- `docs/session-summaries/SESSION_114_SUMMARY.md`
- `pyproject.toml`
- `AGENTS.md`
- `src/new_repo_template/snapshot_assets/templates/python_lane_pyproject.toml`
- `src/new_repo_template/snapshot_assets/templates/python_lib/python_lib_pyproject.toml`
- `src/new_repo_template/snapshot_assets/templates/root_python_workspace_pyproject.toml`
- `src/new_repo_template/snapshot_assets/templates/root_pyproject_base.toml`
- `src/new_repo_template/snapshot_assets/templates/foundation/AGENTS.md`
- `src/new_repo_template/snapshot_assets/templates/foundation/.agent/rules/general-rules.md`
- `src/new_repo_template/scaffold.py`
- `src/new_repo_template/add_mode.py`
- `src/new_repo_template/foundation_manifest.py`
- `src/new_repo_template/snapshot_assets/source_manifest.json`
- `tests/contracts/test_python_lane_contract.py`
- `tests/contracts/test_python_lib_scaffold_contract.py`
- `tests/contracts/test_version_baseline_contract.py`

## YELLOW Pass

- Re-ran the full feature `6.0` restart-read sequence across the active plan/docs, the live/root packaging files, the generated Python templates, the add/scaffold paths, the guidance files, and the relevant contract suites before editing any files.
- Ran `btca status` to confirm the active project resource set and provider/model state.
- Used plain/simple `btca ask -r uv` queries to reconfirm the bounded `uv_build` version-range guidance, the coordinator-only workspace-root rule (`[tool.uv] package = false` and no `[build-system]`), the required `tool.uv.build-backend` settings for a `src`-layout package whose distribution name differs from its import module, and the `source-include` guidance needed to keep `tests/**` in the root sdist.
- During BLUE closeout, did a focused follow-up YELLOW reread of `src/new_repo_template/foundation_manifest.py` and `src/new_repo_template/snapshot_assets/source_manifest.json` after `template-assets validate` exposed a manifest/sync-allowlist mismatch.

## RED

- Expanded `tests/contracts/test_python_lane_contract.py` so generated Python app outputs now assert `uv_build` metadata, coordinator-only root workspace metadata, generated-package `uv build --package python-app` success, and the live repo root-package `uv build` path plus explicit root `tool.uv.build-backend` settings.
- Expanded `tests/contracts/test_python_lib_scaffold_contract.py` so generated Python library outputs now assert `uv_build` metadata, coordinator-only root workspace metadata, and generated-package `uv build --package python-lib` success.
- Replaced Hatchling-based `pyproject.toml` fixtures in `tests/contracts/test_version_baseline_contract.py` with feature-6-aligned `uv_build` fixtures.
- Confirmed RED by running `uv run pytest tests/contracts/test_python_lane_contract.py tests/contracts/test_python_lib_scaffold_contract.py tests/contracts/test_version_baseline_contract.py`, which failed on the expected pre-migration assertions.

## GREEN

- Migrated the live root `pyproject.toml` from Hatchling to `uv_build` with `requires = ["uv_build>=0.10.12,<0.11.0"]`, `module-name = "new_repo_template"`, `module-root = "src"`, and `source-include = ["tests/**"]`.
- Migrated `src/new_repo_template/snapshot_assets/templates/python_lane_pyproject.toml` and `src/new_repo_template/snapshot_assets/templates/python_lib/python_lib_pyproject.toml` to `uv_build` and removed the stale Hatch-specific wheel-target block from the library template.
- Updated `src/new_repo_template/snapshot_assets/templates/root_python_workspace_pyproject.toml` to keep the generated root Python workspace coordinator-only with `[tool.uv] package = false`, and aligned `src/new_repo_template/snapshot_assets/templates/root_pyproject_base.toml` to the same non-package coordinator posture.
- Updated the generated/live Python guidance in `AGENTS.md`, `src/new_repo_template/snapshot_assets/templates/foundation/AGENTS.md`, and `src/new_repo_template/snapshot_assets/templates/foundation/.agent/rules/general-rules.md` so they now describe `uv_build` plus the coordinator-root rule instead of Hatchling.

## BLUE

- Refreshed bundled snapshot metadata with `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."`.
- Validated the live root package with `uv build --out-dir <temp-dir>` and validated generated Python package outputs with `uv build --project <generated-root> --package python-app` and `uv build --project <generated-root> --package python-lib`.
- The first full-suite run exposed an unrelated but real manifest-driven sync-allowlist mismatch: several scaffold-only foundation assets in `src/new_repo_template/snapshot_assets/source_manifest.json` were still marked `sync: true` even though `src/new_repo_template/foundation_manifest.py` intentionally rejects them from the approved sync surface.
- Corrected those entries so the plan-template, task-template, and plan-helper OpenCode assets remain scaffold-only, re-ran `template-assets validate`, revalidated the sync-related contract slices, and then re-ran the full repository suite successfully.

## Validation

- `uv run pytest tests/contracts/test_python_lane_contract.py tests/contracts/test_python_lib_scaffold_contract.py tests/contracts/test_version_baseline_contract.py` -> 15 passed
- `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."` -> passed
- `uv build --out-dir <temp-dir>` -> passed
- `uv run python -m new_repo_template.scaffold --target python --target python-lib --no-interactive --output <temp-dir/generated>` -> passed
- `uv build --project <temp-dir/generated> --package python-app --out-dir <temp-dir/generated/dist/python-app>` -> passed
- `uv build --project <temp-dir/generated> --package python-lib --out-dir <temp-dir/generated/dist/python-lib>` -> passed
- `uv run ruff check src/new_repo_template tests/contracts` -> passed
- `uv run pytest` -> 215 passed

## Documentation Sync

- Updated `PLAN.md` to mark the feature `6.0` implementation record complete and point at this session summary.
- Updated `PROGRESS.md` to record the completed RED/GREEN/BLUE work and move the next-up pointer to feature `7.0` discussion/planning.
- Updated `docs/LIVING_DOCS.md` and `docs/ARCHITECTURE.md` to describe feature `6.0` as implemented rather than merely planned, including the explicit root `tool.uv.build-backend` settings and the coordinator-only root workspace rule.
- Updated `TODO-FEATURES.md` to mark feature `6.0` complete and remove the now-stale dependency notes that said features `7.0` and `10.0` were still blocked by feature `6.0`.

## Outcome

- Feature `6.0` is fully implemented, the root and generated Python package paths now standardize on `uv_build`, the template-sync surface remains intentionally narrow after the source-manifest correction, and the repository is green again at `uv run pytest` with 215 passing tests.
