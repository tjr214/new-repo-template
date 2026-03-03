# Quick Reference (Build Mode Start Here)

- [x] **Always-on monorepo**: every generated repo uses monorepo layout.
- [x] **Core stack**: Bun workspaces + Turborepo.
- [x] **Fullstack**: TanStack Start + Convex.
- [x] **Auth choice required**: explicit `clerk` or `better-auth` prompt; no default.
- [x] **Auth rule scope**: every preset that includes both `web` and `backend` must explicitly choose auth.
- [x] **Desktop**: dedicated Electron app via Electron Forge.
- [x] **Mobile + TV split**: Expo mobile app and separate Expo TV app.
- [x] **Python lane**: first-class selectable target (CLI/TUI focused).
- [x] **CI**: GitHub Actions, with native Windows CI required.
- [x] **Windows policy**: native Windows checks are required; WSL is optional supplemental validation.
- [x] **Convex mode**: cloud-first (local Convex not required by default flow).
- [x] **Signing policy**: unsigned/internal builds are acceptable now; signing/notarization is hardening-phase optional workflow.
- [x] **Execution loop**: strict YELLOW-RED-GREEN-BLUE with ongoing doc sync.
- [x] **Version policy**: template tracks latest known-good versions; generated repos lock to that snapshot on install.
- [x] **Root `pyproject.toml` invariant**: always present in generated repos, even when Python target is not selected.
- [x] **Python lane pyproject boundary**: root `pyproject.toml` remains repo/tooling-level; Python target also scaffolds a lane-local `pyproject.toml` under the Python app directory.
- [x] **Primary UX tool**: global CLI is `nurt` (Nu-Repo Template).
- [x] **Project brand**: project identity is `nurt.ai`; CLI command remains `nurt`.
- [x] **Distribution model**: install `nurt` directly from git via `uv tool install --from git+... nurt`.
- [x] **Execution entrypoint**: `nurt new <project-name>` (no `install.sh` fallback path).
- [x] **Tool update policy**: `nurt` checks for updates on every command run; explicit upgrade command is `nurt update`.
- [x] **Template sync command naming**: use `nurt template-assets sync`.
- [x] **Snapshot model**: `nurt` ships bundled snapshot assets by default (deterministic, offline-capable) and can sync live template assets via command.

---

# New Repo Template - Comprehensive Implementation Plan

## 0) Purpose

Build an always-monorepo template that supports:

- `nurt.ai` global CLI workflow for AI-agent-ready project bootstrapping (`nurt new <project-name>`)

- Fullstack web: TanStack Start + Convex
- Auth options for Convex apps: Clerk or Better Auth (explicit prompt, no default)
- Desktop frontend: Electron (dedicated desktop app)
- Mobile frontend: Expo mobile app
- TV frontend: separate Expo TV app for AndroidTV (Shield-compatible, generic AndroidTV)
- Python lane: first-class selectable target (primarily CLI/TUI, optional FastAPI experimentation)

This plan is comprehensive and execution-ready so a fresh Build Mode context can execute directly from this file.

---

## 1) Locked Decisions

- [x] Monorepo layout is always-on for all generated projects.
- [x] Task orchestration: Turborepo (`turbo`).
- [x] JS/TS package manager/workspaces: Bun.
- [x] Scaffold UX: flags + wizard fallback.
- [x] Fullstack auth: explicit choice required (`clerk` or `better-auth`), no implicit default.
- [x] CI system: GitHub Actions.
- [x] Desktop: dedicated Electron app.
- [x] TV app is always separate from mobile app (`apps/tv` distinct from `apps/mobile`).
- [x] TV input model: remote is primary HID; keyboard/mouse/gamepad are supported secondary inputs.
- [x] Mobile TV validation depth: emulator + manual Shield checklist.
- [x] Release strategy: phased releases.
- [x] Python target remains first-class.
- [x] Convex usage target: cloud-first (no local Convex required in default flow).
- [x] Native Windows CI is required for backend/dev tooling and Electron packaging checks.
- [x] WSL is supplemental only, not a replacement for native Windows checks.
- [x] Code signing: deferred to hardening phase; not required for early milestones.
- [x] Root `pyproject.toml` is mandatory for template tooling compatibility (including RALPH loader flow), independent of selected targets.
- [x] When Python lane is selected, scaffold a Python-lane-local `pyproject.toml`; do not treat the root `pyproject.toml` as the Python app package metadata file.
- [x] Branding decision: product/repository identity is `nurt.ai` with `nurt` as the CLI command.

