# Living Docs

## Current State

The template is in planning-to-implementation transition for a major expansion:
- Always-on monorepo support
- Fullstack web support
- Desktop support
- Mobile and AndroidTV support

The canonical execution checklist is in `PLAN.md`.

M0 execution has started. BTCA project resources are now configured, and the first scaffold contract has progressed from RED to GREEN with an initial implementation slice.

## Active Implementation Rules

- Follow YELLOW-RED-GREEN-BLUE for each implementation slice.
- Use BTCA resource-backed lookups during YELLOW before coding.
- Keep this file, `docs/ARCHITECTURE.md`, and `PROGRESS.md` synchronized during implementation.
- Keep `docs/BTCA_RESOURCES.md` fully synchronized with project-level BTCA resources after every add/remove/change.

## Decisions Snapshot

- Monorepo always-on: yes
- Turbo + Bun: yes
- Convex: cloud-first default
- Auth mode: explicit choice required (`clerk` or `better-auth`)
- Auth rule scope: any preset containing both `web` and `backend` must explicitly choose auth
- Desktop frontend: dedicated Electron app (Forge)
- Mobile: dedicated Expo mobile app (`apps/mobile`)
- TV: dedicated Expo AndroidTV app (`apps/tv`), separate from mobile
- CI: GitHub Actions with required native Windows checks
- Signing: deferred to hardening; unsigned internal builds allowed in early phases
- Versioning: template tracks latest known-good versions, generated repos lock deterministic install state via lockfiles
- Convex CI baseline: credentialless wiring checks only (no external secrets required)
- Generator writes: failure-atomic (transactional write strategy or cleanup-on-failure)
- TV input contract: remote primary; keyboard/mouse/gamepad supported when connected
- Root `pyproject.toml` invariant: always present, even when Python target is not selected
- Python lane metadata boundary: Python target scaffolds `apps/python/pyproject.toml`; root `pyproject.toml` remains monorepo/tooling-level

## Known Constraints

- BTCA project resources are configured and synchronized; subsequent resource changes require immediate docs sync.
- Native Windows validation must not be replaced by WSL-only checks.
- AndroidTV support includes emulator automation plus manual Shield checklist.
- AndroidTV app is always a separate scaffold target, not a mobile profile toggle.
- Fullstack auth choice has no default and must be explicitly selected in non-interactive runs.
- Mixed presets with `web` + `backend` are auth-parameterized only (no auth-agnostic mixed variant).
- Generator failures must not leave partially scaffolded repos behind.
- Root `pyproject.toml` is required for template tooling flows (including RALPH loader compatibility).

## Implementation Notes (M0-M1)

- BTCA resources added: `turborepo`, `bun`, `tanstack-router-start`, `convex-docs`, `convex-better-auth`, `clerk-docs`, `expo-docs`, `react-native-tvos`, `expo-tv-config`, `better-auth-core`.
- YELLOW lookup results collected for Turborepo/Bun task modeling, TanStack Start monorepo defaults, Convex cloud-first workflow, auth integration constraints, Expo/TV configuration, and Electron Forge packaging.
- Initial contract test scaffolding created at `tests/README.md` and `tests/contracts/test_monorepo_foundation_contract.py`.
- First RED result was expected and confirmed: `ModuleNotFoundError: No module named 'new_repo_template'`.
- Initial GREEN implementation added `src/new_repo_template/scaffold.py` and now satisfies the first dry-run foundation contract.
- Python lane GREEN slice complete: `--target python` now scaffolds both root `pyproject.toml` and lane-local `apps/python/pyproject.toml`.
- CLI validation + Python command contract slice complete: `--auth` now fails deterministically when invalid, non-interactive omission has explicit failure coverage, and Python lane scaffolds `apps/python/README.md` with baseline uv commands.
- Failure-atomic scaffold slice complete: generator now stages output in a temp directory and atomically moves it into place; failure-path contract confirms no partial output remains.
- Current blocker/caveat: intermittent BTCA `bun` resource clone/fetch failures; cache reset via `btca clear` helps transiently but needs follow-up hardening guidance.
