# New Repo Template - Development Progress

**Last Updated:** 2026-03-01 01:17:45 PM
**Current Phase:** M1 GREEN/BLUE slice (auth variant env contracts + duplicate-target validation) complete

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

## In Progress

- [ ] M0 setup execution hardening:
  - [ ] Resolve intermittent `bun` BTCA resource load failures (`git clone/fetch failed`) and record stable workaround or remediation.
- [ ] Define and codify version baseline metadata and update workflow.
- [ ] Add security baseline docs (`.env.example` convention + secret handling rules).

- [ ] M1 foundation implementation:
  - [x] Expand scaffold CLI from foundation+python to full target selection contract.
  - [x] Extend deterministic validation errors to full target matrix (web/backend/auth combinations, contradictory selections).
  - [x] Implement transactional/failure-atomic scaffold write path.
  - [ ] Add broader non-interactive validation path coverage for missing/invalid required arguments across all target modes.

## Next Up

- [ ] Expand RED tests for remaining unsupported mixed-combo cases and future interactive fallback semantics.
- [ ] Add deeper auth-variant output contract tests beyond env files (target-specific config/wiring placeholders).
- [ ] Define version baseline metadata and maintainer update/check workflow.
- [ ] Add security baseline docs for `.env.example`/secret handling and CI secret scan expectations.
- [ ] Continue M1 implementation in YELLOW-RED-GREEN-BLUE slices.

## BTCA Governance Log

- [x] 2026-03-01: User-approved resource set (items 1-10 in `PLAN.md`) added via `btca add`.
- [x] 2026-03-01: Revalidated with `btca resources` and `btca status`.
- [x] 2026-03-01: `convex-docs` resource corrected to `https://github.com/get-convex/convex-docs` after invalid search path error.
- [x] 2026-03-01: `btca clear` executed after BTCA runtime suggested cache reset for resource clone/fetch failures.