### 1.1 Version Baseline Policy (Locked Behavior)

- [x] Keep a "latest known-good" baseline for core toolchain (`bun`, `turbo`, `typescript`, `python`) in template metadata.
- [ ] New project generation uses the latest known-good baseline and writes/retains lockfiles so first install is deterministic.
- [ ] For JS/TS dependencies: follow project rule to use `^` ranges while lockfiles pin concrete versions.
- [ ] For Python lane: keep pinned minimums compatible with `>=3.14` and generate deterministic `uv.lock` state.
- [x] Provide an easy one-command update flow to refresh baseline versions and regenerate lockfiles.
- [x] RED/CI must validate baseline versions are present and lockfiles are generated.

### 1.2 Version Update UX (Ease of Maintenance)

- [x] Add a maintainer command (`nurt versions update`) that:
  - [x] Fetches latest stable versions for baseline-managed dependencies.
  - [x] Updates template baseline metadata.
  - [x] Regenerates lockfiles used by scaffolded outputs.
  - [x] Produces a human-readable diff summary for PR review.
- [x] Add a companion check command (`nurt versions check`) for CI guardrails.

---

## 2) Platform Support Policy (DoD Scope)

### Runtime/Dev Scope

- [ ] Native macOS support
- [ ] Native Linux support
- [ ] Native Windows support (no WSL dependency for core JS/TS flow)

### Windows Clarification

- [ ] Windows CI validates native Windows behavior for Bun scripts, TypeScript tooling, TanStack app flows, Convex CLI flows, and Electron packaging.
- [ ] WSL checks (if added later) are non-blocking supplemental validation.

### 2.1 Required Preset Combination Matrix

- [x] Foundation only (monorepo shell only)
- [x] Python-only target
- [x] Web + Backend + Clerk
- [x] Web + Backend + Better Auth
- [x] Desktop-only target
- [x] Mobile-only target
- [x] TV-only target
- [x] Mobile + TV dual-target (separate apps)
- [x] Mixed: Web + Backend + Clerk + Desktop
- [x] Mixed: Web + Backend + Better Auth + Desktop
- [x] Mixed: Web + Backend + Clerk + Mobile + Desktop
- [x] Mixed: Web + Backend + Better Auth + Mobile + Desktop
- [x] Mixed: Web + Backend + Clerk + TV + Desktop
- [x] Mixed: Web + Backend + Better Auth + TV + Desktop
- [x] Mixed: Web + Backend + Clerk + Mobile + TV + Desktop
- [x] Mixed: Web + Backend + Better Auth + Mobile + TV + Desktop
- [x] All-target sanity pass + Clerk (includes Python lane)
- [x] All-target sanity pass + Better Auth (includes Python lane)

---

## 3) BTCA Plan (Mandatory for YELLOW Research)

### 3.1 Approved Resources to Add (1-10)

- [x] Add `turborepo` (git: `vercel/turborepo`)
- [x] Add `bun` (git: `oven-sh/bun`)
- [x] Add `tanstack-router-start` (git: `TanStack/router`)
- [x] Add `convex-docs` (git: `get-convex/convex-docs`)
- [x] Add `convex-better-auth` (git: `get-convex/better-auth`)
- [x] Add `clerk-docs` (git: `clerk/clerk-docs`)
- [x] Add `expo-docs` (git: `expo/expo`)
- [x] Add `react-native-tvos` (git: `react-native-tvos/react-native-tvos`)
- [x] Add `expo-tv-config` (git: `react-native-tvos/config-tv`)
- [x] Add `better-auth-core` (git: `better-auth/better-auth`)

