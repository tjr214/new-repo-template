# Architecture

## Scope

This repository is a project template that generates new repositories. The template itself is the system under design.

The target architecture is an always-on monorepo template that can scaffold:
- Web fullstack apps (TanStack Start + Convex)
- Desktop apps (Electron)
- Mobile apps (Expo, dedicated app)
- TV apps (Expo AndroidTV, dedicated app separate from mobile)
- Python-oriented projects (CLI/TUI-first)

## Core Decisions

- Monorepo orchestration: Turborepo (`turbo`)
- JS/TS package manager and workspaces: Bun
- Auth integration mode for Convex fullstack scaffolds: explicit prompt (`clerk` or `better-auth`)
- Auth selection rule: any scaffold selecting both `web` and `backend` must explicitly choose auth
- Desktop packaging tool: Electron Forge
- Convex workflow: cloud-first
- CI platform: GitHub Actions
- Platform support policy: native macOS + Linux + Windows (WSL optional supplemental only)
- Version policy: latest known-good baseline in template, deterministic lockfile state in generated repos
- Scaffold contract: explicit preset-combination matrix and deterministic non-interactive CLI behavior
- Generator write model: failure-atomic scaffolding (transactional writes or cleanup-on-failure)
- TV input contract: remote-primary navigation with keyboard/mouse/gamepad support as secondary inputs
- Root metadata invariant: `pyproject.toml` exists at repository root for all generated repos regardless of selected targets
- Python lane metadata boundary: Python app metadata/deps live in lane-local `apps/python/pyproject.toml`, while root `pyproject.toml` remains monorepo/tooling-level
- Security baseline: root `.gitignore` baseline (copied from template root) includes env/secret guards and selected targets scaffold placeholder-only `.env.example`
- Global UX direction: distribute and run as `nurt` global CLI installed via uv from git; user entrypoint is `nurt new <project-name>`

## Planned Topology

- Root workspace with `apps/*` and `packages/*`
- Shared packages for config and reusable code
- Selectable target generators within an always-on monorepo shell

## Current Implementation Status

