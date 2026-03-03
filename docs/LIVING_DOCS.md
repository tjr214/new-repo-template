# Living Docs

## Current State

The template is in planning-to-implementation transition for a major expansion:
- Always-on monorepo support
- Fullstack web support
- Desktop support
- Mobile and AndroidTV support

The canonical execution checklist is in `PLAN.md`.

M0-M3 execution is complete. M4 automatable slices are complete with manual Emulator/Shield hardware validation deferred as carryover gates, and M5 is now in closeout with CI matrix/cache hardening, branch-protection guidance, dedicated preset-regression coverage, dependency versioning policy, optional signing/release checklist design, CI env-template asset reliability fixes, and Windows installer-script contract shell hardening in place.

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
- Installer/tooling script slice complete: `install.sh` and `.template_scripts/update-opencode.sh` support `--dry-run`, and updater flow includes turborepo (`turbo`) install/update handling for maintainer/legacy flows.
- User-facing bootstrap path is now fully `nurt`-first (`uv tool install --from git+... nurt` then `nurt new <project-name>`); script-first bootstrap is not the default user guidance.
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
- JS-target app manifests are now scaffolded (`apps/{web,backend,desktop,mobile,tv}/package.json`), and Bun workspace install viability is contract-tested in `tests/contracts/test_bun_workspace_install_contract.py` (including `bun install` and `bun install --frozen-lockfile` on generated `web+backend` output).
- Minimal preset command-smoke coverage is now active in `tests/contracts/test_turbo_command_smoke_contract.py`: generated `web+backend` scaffold runs `bun install --frozen-lockfile` and passes root `bun run dev/build/test/lint/typecheck` scripts end-to-end.
- Python lane execution contract coverage now includes baseline command viability in `tests/contracts/test_python_lane_contract.py` (`uv sync --group dev`, `uv run pytest`, `uv run ruff check .`, `uv run mypy src`).
- Python lane scaffold dependency metadata now uses uv dependency groups (`[dependency-groups].dev`) so documented baseline commands execute without manual pyproject edits.
- CI matrix now performs explicit cross-platform script smoke checks: Bun setup on each runner plus execution of Bun workspace install, Turbo root-script smoke, and Python baseline command contracts.
- User-facing bootstrap guidance in `README.md` now explicitly documents global `nurt` flow and labels `install.sh` as legacy/maintainer-only path.
- Fullstack auth-variant contract coverage is now concrete: `tests/contracts/test_fullstack_auth_wiring_contract.py` validates TanStack-style web files and Convex-style backend files for both Clerk and Better Auth outputs, plus dry-run path visibility.
- Scaffolded `web+backend` outputs now include concrete framework baseline files (`apps/web/src/main.tsx`, `router.tsx`, route files; `apps/backend/convex/http.ts`, `schema.ts`) instead of auth-only placeholder wiring.
- Convex backend command-smoke coverage is now active in `tests/contracts/test_convex_backend_smoke_contract.py`: generated backend workspaces expose `convex:codegen` and `convex:dev` scripts that run credentialless CLI help commands for CI-safe smoke validation.
- Cross-platform CI smoke contract step now includes Convex backend smoke checks, preserving baseline secret-free validation while increasing fullstack wiring confidence.
- Backend local-dev flow guidance is now scaffolded into generated outputs at `apps/backend/README.md`, covering cloud-first Convex steps, auth decision alignment (`AUTH_PROVIDER`), and separation between credentialed local commands and CI-safe smoke commands.
- Fullstack setup/auth decision documentation is now centralized in `docs/FULLSTACK_SETUP.md` and linked from `README.md`.
- Backend workspace scripts now distinguish credentialed local commands (`convex:dev`, `convex:codegen`) from CI-safe wrappers (`convex:dev:smoke`, `convex:codegen:smoke`), while `dev`/`test` remain smoke-safe for cross-platform CI.
- M0 governance baseline is now fully closed: `PLAN.md` is explicitly marked and maintained as canonical implementation source-of-truth.
- M2 web scaffold now includes a fuller TanStack Start-style baseline beyond route stubs: `app.config.ts`, `vite.config.ts`, `tsconfig.json`, `index.html`, `src/routeTree.gen.ts`, and base styles in `apps/web/src/styles.css`.
- Fullstack shared workspace integration is now active for `web+backend` presets via `packages/shared` (`@generated/shared`), with both web and backend manifests wired through `workspace:*` dependencies and baseline web route consumption.
- Desktop Electron Forge baseline scaffold is now concrete for `desktop` target: generated output includes `apps/desktop/README.md`, `forge.config.ts`, `tsconfig.json`, `index.html`, and `src/{main,preload,renderer}.ts`.
- Desktop workspace package manifest now includes Forge-oriented local commands (`desktop:start`, `desktop:package`, `desktop:make`) and CI-safe smoke wrappers (`desktop:*:smoke`) with root task scripts mapped to non-GUI smoke behavior for deterministic CI compatibility.
- Unsigned desktop artifact guidance is now scaffolded into generated desktop README docs for internal distribution expectations during pre-hardening milestones.
- Desktop runtime smoke coverage is now active in `tests/contracts/test_desktop_runtime_smoke_contract.py`: generated `desktop` scaffold is install-validated with Bun, executes Forge start/package smoke commands, and verifies deterministic unsigned output path wiring (`out/unsigned/*`, `out/unsigned-smoke/*`).
- CI native matrix smoke step now includes desktop runtime smoke contracts in `.github/workflows/ci.yml`, extending Linux/macOS/Windows confidence for desktop script wiring.
- Advisory secret scanning is now enabled in CI via a dedicated non-blocking `secret-scan-advisory` job using `gitleaks/gitleaks-action@v2` (`continue-on-error: true`) to surface potential leaks without gating baseline delivery.
- Desktop runtime smoke coverage now also executes `desktop:make:smoke` in contract tests, completing the dev/build/package baseline gate for M3.
- Shared workspace package reuse now covers web+desktop combinations: scaffolded outputs emit `packages/shared`, desktop package wiring includes `@generated/shared`, and desktop renderer consumes shared utility exports.
- M4 mobile/TV baseline contracts are now active in `tests/contracts/test_mobile_tv_scaffold_contract.py` for mobile-only scaffold shape, tv-only scaffold shape, TV plugin isolation (`@react-native-tvos/config-tv` in `apps/tv/app.json`), and mobile+tv dry-run path visibility.
- Scaffold outputs now include concrete Expo baseline files for both mobile and TV targets (`app.json`, `babel.config.js`, `index.js`, `App.tsx`, `tsconfig.json`) generated from snapshot templates under `src/new_repo_template/snapshot_assets/templates/mobile/` and `src/new_repo_template/snapshot_assets/templates/tv/`.
- Mobile and TV workspace manifests are now Expo-oriented (scripts + dependencies), with TV-specific plugin dependency wiring (`@react-native-tvos/config-tv`) isolated to `apps/tv`.
- TV Android build-profile baseline is now scaffolded for dedicated `apps/tv`: generated output includes `apps/tv/eas.json` with `development`/`preview` APK internal-distribution profiles and package scripts for profile-aware Android EAS builds (`tv:build:development`, `tv:build:preview`), with contract coverage in `tests/contracts/test_tv_android_build_profile_contract.py`.
- TV HID/input baseline is now scaffolded with remote-primary focus wiring and fallback-input checklist artifacts: generated TV app includes `useTVEventHandler` + preferred focus markers in `apps/tv/App.tsx` and a dedicated `apps/tv/TV_INPUT_CHECKLIST.md` covering keyboard/mouse/gamepad validation, with contract coverage in `tests/contracts/test_tv_input_hid_contract.py`.
- Mobile/TV setup docs are now scaffolded directly into generated apps: `apps/mobile/README.md` includes CI-safe validation command guidance and `apps/tv/README.md` includes dedicated Android TV Emulator and NVIDIA Shield validation flow guidance.
- TV input checklist content now explicitly includes Android TV Emulator and NVIDIA Shield validation sections with remote-primary and keyboard/mouse/gamepad fallback pass criteria.
- Setup-doc dry-run and scaffold coverage is now enforced in `tests/contracts/test_mobile_tv_setup_docs_contract.py`.
- Template-level mobile/TV workflow documentation now exists at `docs/MOBILE_TV_SETUP.md` and is linked from `README.md`.
- Mobile/TV runtime execution contract coverage is now active in `tests/contracts/test_mobile_tv_runtime_smoke_contract.py`: generated `mobile+tv` scaffold installs with Bun and runs app-local `lint`, `typecheck`, and `test` scripts in CI-safe mode for both apps.
- Mobile/TV workspace scripts now route through explicit smoke wrappers (`mobile|tv:lint:smoke`, `mobile|tv:typecheck:smoke`, `mobile|tv:test:smoke`), with app-local smoke tests (`smoke.test.js`) scaffolded for deterministic baseline `test` execution.
- Generated TV outputs now include `apps/tv/TV_VALIDATION_LOG.md` to capture emulator + Shield run metadata, remote-primary checkpoints, fallback-input outcomes, and evidence links.
- M5 CI hardening is now started: `.github/workflows/ci.yml` includes top-level workflow concurrency cancellation, dependency cache restoration (`actions/cache@v4` for uv and Bun cache paths), explicit TV input contract execution in cross-platform smoke coverage, and an explicit required preset-matrix contract step in guardrail flow.
- Branch protection guidance is now documented at `docs/BRANCH_PROTECTION.md`, including required status checks (`Tests` matrix + `Version Baseline Guardrail`) and non-blocking advisory treatment for `Secret Scan (Advisory)`.
- A dedicated preset regression CI lane is now defined as `Preset Regression Suite`, executing required preset/auth/fullstack regression contracts and documented in `docs/REGRESSION_SUITE.md`.
- Dependency governance policy is now documented in `docs/DEPENDENCY_UPGRADE_POLICY.md`, including cadence, version-range expectations, lockfile rules, and maintainer command flow (`nurt versions check/update`).
- Optional signing workflow design is now documented in `docs/OPTIONAL_SIGNING_PIPELINE.md` with a concrete secrets map and disabled-by-default enablement model.
- Manual release orchestration baseline now includes `.github/workflows/release.yml` (`workflow_dispatch`, `enable_signing` default `false`) and phased rollout gates in `docs/RELEASE_CHECKLIST.md`.
- CI hardening now includes a guard against missing scaffold env seed assets: `.gitignore` explicitly unignores `src/new_repo_template/snapshot_assets/templates/env/*.env`, and contract coverage verifies those template files exist and are not hidden by git ignore rules.
- Installer dry-run contract tests now resolve a POSIX shell explicitly (`bash` preferred, `sh` fallback) to avoid Windows-specific shell-resolution drift in full-suite CI runs.
- Installer dry-run shell-script contracts are now explicitly POSIX-scoped in tests (skipped on Windows runners) while Windows CI continues to enforce core scaffold/runtime contracts.