### 3.2 BTCA Sync Requirements

- [x] Ensure project-level resources in `btca.config.jsonc` match `docs/BTCA_RESOURCES.md`
- [x] Validate with `btca resources` and `btca status`
- [x] Keep `docs/BTCA_RESOURCES.md` fully in-sync at each resource change
- [x] Record explicit user confirmation for each resource add/remove event in session artifacts.
- [x] Immediately sync `docs/BTCA_RESOURCES.md` after each `btca add`/`btca remove`.
- [x] Re-validate with `btca resources` and `btca status` after each BTCA config change.

### 3.3 YELLOW Lookup Checklist (must be completed before implementation of each milestone)

- [x] Ask Turborepo best practices for Bun workspaces, caching, and pipeline design.
- [x] Ask TanStack Start project structure, SSR/runtime expectations, and monorepo guidance.
- [x] Ask Convex cloud-first workflow expectations and codegen/versioning guidance.
- [x] Ask Convex + Clerk integration constraints for TanStack Start.
- [x] Ask Convex Better Auth integration constraints and known caveats.
- [x] Ask Expo monorepo setup patterns with Bun/Turbo.
- [x] Ask AndroidTV support details (`react-native-tvos`, config plugins, env flags, focus patterns).
- [x] Ask Electron Forge monorepo integration and packaging best practices.
- [x] Ask cross-platform script guidance for native Windows reliability.

### 3.4 BTCA Governance Log

- [x] 2026-03-01: User approved adding resources 1-10.
- [ ] Every future BTCA resource change is logged in `PROGRESS.md` with command result summary.

---

## 4) Target Monorepo Architecture (Template Output)

- [x] Root workspace with `apps/*` and `packages/*`
- [ ] Root `pyproject.toml` is always scaffolded and retained for template/runtime tooling requirements.
- [ ] Root `pyproject.toml` is repo-level metadata/tooling anchor, not a replacement for app-local Python package metadata.
- [ ] Shared infra packages for lint/tsconfig/tooling presets
- [ ] Selectable app targets generated into monorepo:
  - [ ] `apps/web` (TanStack Start)
  - [ ] `apps/backend` (Convex functions/config)
  - [x] `apps/desktop` (Electron)
  - [ ] `apps/mobile` (Expo mobile app)
  - [ ] `apps/tv` (Expo AndroidTV app, separate from mobile)
  - [ ] Python target lane (for CLI/TUI, optional FastAPI experiments) with lane-local `pyproject.toml`
- [x] Shared UI/util package(s) for web + desktop reuse where practical
- [x] Root scripts route through Turbo (`dev`, `build`, `test`, `lint`, `typecheck`)

### 4.1 CLI Behavior Contract (Scaffolder)

- [x] Support explicit non-interactive mode for CI (`--no-interactive`).
- [x] In non-interactive mode, missing required options fail with non-zero exit and clear remediation text.
- [ ] In interactive mode, wizard prompts can resolve missing options.
- [x] Any configuration that includes both `web` and `backend` requires explicit auth choice (`clerk` or `better-auth`).
- [ ] If `web` and `backend` are selected and auth is omitted:
  - [ ] interactive: prompt user
  - [x] non-interactive: hard fail with validation error
- [x] If auth is provided without both `web` and `backend`: hard fail with deterministic validation error.
- [x] Mixed preset entries with `web` + `backend` are auth-parameterized only (no auth-agnostic mixed presets).
- [x] Invalid/contradictory target combinations fail before any files are written.
- [x] Support `--dry-run` to print resolved scaffold plan without writing files.
- [x] No generator option may suppress root `pyproject.toml`; it is a global invariant.
- [x] If Python target is selected, generator must scaffold Python lane-local `pyproject.toml` in the lane directory in addition to root `pyproject.toml`.
- [x] `tv` target always resolves to a separate `apps/tv` scaffold and never mutates `apps/mobile` into TV mode.
- [x] If both `mobile` and `tv` are selected, generator creates both apps with shared packages only where explicit.
- [x] Duplicate target selections fail with deterministic validation errors.
- [x] Generator writes are failure-atomic: no partial scaffold output remains on failure.
- [x] Implement transactional write strategy (stage temp output then atomic move) or guaranteed cleanup-on-failure.

