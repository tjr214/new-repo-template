# New Repo Template - Development Progress

**Last Updated:** 2026-03-01 02:34:22 PM
**Current Phase:** M1 GREEN slice (`nurt` command bootstrap + startup update-check)

---

## Completed

- [x] Confirmed strategic direction for always-on monorepo template.
- [x] Finalized core stack decisions (Turbo + Bun, cloud-first Convex, Electron Forge, Expo TV path).
- [x] Defined CI direction (GitHub Actions with required native Windows checks).
- [x] Created comprehensive execution plan at `PLAN.md`.
- [x] Incorporated plan guardrails: upfront version policy, preset matrix, CLI behavior contract, secret-free Convex CI strategy, Python lane contract, security baseline, BTCA governance logging.
- [x] Added generator failure atomicity guardrail (transactional writes or cleanup-on-failure with explicit tests).
- [x] Updated plan to make AndroidTV a dedicated app target with remote-primary + keyboard/mouse/gamepad support contract.
- [x] Clarified preset matrix auth dimension so all `web` + `backend` mixed presets explicitly include auth variants.
- [x] Added global root `pyproject.toml` invariant for all generated repos, including non-Python selections.
- [x] Added approved project BTCA resources (`turborepo`, `bun`, `tanstack-router-start`, `convex-docs`, `convex-better-auth`, `clerk-docs`, `expo-docs`, `react-native-tvos`, `expo-tv-config`, `better-auth-core`).
- [x] Synced `docs/BTCA_RESOURCES.md` with project-level BTCA resource configuration.
- [x] Ran milestone YELLOW lookups via BTCA for Turbo/Bun, TanStack Start, Convex cloud-first, Convex+Clerk, Convex+Better Auth, Expo/TV, and Electron Forge guidance.
- [x] Established generator contract test scaffolding under `tests/`.
- [x] Added and executed first RED contract test for monorepo foundation dry-run behavior.
- [x] Implemented initial scaffold CLI module at `src/new_repo_template/scaffold.py` with required `--target`, `--output`, `--no-interactive`, and `--dry-run` flags.
- [x] Added initial foundation scaffold resolution contract output (`apps/`, `packages/`, `pyproject.toml`) and dry-run no-write behavior.
- [x] Turned first RED contract test GREEN (`uv run pytest tests/contracts/test_monorepo_foundation_contract.py`).
- [x] Updated `PLAN.md` to explicitly lock Python pyproject boundary behavior (root tooling `pyproject.toml` + lane-local Python `pyproject.toml`).
- [x] Added RED contract tests for Python lane dry-run and write behavior at `tests/contracts/test_python_lane_contract.py`.
- [x] Expanded scaffold CLI to support `--target python` with lane-local scaffold output under `apps/python`.
- [x] Implemented root/lane pyproject separation for Python target, including root `[tool.uv.workspace]` member wiring.
- [x] Verified GREEN for foundation + Python contracts (`uv run pytest`).
- [x] Ran YELLOW context lookups for argparse validation style and uv command baseline recommendations.
- [x] Added RED tests for CLI validation + Python command documentation at `tests/contracts/test_cli_validation_and_python_commands_contract.py`.
- [x] Implemented deterministic `--auth` validation error path for unsupported target combinations.
- [x] Added Python lane command documentation scaffold (`apps/python/README.md`) with baseline uv commands.
- [x] Added non-interactive failure-path coverage for omitted `--no-interactive`.
- [x] Verified full suite GREEN after this slice (`uv run pytest`: 6 passed).
- [x] Ran YELLOW context lookup on atomic staging/rename patterns via CPython docs.
- [x] Added RED failure-atomicity contract at `tests/contracts/test_failure_atomicity_contract.py`.
- [x] Implemented transactional scaffold write strategy (temp staging directory + atomic move into final output path).
- [x] Added simulated mid-generation failure hook for contract testing and ensured cleanup of staged output.
- [x] Verified full suite GREEN after atomicity implementation (`uv run pytest`: 7 passed).
- [x] Added RED target-matrix/auth contract tests in `tests/contracts/test_target_matrix_and_auth_contract.py`.
- [x] Ran YELLOW BTCA lookup to confirm `argparse` repeat-option pattern (`action='append'` + post-parse validation).
- [x] Expanded target model to include `web`, `backend`, `desktop`, `mobile`, and `tv` in addition to `foundation` and `python`.
- [x] Enforced explicit auth requirement for `web` + `backend` selections in non-interactive mode.
- [x] Enforced standalone-only `foundation` target validation.
- [x] Added contract coverage for mobile+tv separate app scaffolding and root `pyproject.toml` invariant on JS-only/TV-only outputs.
- [x] Verified full suite GREEN after target/auth expansion (`uv run pytest`: 13 passed).
- [x] Ran YELLOW BTCA lookups for Convex+Clerk and Convex+Better Auth env placeholder conventions.
- [x] Added deeper RED tests for duplicate target validation and auth-variant env placeholders in `tests/contracts/test_target_matrix_and_auth_contract.py`.
- [x] Implemented deterministic duplicate-target validation error handling.
- [x] Updated auth-variant `.env.example` generation to include Vite/Convex/Clerk/Better Auth placeholder keys expected by contract tests.
- [x] Verified full suite GREEN after auth-variant contract expansion (`uv run pytest`: 16 passed).
- [x] Added RED auth-wiring placeholder contract tests for Clerk and Better Auth variants in `tests/contracts/test_target_matrix_and_auth_contract.py`.
- [x] Implemented auth-wiring placeholder scaffold outputs:
  - [x] `apps/backend/convex/auth.config.ts`
  - [x] `apps/web/src/auth-provider.ts` for Clerk
  - [x] `apps/web/src/auth-client.ts` for Better Auth
