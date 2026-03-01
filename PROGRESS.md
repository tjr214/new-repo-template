# New Repo Template - Development Progress

**Last Updated:** 2026-03-01 12:33:07 PM
**Current Phase:** M1 GREEN slice (Python lane pyproject boundary) complete

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

## In Progress

- [ ] M0 setup execution hardening:
  - [ ] Resolve intermittent `bun` BTCA resource load failures (`git clone/fetch failed`) and record stable workaround or remediation.
- [ ] Define and codify version baseline metadata and update workflow.
- [ ] Add security baseline docs (`.env.example` convention + secret handling rules).

- [ ] M1 foundation implementation:
  - [ ] Expand scaffold CLI from foundation+python to full target selection contract.
  - [ ] Add deterministic validation errors for invalid combinations and auth rules.
  - [ ] Implement transactional/failure-atomic scaffold write path.
  - [ ] Add non-interactive validation path coverage for missing/invalid required arguments.

## Next Up

- [ ] Add RED tests for CLI validation behavior (`--no-interactive`, auth-required combinations, invalid combos).
- [ ] Add RED tests for Python baseline commands and generated lane command docs (`uv sync --group dev`, `uv run pytest`, `uv run ruff check .`, `uv run mypy src`).
- [ ] Define version baseline metadata and maintainer update/check workflow.
- [ ] Add security baseline docs for `.env.example`/secret handling and CI secret scan expectations.
- [ ] Continue M1 implementation in YELLOW-RED-GREEN-BLUE slices.

## BTCA Governance Log

- [x] 2026-03-01: User-approved resource set (items 1-10 in `PLAN.md`) added via `btca add`.
- [x] 2026-03-01: Revalidated with `btca resources` and `btca status`.
- [x] 2026-03-01: `convex-docs` resource corrected to `https://github.com/get-convex/convex-docs` after invalid search path error.
- [x] 2026-03-01: `btca clear` executed after BTCA runtime suggested cache reset for resource clone/fetch failures.