### 4.2 Installation Orchestration Contract (`nurt` Global CLI)

- [x] Primary execution flow is `nurt new <project-name>` (no `install.sh` fallback path).
- [ ] `nurt` is installed from git using uv tools (`uv tool install --from git+... nurt`).
- [x] `nurt` always performs update-check logic at command startup and prints deterministic notice when an update exists.
- [x] `nurt update` performs explicit tool upgrade flow.
- [x] `nurt new` supports both interactive wizard/TUI mode and non-interactive flag mode.
- [x] If no targets are provided to `nurt new`, interactive mode should resolve target/auth selection via prompts.
- [x] `nurt new --dry-run` is non-destructive and validates full scaffold plan resolution.
- [ ] Existing template governance/workflow assets remain in generated repos; scaffold output overlays app/runtime files only.
- [x] `nurt template-assets sync` replaces template asset sync script behavior with one cohesive command.
- [x] `nurt tools sync` consolidates tool update/install behavior currently spread across scripts.

### 4.3 Snapshot Asset Packaging Contract (for `nurt`)

- [x] Source-of-truth assets are declared by manifest (explicit include/exclude list, deterministic ordering).
- [x] Snapshot generation command produces bundled package assets from manifest-scoped files.
- [x] Snapshot generation writes metadata manifest (source commit, generation timestamp, file hashes, nurt version).
- [x] Packaged snapshot files are included in the wheel/sdist via hatchling build config and loaded at runtime with `importlib.resources`.
- [x] `nurt new` uses bundled snapshot assets by default (offline-capable, deterministic behavior).
- [x] `nurt template-assets sync` can pull/update live assets from the template repository on demand.
- [x] Snapshot generation validates forbidden-path exclusions (`.git`, caches, virtualenvs, local secrets).
- [x] RED tests assert snapshot determinism and packaged-asset availability after install.

---

## 5) Execution Method (Required)

For each implementation unit, follow:

- [ ] **YELLOW**: scan/read all relevant files + run BTCA resource-specific asks before coding.
- [ ] **RED**: add failing tests first (contract/integration-first for template scaffolding).
- [ ] **GREEN**: implement minimum code required to pass RED tests.
- [ ] **BLUE**: refactor/harden while preserving passing tests.

Documentation must be updated continuously during GREEN/BLUE:

- [ ] `docs/LIVING_DOCS.md`
- [ ] `docs/ARCHITECTURE.md`
- [ ] `PROGRESS.md`
- [ ] New `docs/session-summaries/SESSION_X_SUMMARY.md` (never overwrite existing summaries)

---

## 6) Milestones, Tasks, and DoD Gates

## M0 - Planning Baseline + BTCA Foundation

### Tasks

- [x] Add approved BTCA resources (1-10)
- [x] Create/seed missing docs: `docs/LIVING_DOCS.md`, `docs/ARCHITECTURE.md`
- [x] Expand `PROGRESS.md` from template placeholder to active tracker
- [x] Keep `PLAN.md` as canonical implementation source of truth
- [x] Define generator contract test scaffolding under `tests/`
- [x] Define and codify version baseline metadata and update workflow.
- [x] Add security baseline docs (`.env.example` convention + secret handling rules).

### DoD Gates

- [x] `btca status` and `btca resources` are valid
- [x] `docs/BTCA_RESOURCES.md` matches project resources exactly
- [x] Planning docs exist and are internally consistent
- [x] Baseline test scaffolding in `tests/` is present and runnable
- [x] Version baseline policy is codified and covered by tests/CI checks.
- [x] Security baseline conventions are documented and validated by scaffold tests.

