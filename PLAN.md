# Multiple Same-Type Projects Plan

**Last Updated:** 2026-03-13 07:51:41 PM
**Status:** Complete
**Previous Cycle Archive:** `docs/archive/plans/PLAN_2026-03-13_07-05-11_PM.md`
**Previous Cycle Summary:** `docs/session-summaries/SESSION_105_SUMMARY.md`

---

## Goal

Update `nurt new` and the scaffold engine so a generated monorepo can contain multiple named projects of the same type, with a full migration from singleton target paths to named instance directories.

---

## YELLOW

- [x] Read the repo files, tests, and documentation relevant to `3.0`, including `TODO-FEATURES.md`, `src/new_repo_template/{scaffold.py,nurt_cli.py,interactive_ui.py,interactive_tui.py,version_baseline.py}`, and the current contract suites around target validation, root workspaces, `nurt new`, and the Textual wizard.
- [x] Run `btca status`, `btca resources`, and `btca ask` for dependency guidance affecting the next slice.
- [x] Confirm the migration direction: fully normalize all app/library lanes to named instance directories now instead of carrying dual singleton-vs-multi-instance behavior.
- [x] Confirm workspace implications from YELLOW research:
  - Bun/Turborepo can support mixed top-level support packages plus nested named project workspaces.
  - uv workspace members should move from direct members to `apps/python/*` and `packages/python/*` when Python projects become named instances.
- [x] Lock the planning decisions for build work:
  - New primary creation syntax will be project-instance based rather than target-kind based.
  - Generated app/library paths become `apps/<type>/<name>` and `packages/<language>/<name>`.
  - Existing shared support packages remain at `packages/typescript-config`, `packages/eslint-config`, and `packages/shared`.
  - Backend auth becomes per backend instance rather than one global repo-wide toggle.

### Planned Model

- [x] Repository path normalization:
  - `apps/python/<name>`
  - `apps/web/<name>`
  - `apps/backend/<name>`
  - `apps/desktop/<name>`
  - `apps/mobile/<name>`
  - `apps/tv/<name>`
  - `apps/typescript-cli/<name>`
  - `packages/python/<name>`
  - `packages/typescript/<name>`
- [x] CLI model:
  - primary non-interactive syntax: repeatable `--project <type>:<name>`
  - legacy `--target` remains only as a temporary compatibility shim for one default-named instance during migration
- [x] Wizard model:
  - choose project types/counts
  - collect normalized names for each instance
  - resolve backend auth per backend instance
  - resolve any required web-to-backend bindings before review
- [x] Internal scaffold model:
  - replace target-only planning with typed project-instance specs
  - generate paths, package names, workspace members, and dependency wiring from project-instance metadata instead of singleton constants

## RED

- [x] Add new contract coverage for project-instance parsing and validation in `scaffold.py` and `nurt_cli.py`.
- [x] Add dry-run and write contracts for repeated same-type projects, for example:
  - [x] two Python apps
  - [x] two web apps
  - [x] two TypeScript libraries
  - [x] Python app + Python library with distinct names
- [x] Add validation contracts for invalid `--project` syntax, duplicate names within the same parent path, reserved/internal package collisions, and illegal mixes like `foundation` plus named projects.
- [x] Add contracts for backend auth becoming per-instance and for web apps that must bind to an explicit backend when multiple backend instances exist.
- [x] Update root workspace contracts to expect nested workspace globs in root `package.json` and named-member globs in root `pyproject.toml`.
- [x] Update Python lockfile/workspace contracts so root uv workspace behavior still holds under named app/library directories.
- [x] Replace or expand current singleton path assumptions in:
  - `tests/contracts/test_required_preset_matrix_contract.py`
  - `tests/contracts/test_python_lane_contract.py`
  - `tests/contracts/test_python_lib_scaffold_contract.py`
  - `tests/contracts/test_typescript_cli_scaffold_contract.py`
  - `tests/contracts/test_typescript_lib_scaffold_contract.py`
  - `tests/contracts/test_nurt_cli_contract.py`
  - `tests/contracts/test_interactive_tui_contract.py`
- [x] Add explicit contract coverage for compatibility behavior if `--target` remains supported during the transition.

## GREEN

- [x] Introduce a typed project-instance model in `src/new_repo_template/scaffold.py`, likely replacing `ScaffoldPlan.targets` with project specs that carry type, name, optional auth, and optional bindings.
- [x] Add CLI parsing in `src/new_repo_template/nurt_cli.py` for repeatable `--project <type>:<name>` inputs and route that model into scaffold resolution.
- [x] Implement a compatibility layer for `--target` that maps each target to one default-named project instance during the migration window.
- [x] Refactor path generation in `src/new_repo_template/scaffold.py` so all app/library output is generated under named instance directories instead of singleton fixed paths.
- [x] Update root workspace templates and generation logic:
  - [x] root `package.json` workspaces should include top-level support packages plus nested project paths
  - [x] root uv workspace members should target `apps/python/*` and `packages/python/*`
- [x] Update each scaffold lane to derive package names, commands, README copy, env paths, and test locations from the resolved project instance name.
- [x] Update backend/web auth wiring so auth config is generated per backend instance and any web app binding targets the correct backend instance.
- [x] Update `src/new_repo_template/interactive_ui.py` to collect project instances, names, backend auth, and any required bindings.
- [x] Update `src/new_repo_template/interactive_tui.py` from target multi-select into a project-instance workflow while preserving keyboard-first navigation, review flow, and compact layout behavior.
- [x] Keep post-create behavior stable so lockfile generation, BMAD installation, and core-tools sync still run correctly after a multi-instance scaffold.

## BLUE

- [x] Refactor duplicated per-target path/package logic into reusable builders for app instances, Python package instances, and TypeScript package instances.
- [x] Harden validation for:
  - [x] duplicate sibling names
  - [x] collisions with internal support packages
  - [x] invalid backend bindings
  - [x] default-name compatibility behavior
  - [x] deterministic dry-run plan ordering
- [x] Reconcile all remaining singleton-path assumptions in docs, templates, tests, and runtime helpers.
- [x] Rerun targeted contracts for scaffold planning, `nurt new`, interactive UI/TUI, workspaces, and runtime smokes.
- [x] Rerun `uv run ruff check src/new_repo_template tests/contracts`.
- [x] Rerun full `uv run pytest`.

## Documentation Sync

- [x] Update `PROGRESS.md`.
- [x] Update `docs/LIVING_DOCS.md`.
- [x] Update `docs/ARCHITECTURE.md`.
- [x] Update `TODO-FEATURES.md` when `3.0` is complete.
- [x] Create a new session summary in `docs/session-summaries/`.