- [x] Verified full suite GREEN after auth-wiring slice (`uv run pytest`: 18 passed).
- [x] Ran YELLOW BTCA lookups for env placeholder and secret-handling conventions (Convex + Clerk docs).
- [x] Added RED security baseline contracts in `tests/contracts/test_security_baseline_contract.py`.
- [x] Implemented root `.gitignore` security baseline handling in scaffold output.
- [x] Implemented target-local `.env.example` generation for selected targets with placeholder values.
- [x] Added security baseline documentation at `docs/SECURITY_BASELINE.md`.
- [x] Verified full suite GREEN after security baseline slice (`uv run pytest`: 20 passed).
- [x] Corrected `.gitignore` strategy: scaffold now copies the repository root `.gitignore` baseline instead of synthesizing a new file.
- [x] Expanded repository root `.gitignore` baseline with `.env.*`, `!.env.example`, `*.pem`, and `*.key` guards.
- [x] Added `--dry-run` support to `.template_scripts/update-opencode.sh` with a non-destructive status table path.
- [x] Added turborepo tool management to `.template_scripts/update-opencode.sh` (`bun add -g turbo`).
- [x] Added `--dry-run` support to `install.sh` with explicit non-destructive plan output.
- [x] Added contract tests for installer/updater dry-run behaviors in `tests/contracts/test_installer_scripts_dry_run_contract.py`.
- [x] Verified full suite GREEN after script dry-run + turborepo slice (`uv run pytest`: 22 passed).
- [x] Wired `install.sh` to invoke the scaffold engine (`src/new_repo_template/scaffold.py`) for both dry-run planning and non-dry apply flows.
- [x] Added installer dry-run contract coverage for forwarding target/auth options into scaffold planning output.
- [x] Updated `PLAN.md` with explicit clone -> `install.sh` orchestration contract semantics.
- [x] Verified full suite GREEN after installer orchestration alignment (`uv run pytest`: 23 passed).
- [x] Locked strategic pivot to all-in global `nurt` tool distribution (no `install.sh` fallback path for user flow).
- [x] Updated `PLAN.md` with `nurt` command model (`new`, `update`, `tools sync`, `template-assets sync`) and startup update-check requirements.
- [x] Added snapshot asset packaging contract details to `PLAN.md` (manifest, metadata, bundled runtime assets, deterministic behavior).
- [x] Added `nurt` CLI implementation module at `src/new_repo_template/nurt_cli.py`.
- [x] Implemented `nurt` command routing for `new`, `update`, `tools sync`, and `template-assets sync`.
- [x] Implemented mandatory startup update-check hook on every `nurt` invocation (with deterministic simulated notice path for contract tests).
- [x] Added `nurt` contract tests in `tests/contracts/test_nurt_cli_contract.py` (new dry-run parity, update dry-run, startup update notice, tools sync dry-run, template-assets sync dry-run).
- [x] Added `nurt` console entrypoint in `pyproject.toml`.
- [x] Verified full suite GREEN after `nurt` bootstrap slice (`uv run pytest`: 29 passed).

## In Progress

- [ ] M0 setup execution hardening:
  - [ ] Resolve intermittent `bun` BTCA resource load failures (`git clone/fetch failed`) and record stable workaround or remediation.
- [ ] Define and codify version baseline metadata and update workflow.

- [ ] M1 foundation implementation:
  - [x] Expand scaffold CLI from foundation+python to full target selection contract.
  - [x] Extend deterministic validation errors to full target matrix (web/backend/auth combinations, contradictory selections).
  - [x] Implement transactional/failure-atomic scaffold write path.
  - [ ] Add broader non-interactive validation path coverage for missing/invalid required arguments across all target modes.
  - [x] Add auth-variant env placeholder scaffolding + minimal wiring placeholder files for `web+backend`.
  - [x] Add non-destructive `--dry-run` support for installer and tool updater scripts.

- [ ] Nurt migration implementation:
  - [x] Introduce `nurt` CLI entrypoint and command router.
  - [ ] Migrate installer/update orchestration into `nurt` subcommands beyond script-wrapper behavior.
  - [x] Implement mandatory startup update-check and `nurt update` flow.
  - [ ] Implement snapshot asset generation + packaged asset loading path.

## Next Up

- [ ] Expand RED tests for remaining unsupported mixed-combo cases and future interactive fallback semantics.
- [ ] Add stronger auth-variant output contracts for concrete framework wiring once TanStack Start + Convex file layouts are introduced.
- [ ] Define version baseline metadata and maintainer update/check workflow.
- [ ] Add lightweight secret scanning in CI (advisory first).
- [ ] Continue M1 implementation in YELLOW-RED-GREEN-BLUE slices.

## BTCA Governance Log

- [x] 2026-03-01: User-approved resource set (items 1-10 in `PLAN.md`) added via `btca add`.
- [x] 2026-03-01: Revalidated with `btca resources` and `btca status`.
- [x] 2026-03-01: `convex-docs` resource corrected to `https://github.com/get-convex/convex-docs` after invalid search path error.
- [x] 2026-03-01: `btca clear` executed after BTCA runtime suggested cache reset for resource clone/fetch failures.