---

## M1 - Always-On Monorepo Foundation

### Tasks

- [x] Add root workspace config (`package.json` workspaces, `turbo.json`, Bun setup)
- [x] Add cross-platform-safe scripts (avoid bash-only assumptions for core commands)
- [x] Implement generator CLI: flags + interactive wizard fallback
- [x] Implement global CLI entrypoint `nurt` with `new`, `update`, `tools sync`, and `template-assets sync` commands.
- [x] Implement selectable targets model (always monorepo, selected app types only)
- [x] Preserve first-class Python lane support in monorepo selection
- [x] Add contract tests for foundation scaffold shape and scripts
- [x] Ensure root `pyproject.toml` is generated for every preset combination (including non-Python selections).
- [x] Implement non-interactive/CI mode behavior and deterministic validation errors.
- [x] Implement `--dry-run` behavior for preflight resolution.
- [x] Implement failure-atomic scaffold writes (transactional or cleanup-on-failure).
- [x] Add `--dry-run` mode to `nurt new` and `nurt tools sync` for non-destructive validation.
- [x] Integrate scaffold engine invocation into `nurt new` while preserving existing template assets.
- [x] Remove script-first bootstrap path from user docs in favor of global `nurt` command flow.

### RED Tests (must fail first)

- [x] Generated repo always has monorepo root shape
- [x] Turbo tasks are wired for selected targets
- [x] Bun workspace install works
- [x] Python-selected target scaffolds expected files and runs baseline checks
- [x] Root `pyproject.toml` exists for every generated preset, including JS-only and TV-only outputs.
- [x] Invalid flag combinations fail with deterministic error messages.
- [x] Non-interactive mode missing required choices fails without prompts.
- [x] Any `web` + `backend` selection without auth fails with deterministic validation error.
- [x] Simulated mid-generation failure leaves no partial repo artifacts.
- [x] `nurt new --dry-run` and `nurt tools sync --dry-run` execute successfully without mutating repository state.
- [x] `nurt new` interactive wizard flow resolves targets/auth and produces deterministic equivalent plan output.
- [x] Native non-dry-run sync commands surface deterministic validation/failure messaging (`nurt tools sync` failure summary path and `nurt template-assets sync` root/dirty-repo guardrails).
- [x] `nurt new` interactive stdin-closure paths fail cleanly with remediation guidance instead of raw traceback output.
- [x] Mixed combo validation contracts cover additional unsupported auth/target combinations (`web+backend+desktop` auth requirement and auth misuse with partial mixed selections).
- [x] `nurt versions update` regenerates lockfiles (with dry-run planning and summary reporting), and `nurt versions check --check-lockfiles` enforces lockfile presence.

### DoD Gates

- [x] Foundation scaffold tests pass
- [x] `dev/build/test/lint/typecheck` commands pass on selected minimal preset
- [x] Cross-platform script checks pass on Linux/macOS/Windows CI
- [x] CLI behavior contract tests pass for interactive and non-interactive paths.
- [x] Root `pyproject.toml` invariant is enforced by tests across required matrix combinations.
- [x] Failure-atomicity tests pass (transactional write or cleanup-on-failure verified).

---

## M2 - Fullstack Web Preset (TanStack Start + Convex + Auth Choice)

### Tasks

- [x] Scaffold `apps/web` for TanStack Start
- [x] Scaffold `apps/backend` for Convex cloud workflow
- [x] Add explicit auth selection prompt (`clerk` or `better-auth`)
- [x] Scaffold auth-specific wiring and env templates
- [x] Add shared package integration where appropriate
- [x] Implement credentialless CI-safe checks for Convex cloud-first scaffolds.

### RED Tests

- [x] `fullstack + clerk` scaffold contract test
- [x] `fullstack + better-auth` scaffold contract test
- [x] Convex codegen and startup command smoke checks
- [x] Auth-required env template assertions
- [x] Auth-required behavior tests for non-interactive mode (error when omitted).
- [x] Mixed `web` + `backend` presets require explicit auth and pass in both auth variants.
- [x] Credentialless CI checks validate wiring without external auth keys.