- Milestone M1 bootstrap is active (with M0 baseline tasks partially completed).
- Project BTCA resource layer is now configured for the locked dependency set in `PLAN.md`.
- Initial contract-test harness now exists under `tests/` with a first RED test for monorepo foundation dry-run behavior.
- The initial RED test is now GREEN via a bootstrap CLI implementation at `src/new_repo_template/scaffold.py`.
- Python lane RED/GREEN slice is complete with `tests/contracts/test_python_lane_contract.py`, including baseline command execution checks.
- CLI validation + command-doc RED/GREEN slice is complete with `tests/contracts/test_cli_validation_and_python_commands_contract.py`, including expanded non-interactive missing/invalid argument coverage across multiple target modes.
- Failure-atomic RED/GREEN slice is complete with `tests/contracts/test_failure_atomicity_contract.py`.
- Target-matrix RED/GREEN slice is complete with `tests/contracts/test_target_matrix_and_auth_contract.py`.
- Security baseline RED/GREEN slice is complete with `tests/contracts/test_security_baseline_contract.py` and `docs/SECURITY_BASELINE.md`.
- Installer/updater script RED/GREEN slice is complete with `tests/contracts/test_installer_scripts_dry_run_contract.py`.
- Current scaffold implementation supports `foundation`, `python`, `web`, `backend`, `desktop`, `mobile`, and `tv` targets with non-interactive mode, dry-run support, deterministic auth validation for `web+backend`, duplicate-target validation, auth-variant env placeholders, minimal auth wiring placeholders, root `.gitignore` secret guards, and transactional scaffold writes.
- Installer tooling now supports non-destructive script-level dry-runs and includes turborepo (`turbo`) update/install in the updater workflow.
- Installer support remains available for legacy/maintainer operations, but user bootstrap is standardized on global `nurt` command flow.
- Script-first UX has been superseded: primary execution is `uv tool install --from git+... nurt` followed by `nurt new <project-name>` with bundled snapshot assets and explicit `nurt update` lifecycle.
- `nurt` command bootstrap is implemented at `src/new_repo_template/nurt_cli.py` with command routing (`new`, `update`, `tools sync`, `template-assets sync`) and startup update-check hook.
- `nurt new` now includes interactive prompt-based target/auth resolution path.
- Snapshot assets are bundled under `src/new_repo_template/snapshot_assets/` and loaded at runtime via `importlib.resources`.
- Snapshot generation command path is implemented at `nurt template-assets snapshot` using manifest-driven source entries and metadata hashing.
- Script-wrapper migration slice is complete for sync commands: `nurt tools sync` and `nurt template-assets sync` now call native Python operations in `src/new_repo_template/sync_ops.py`.
- Contract coverage now includes non-dry-run sync failure messaging for native `nurt` sync commands (tools sync simulated failure output and template-assets sync validation failures).
- Interactive `nurt new` now handles stdin-closure failure paths with deterministic remediation output instead of raw EOF tracebacks.
- Mixed-combo validation coverage now includes additional unsupported auth/target combinations in mixed presets.
- Required preset-combination matrix coverage is now implemented for all `PLAN.md` Section 2.1 combinations in `tests/contracts/test_required_preset_matrix_contract.py`, including both auth variants and all-target (python-inclusive) sanity passes.
- Root workspace scaffold now emits `package.json` and `turbo.json` at repository root for all outputs, with Bun workspaces (`apps/*`, `packages/*`) and Turbo-routed root scripts (`dev`, `build`, `test`, `lint`, `typecheck`).
- Root workspace contract coverage now verifies dry-run visibility and scaffolded workspace/task wiring in `tests/contracts/test_root_workspace_contract.py`.
- JS app targets now scaffold workspace-local `package.json` manifests (`apps/web`, `apps/backend`, `apps/desktop`, `apps/mobile`, `apps/tv`) with baseline script placeholders for Turbo/Bun wiring.
- Bun workspace install viability coverage is now active in `tests/contracts/test_bun_workspace_install_contract.py` and verifies generated `web+backend` output supports both `bun install` and `bun install --frozen-lockfile`.
- Minimal selected-preset command-smoke coverage is now active in `tests/contracts/test_turbo_command_smoke_contract.py`, validating root script viability for `dev`, `build`, `test`, `lint`, and `typecheck` after install on generated `web+backend` output.
- Fullstack scaffold baseline now includes concrete framework file layout for `web+backend`: TanStack-style web routing/app entry files and Convex-style backend `http.ts`/`schema.ts` baseline files.
- Fullstack auth variant contract coverage is now concrete in `tests/contracts/test_fullstack_auth_wiring_contract.py`, with Clerk and Better Auth assertions on provider-aware backend auth config and frontend auth client/provider stubs.
- Version baseline metadata/workflow is implemented with `version-baseline.json` and native `nurt versions check/update` commands in `src/new_repo_template/version_baseline.py`.
- Version baseline workflow now includes lockfile lifecycle controls: update-time regeneration (with dry-run/summaries) and check-time lockfile presence validation.
- CI workflow wiring now enforces version/lockfile governance using `nurt versions check --check-lockfiles --check-latest`, sets up Bun on matrix runners, and runs cross-platform script smoke contracts on native Linux/macOS/Windows.
- Interactive prompt rendering now includes Rich/Textual-aware UI infrastructure in `src/new_repo_template/interactive_ui.py` with deterministic plain fallback behavior.

## Validation Model

Implementation follows a strict YELLOW-RED-GREEN-BLUE loop:
- YELLOW: read/lookup first (including BTCA resource-backed asks)
- RED: failing contract tests for scaffold output
- GREEN: minimal implementation to pass tests
- BLUE: refactor and harden

DoD is enforced by contract tests under `tests/` plus CI matrix checks across Linux/macOS/Windows.

