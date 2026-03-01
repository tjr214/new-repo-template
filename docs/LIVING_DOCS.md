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
- Global execution UX pivot: primary user flow is moving to globally installed `nurt` (`nurt new <project-name>`) with no `install.sh` fallback user path

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
- Target matrix slice complete for current scaffold breadth: CLI now accepts `foundation/python/web/backend/desktop/mobile/tv`, enforces auth for `web+backend`, enforces foundation-standalone behavior, and verifies distinct `mobile` + `tv` app output contracts.
- Auth variant env contract slice complete: duplicate target selections now fail deterministically, and `web+backend` auth variants scaffold explicit `.env.example` placeholders for Clerk and Better Auth flows.
- Auth wiring placeholder slice complete: `web+backend` auth variants now scaffold minimal placeholder wiring files for frontend/backend auth integration points (`apps/backend/convex/auth.config.ts`, plus auth-specific web wiring stubs).
- Security baseline slice complete: generated outputs now copy the root `.gitignore` baseline (with env/secret guards) and include target-local `.env.example` placeholders; baseline policy is documented in `docs/SECURITY_BASELINE.md`.
- Installer/tooling script slice complete: `install.sh` and `.template_scripts/update-opencode.sh` now support `--dry-run`, and updater flow now includes turborepo (`turbo`) install/update handling.
- Installer orchestration is now aligned with clone-and-run paradigm: `install.sh` forwards target/auth inputs to scaffold planning/apply flows while preserving existing template governance assets.
- New strategic direction: migrate fully to global `nurt` command model (`new`, `update`, `tools sync`, `template-assets sync`) with startup update-check on every invocation and bundled snapshot assets as runtime default.
- `nurt` bootstrap implementation is now in place with command routing and startup update-check hook.
- `nurt new` now supports interactive target/auth prompt flow when flags are omitted.
- Snapshot asset pipeline is now active: scaffold content is loaded from bundled package templates, and `nurt template-assets snapshot` can regenerate packaged assets + metadata.
- `nurt tools sync` and `nurt template-assets sync` now execute native Python operations (no script wrapper dependency in CLI command handlers).
- `nurt` sync contracts now include non-dry-run failure-path assertions for clear operator feedback (project-root/dirty-git validation for template sync and deterministic failure reporting for tools sync).
- `nurt new` interactive flow now handles closed stdin (EOF) with deterministic remediation messaging instead of tracebacks.
- Version baseline workflow is now codified: `version-baseline.json` tracks managed toolchain versions and `nurt versions check/update` provides maintainer validation/update flows (including latest-version comparison and dry-run planning).
- Version baseline workflow now includes lockfile governance: `nurt versions update` regenerates lockfiles by default and `nurt versions check --check-lockfiles` enforces required lockfile presence.
- CI guardrail wiring is now active in `.github/workflows/ci.yml`, including required native OS test matrix and `nurt versions check --check-lockfiles --check-latest` enforcement.
- Interactive UI layer is now Rich/Textual-aware: `nurt new` renders enhanced target/auth menus when Rich is available and falls back deterministically to plain prompts when unavailable.
- Mixed preset validation contracts now include additional unsupported auth/target mixed-combo checks.
- Non-interactive scaffold validation coverage has been expanded across target modes: omitted `--no-interactive` is now contract-tested for foundation/python/web+backend/mobile+tv, and parser-level missing/invalid argument failures (`--target`, `--output`, invalid `--target`/`--auth`) are now explicitly covered.
- Required preset matrix coverage from `PLAN.md` Section 2.1 is now implemented in `tests/contracts/test_required_preset_matrix_contract.py`, including all-target (python-inclusive) sanity passes for both auth variants.
- BTCA `bun` clone/fetch hardening follow-up has been explicitly deprioritized for now so implementation can continue on core PLAN milestones.
- Root workspace bootstrap slice is now in place: scaffold outputs include root `package.json` (Bun workspaces + Turbo-routed `dev/build/test/lint/typecheck` scripts) and root `turbo.json` (minimal task graph for those commands), with contract coverage in `tests/contracts/test_root_workspace_contract.py`.