### DoD Gates

- [x] Both auth presets pass contract tests
- [x] Local dev flow works for cloud Convex mode
- [x] Native Windows backend dev/test commands pass in CI
- [x] Docs updated with fullstack setup and auth decision flow
- [x] Required CI path remains secret-free for baseline checks.

---

## M3 - Desktop Preset (Electron via Forge)

### Tasks

- [x] Scaffold dedicated `apps/desktop`
- [x] Integrate Electron Forge with monorepo/Turbo tasks
- [x] Reuse shared UI/util packages with web where practical
- [x] Provide desktop dev/start/build/package scripts
- [x] Add internal distribution guidance for unsigned artifacts

### RED Tests

- [x] Desktop scaffold contract test
- [x] Electron app starts in dev mode
- [x] Desktop packaging smoke tests per OS (unsigned)

### DoD Gates

- [x] Desktop dev/build/package passes in CI (macOS/Linux/Windows)
- [x] Native Windows Electron packaging passes
- [x] No signing required for milestone completion
- [x] Internal distribution docs for unsigned binaries are present

---

## M4 - Mobile + TV Presets (Expo, Separate Apps)

### Tasks

- [x] Scaffold `apps/mobile` with Expo mobile baseline
- [x] Scaffold `apps/tv` with Expo AndroidTV baseline (separate app)
- [x] Wire TV-related config/plugin conventions in `apps/tv` only
- [x] Add TV-focused env/build profile notes and scripts for dedicated TV app
- [x] Add TV focus/navigation baseline patterns checklist (remote-primary)
- [x] Add keyboard/mouse/gamepad fallback input support checklist for TV app
- [x] Add CI-safe runtime smoke contract for mobile/TV `lint`/`typecheck`/`test` baseline scripts
- [x] Scaffold TV validation log artifact for emulator + Shield run tracking

### RED Tests

- [x] Mobile scaffold contract test
- [x] TV scaffold contract test (separate `apps/tv` output)
- [x] TV config contract test (plugin/config presence and expected wiring in `apps/tv`)
- [x] Android build profile checks for TV app
- [x] HID contract test for TV app input handling (remote primary + keyboard/mouse/gamepad supported)
- [x] Mobile/TV setup docs + validation checklist contract test coverage
- [x] Mobile/TV runtime smoke contract coverage for CI-safe `lint`/`typecheck`/`test` command viability

### DoD Gates

- [x] Expo mobile baseline passes lint/typecheck/tests
- [x] Expo TV baseline passes lint/typecheck/tests
- [ ] AndroidTV emulator validation checklist completed
- [ ] Manual Shield checklist completed and logged
- [ ] TV input UX checks pass: remote-primary navigation and keyboard/mouse/gamepad support
- [x] Docs updated for separate mobile/TV setup, caveats, and test flow

### M4 Deferred Hardware Validation Carryover (must close before release)

- [ ] Ensure execution environment has Android SDK tooling available (`adb`, `emulator`, Android TV AVD image).
- [ ] Execute Android TV Emulator checklist and log outcomes in generated `apps/tv/TV_VALIDATION_LOG.md`.
- [ ] Execute NVIDIA Shield checklist and log outcomes in generated `apps/tv/TV_VALIDATION_LOG.md`.
- [ ] Confirm remote-primary + keyboard/mouse/gamepad fallback UX from recorded emulator + Shield runs.
- [ ] Keep this carryover open while M5 begins; do not consider program-level release readiness complete until it is closed.

---

## M5 - Hardening, CI Maturity, and Release Readiness

### Tasks

- [x] Begin hardening slices while preserving M4 deferred hardware-validation carryover as an explicit pre-release gate.
- [x] Expand GitHub Actions matrix and cache strategy
- [x] Add branch protection guidance (required status checks)
- [ ] Add regression suite across preset combinations
- [ ] Add upgrade/versioning policy for template dependencies
- [ ] Add optional signing pipeline design (disabled by default)