Baseline CI is credentialless for cloud-first Convex wiring checks; credential-dependent deployment tests are optional and separately gated.

Current contract coverage:

- `tests/contracts/test_monorepo_foundation_contract.py`
  - Contract intent: non-interactive `--dry-run` foundation scaffold path succeeds, reports monorepo shape (`apps`, `packages`, `pyproject.toml`), and writes no files.
- `tests/contracts/test_python_lane_contract.py`
  - Contract intent: Python target dry-run/write flows preserve root/lane pyproject separation (`pyproject.toml` and `apps/python/pyproject.toml`) and baseline lane commands execute (`uv sync --group dev`, `uv run pytest`, `uv run ruff check .`, `uv run mypy src`).
- `tests/contracts/test_cli_validation_and_python_commands_contract.py`
  - Contract intent: deterministic CLI validation failures (including missing `--no-interactive` across foundation/python/web+backend/mobile+tv modes, missing required args, and invalid choice handling) and Python lane baseline command documentation generation.
- `tests/contracts/test_failure_atomicity_contract.py`
  - Contract intent: simulated mid-generation failure leaves no partial output at the final scaffold path.
- `tests/contracts/test_target_matrix_and_auth_contract.py`
  - Contract intent: multi-target validation/auth rules, duplicate target rejection, unsupported mixed-combo auth validation, auth-variant env placeholders, minimal auth wiring placeholders, and separate mobile/TV app scaffolding behavior.
- `tests/contracts/test_required_preset_matrix_contract.py`
  - Contract intent: full required preset matrix from `PLAN.md` Section 2.1 scaffolds successfully with root `pyproject.toml` invariant, expected target directories, python-lane pyproject inclusion when selected, and auth-variant wiring assertions.
- `tests/contracts/test_root_workspace_contract.py`
  - Contract intent: root workspace config files (`package.json`, `turbo.json`) are present in dry-run/scaffold output and include baseline cross-platform script/task wiring for `dev`, `build`, `test`, `lint`, and `typecheck`.
- `tests/contracts/test_bun_workspace_install_contract.py`
  - Contract intent: JS workspace manifests are scaffolded for `web+backend` outputs and generated workspace installs remain viable via `bun install` and `bun install --frozen-lockfile`.
- `tests/contracts/test_turbo_command_smoke_contract.py`
  - Contract intent: selected minimal JS preset passes root Turbo-routed command scripts (`dev`, `build`, `test`, `lint`, `typecheck`) after Bun install.
- `tests/contracts/test_fullstack_auth_wiring_contract.py`
  - Contract intent: `web+backend` scaffold outputs include concrete TanStack/Convex baseline files and auth-variant-specific wiring for both Clerk and Better Auth, with dry-run path visibility.
- `tests/contracts/test_security_baseline_contract.py`
  - Contract intent: root `.gitignore` secret/env protections and per-target `.env.example` placeholder generation.
- `tests/contracts/test_installer_scripts_dry_run_contract.py`
  - Contract intent: non-destructive `--dry-run` behavior for installer/updater scripts and turborepo updater visibility.
- `tests/contracts/test_nurt_cli_contract.py`
  - Contract intent: `nurt` command routing, new-project dry-run parity, startup update notice behavior, dry-run safety for `update`/`tools sync`/`template-assets sync`, deterministic non-dry-run failure messaging for native sync paths, and deterministic interactive stdin-failure remediation.
- `tests/contracts/test_snapshot_assets_contract.py`
  - Contract intent: packaged snapshot template availability and deterministic snapshot metadata generation.
- `tests/contracts/test_version_baseline_contract.py`
  - Contract intent: codified version baseline metadata validation and maintainer update/check workflow behavior (including stale detection, lockfile regeneration/check guardrails, and dry-run non-destructive updates).
- `tests/contracts/test_ci_versions_guardrail_contract.py`
  - Contract intent: CI workflow includes required version guardrail command plus cross-platform matrix smoke-check wiring (Bun setup and targeted command-smoke contract execution).