### DoD Gates

- [ ] Required CI jobs green on PRs
- [ ] Preset combination matrix passes
- [ ] `docs/ARCHITECTURE.md`, `docs/LIVING_DOCS.md`, `PROGRESS.md` fully synced
- [ ] Optional signing workflow documented with secrets map and enablement steps
- [ ] Release checklist complete for phased rollout

---

## 7) GitHub Actions CI Design (Initial)

### 7.1 Workflow Files

- [x] `.github/workflows/ci.yml` (required)
- [ ] `.github/workflows/release.yml` (later)
- [ ] `.github/workflows/nightly.yml` (optional)

### 7.2 Required CI Matrix (initial)

- [x] OS matrix: `ubuntu-latest`, `macos-latest`, `windows-latest`
- [ ] Foundation tasks: install, lint, typecheck, tests
- [x] Scaffold contract tests for selected presets
- [x] Required preset-combination matrix checks
- [x] Windows-native checks for JS/TS backend workflows
- [x] Windows-native Electron package smoke check
- [x] Dedicated TV app scaffold and input-contract checks
- [x] Version baseline compliance check
- [x] Lightweight secret scan job

### 7.3 Non-Blocking/Deferred CI

- [ ] Signing/notarization jobs (run only if secrets exist)
- [ ] iOS packaging (macOS + signing assets) deferred
- [ ] Full installer publishing deferred until hardening

---

## 8) Code Signing/Notarization Strategy

### Current Policy (development phase)

- [ ] Unsigned builds are acceptable for local/internal use.
- [ ] CI requires successful unsigned packaging, not signed release artifacts.

### Future Policy (hardening/release phase)

- [ ] Add optional signing jobs behind secrets and release flags.
- [ ] Keep unsigned path available for internal/private distribution.
- [ ] Document trust/warning expectations for unsigned apps.

---

## 9) Backend and Runtime Strategy

- [x] Convex is cloud-first for this template's fullstack lane.
- [x] Convex local deployments are documented as optional advanced workflow, not default requirement.
- [x] Primary fullstack backend path is TypeScript + Convex.
- [x] Python remains first-class but primarily for CLI/TUI and optional local service experimentation.

### 9.1 Convex Cloud-First Testability (No Credentials Required in Baseline CI)

- [x] Baseline CI uses scaffold contract tests and static wiring checks only.
- [x] Baseline CI does not require Convex login, `CONVEX_DEPLOY_KEY`, or third-party auth credentials.
- [x] Credential-dependent smoke tests are optional and separately gated.
- [x] Generated repos include `.env.example` placeholders for required Convex/auth variables.

### 9.2 Python Lane First-Class Contract

- [x] Define canonical scaffold shape for Python lane (app dir, source package, tests, config).
- [x] Python lane must have its own app-local `pyproject.toml` (for package/app metadata and Python deps), while root `pyproject.toml` remains the monorepo-level invariant.
- [x] Define baseline Python commands for generated projects:
  - [x] `uv sync --group dev`
  - [x] `uv run pytest`
  - [x] `uv run ruff check .`
  - [x] `uv run mypy src`
- [x] Ensure Python lane participates in required preset matrix tests.
- [x] Validate Python lane behavior in CI on supported host platforms.

---

## 10) Generator Contract and Test Strategy

### 10.1 Contract-First Tests (in `tests/`)

- [x] Foundation scaffold contract tests
- [x] Fullstack auth variant tests
- [x] Desktop scaffold tests
- [x] Mobile scaffold tests
- [x] TV scaffold tests
- [x] Python lane scaffold tests
- [x] Cross-platform command smoke tests
- [x] Required preset-combination matrix tests (Section 2.1)
- [x] CLI behavior contract tests (`--no-interactive`, invalid combos, auth-required flow)
- [x] Matrix tests must include auth variants for every preset containing both `web` and `backend`.
- [x] Matrix tests must assert root `pyproject.toml` presence for every generated configuration.

### 10.2 Test Rules

- [x] Tests create disposable temp output dirs
- [x] No external credentials required for baseline tests
- [x] Deterministic assertions on files/config/scripts
- [x] CI-friendly and parallelizable where possible
- [x] Failure-path tests assert no partial scaffold output on generator errors.

### 10.3 Security Baseline (Early)

- [x] Each generated target includes `.env.example` with placeholder values only.
- [x] Add explicit secret-handling rules to docs (never commit real `.env` or credential files).
- [x] Ensure generated `.gitignore` covers local env/secret artifacts.
- [x] Add lightweight secret scanning in CI (advisory first, can become required later).

---

## 11) Documentation and Tracking Protocol

During implementation, after each substantial slice:

- [ ] Update `PROGRESS.md` with timestamp, phase, completed items, and next tasks
- [ ] Update `docs/LIVING_DOCS.md` with practical notes and known caveats
- [ ] Update `docs/ARCHITECTURE.md` with decision/rationale updates
- [ ] Update `docs/BTCA_RESOURCES.md` if BTCA resources changed
- [ ] Create a new session summary (`docs/session-summaries/SESSION_X_SUMMARY.md`) without overwriting existing files

---

## 12) Risks and Mitigations

- [ ] **Cross-platform shell breakage (Windows):** prefer Node-based scripts and cross-platform command patterns.
- [ ] **Toolchain drift across presets:** pin versions with policy and run matrix CI.
- [ ] **Auth integration churn:** keep variant-specific tests and template fixtures.
- [ ] **Electron packaging complexity:** use Forge defaults and incremental packaging gates.
- [ ] **AndroidTV ecosystem instability:** lock known-good config paths and maintain manual Shield checklist.
- [ ] **TV UX quality drift:** enforce remote-primary focus checks and fallback HID tests (keyboard/mouse/gamepad).
- [ ] **Partial scaffold output on failure:** use transactional writes or strict cleanup-on-failure and test both paths.
- [ ] **Scope creep:** phased release with strict DoD per milestone.

---

## 13) Final DoD (Program-Level)

The program is complete when:

- [ ] Always-monorepo template generation works with flags + wizard.
- [ ] Presets are available: web/backend/auth variants, desktop Electron, separate mobile app, separate TV app, python lane.
- [ ] Required CI matrix is green on Linux/macOS/Windows.
- [ ] Required preset combination matrix (Section 2.1) is green, including auth variants for every `web` + `backend` preset.
- [ ] Native Windows backend and Electron checks are passing.
- [ ] TV app guarantees remote-primary UX with keyboard/mouse/gamepad support.
- [ ] Contract tests in `tests/` comprehensively cover scaffold outputs.
- [ ] Root `pyproject.toml` invariant holds for all generated repositories.
- [ ] Generator failure atomicity is guaranteed by implementation and tests.
- [ ] Core docs and trackers are synchronized and current.
- [ ] Phased release notes/checklists are complete.

---

## 14) Immediate Next Actions (Build Mode Step 1)

- [x] Start `nurt` CLI migration slice: introduce global command entrypoint and command routing (`new`, `update`, `tools sync`, `template-assets sync`).
- [x] Add first RED tests for `nurt new` parity with current scaffold contracts.
- [x] Add RED tests for `nurt` startup update-check behavior and `nurt update` execution path.
- [x] Add snapshot asset generation command + metadata manifest scaffolding and tests.
- [x] Replace script-wrapper behavior inside `nurt tools sync` / `nurt template-assets sync` with native Python command implementations.
- [x] Implement polished Rich/Textual interactive UI for `nurt new` (Rich table/panel prompt layer with deterministic plain fallback).
- [x] Wire CI guardrail execution for `nurt versions check --check-lockfiles --check-latest` in GitHub Actions.
- [ ] Keep documentation synchronized continuously during implementation.
