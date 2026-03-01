# Quick Reference (Build Mode Start Here)

- [x] **Always-on monorepo**: every generated repo uses monorepo layout.
- [x] **Core stack**: Bun workspaces + Turborepo.
- [x] **Fullstack**: TanStack Start + Convex.
- [x] **Auth choice required**: explicit `clerk` or `better-auth` prompt; no default.
- [x] **Desktop**: dedicated Electron app via Electron Forge.
- [x] **Mobile**: Expo with AndroidTV support path.
- [x] **Python lane**: first-class selectable target (CLI/TUI focused).
- [x] **CI**: GitHub Actions, with native Windows CI required.
- [x] **Windows policy**: native Windows checks are required; WSL is optional supplemental validation.
- [x] **Convex mode**: cloud-first (local Convex not required by default flow).
- [x] **Signing policy**: unsigned/internal builds are acceptable now; signing/notarization is hardening-phase optional workflow.
- [x] **Execution loop**: strict YELLOW-RED-GREEN-BLUE with ongoing doc sync.
- [x] **Version policy**: template tracks latest known-good versions; generated repos lock to that snapshot on install.

---

# New Repo Template - Comprehensive Implementation Plan

## 0) Purpose

Build an always-monorepo template that supports:

- Fullstack web: TanStack Start + Convex
- Auth options for Convex apps: Clerk or Better Auth (explicit prompt, no default)
- Desktop frontend: Electron (dedicated desktop app)
- Mobile frontend: Expo, including AndroidTV support (Shield-compatible, generic AndroidTV)
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
- [x] Mobile TV validation depth: emulator + manual Shield checklist.
- [x] Release strategy: phased releases.
- [x] Python target remains first-class.
- [x] Convex usage target: cloud-first (no local Convex required in default flow).
- [x] Native Windows CI is required for backend/dev tooling and Electron packaging checks.
- [x] WSL is supplemental only, not a replacement for native Windows checks.
- [x] Code signing: deferred to hardening phase; not required for early milestones.

### 1.1 Version Baseline Policy (Locked Behavior)

- [ ] Keep a "latest known-good" baseline for core toolchain (`bun`, `turbo`, `typescript`, `python`) in template metadata.
- [ ] New project generation uses the latest known-good baseline and writes/retains lockfiles so first install is deterministic.
- [ ] For JS/TS dependencies: follow project rule to use `^` ranges while lockfiles pin concrete versions.
- [ ] For Python lane: keep pinned minimums compatible with `>=3.14` and generate deterministic `uv.lock` state.
- [ ] Provide an easy one-command update flow to refresh baseline versions and regenerate lockfiles.
- [ ] RED/CI must validate baseline versions are present and lockfiles are generated.

### 1.2 Version Update UX (Ease of Maintenance)

- [ ] Add a maintainer command (for example `bun run versions:update`) that:
  - [ ] Fetches latest stable versions for baseline-managed dependencies.
  - [ ] Updates template baseline metadata.
  - [ ] Regenerates lockfiles used by scaffolded outputs.
  - [ ] Produces a human-readable diff summary for PR review.
- [ ] Add a companion check command (for example `bun run versions:check`) for CI guardrails.

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

- [ ] Foundation only (monorepo shell only)
- [ ] Python-only target
- [ ] Web + Backend + Clerk
- [ ] Web + Backend + Better Auth
- [ ] Desktop-only target
- [ ] Mobile-only target
- [ ] Mobile + AndroidTV profile enabled
- [ ] Mixed: Web + Backend + Desktop
- [ ] Mixed: Web + Backend + Mobile + Desktop
- [ ] Mixed all-target sanity pass (includes Python lane)

---

## 3) BTCA Plan (Mandatory for YELLOW Research)

### 3.1 Approved Resources to Add (1-10)

- [ ] Add `turborepo` (git: `vercel/turborepo`)
- [ ] Add `bun` (git: `oven-sh/bun`)
- [ ] Add `tanstack-router-start` (git: `TanStack/router`)
- [ ] Add `convex-docs` (git: `get-convex/convex-backend`, docs path)
- [ ] Add `convex-better-auth` (git: `get-convex/better-auth`)
- [ ] Add `clerk-docs` (git: `clerk/clerk-docs`)
- [ ] Add `expo-docs` (git: `expo/expo`)
- [ ] Add `react-native-tvos` (git: `react-native-tvos/react-native-tvos`)
- [ ] Add `expo-tv-config` (git: `react-native-tvos/config-tv`)
- [ ] Add `better-auth-core` (git: `better-auth/better-auth`)

### 3.2 BTCA Sync Requirements

- [ ] Ensure project-level resources in `btca.config.jsonc` match `docs/BTCA_RESOURCES.md`
- [ ] Validate with `btca resources` and `btca status`
- [ ] Keep `docs/BTCA_RESOURCES.md` fully in-sync at each resource change
- [ ] Record explicit user confirmation for each resource add/remove event in session artifacts.
- [ ] Immediately sync `docs/BTCA_RESOURCES.md` after each `btca add`/`btca remove`.
- [ ] Re-validate with `btca resources` and `btca status` after each BTCA config change.

### 3.3 YELLOW Lookup Checklist (must be completed before implementation of each milestone)

- [ ] Ask Turborepo best practices for Bun workspaces, caching, and pipeline design.
- [ ] Ask TanStack Start project structure, SSR/runtime expectations, and monorepo guidance.
- [ ] Ask Convex cloud-first workflow expectations and codegen/versioning guidance.
- [ ] Ask Convex + Clerk integration constraints for TanStack Start.
- [ ] Ask Convex Better Auth integration constraints and known caveats.
- [ ] Ask Expo monorepo setup patterns with Bun/Turbo.
- [ ] Ask AndroidTV support details (`react-native-tvos`, config plugins, env flags, focus patterns).
- [ ] Ask Electron Forge monorepo integration and packaging best practices.
- [ ] Ask cross-platform script guidance for native Windows reliability.

### 3.4 BTCA Governance Log

- [x] 2026-03-01: User approved adding resources 1-10.
- [ ] Every future BTCA resource change is logged in `PROGRESS.md` with command result summary.

---

## 4) Target Monorepo Architecture (Template Output)

- [ ] Root workspace with `apps/*` and `packages/*`
- [ ] Shared infra packages for lint/tsconfig/tooling presets
- [ ] Selectable app targets generated into monorepo:
  - [ ] `apps/web` (TanStack Start)
  - [ ] `apps/backend` (Convex functions/config)
  - [ ] `apps/desktop` (Electron)
  - [ ] `apps/mobile` (Expo + AndroidTV-ready profile)
  - [ ] Python target lane (for CLI/TUI, optional FastAPI experiments)
- [ ] Shared UI/util package(s) for web + desktop reuse where practical
- [ ] Root scripts route through Turbo (`dev`, `build`, `test`, `lint`, `typecheck`)

### 4.1 CLI Behavior Contract (Scaffolder)

- [ ] Support explicit non-interactive mode for CI (`--no-interactive`).
- [ ] In non-interactive mode, missing required options fail with non-zero exit and clear remediation text.
- [ ] In interactive mode, wizard prompts can resolve missing options.
- [ ] Fullstack target requires explicit auth choice (`clerk` or `better-auth`).
- [ ] If fullstack is selected and auth is omitted:
  - [ ] interactive: prompt user
  - [ ] non-interactive: hard fail with validation error
- [ ] If auth is provided without fullstack target: hard fail with deterministic validation error.
- [ ] Invalid/contradictory target combinations fail before any files are written.
- [ ] Support `--dry-run` to print resolved scaffold plan without writing files.

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

- [ ] Add approved BTCA resources (1-10)
- [ ] Create/seed missing docs: `docs/LIVING_DOCS.md`, `docs/ARCHITECTURE.md`
- [ ] Expand `PROGRESS.md` from template placeholder to active tracker
- [ ] Keep `PLAN.md` as canonical implementation source of truth
- [ ] Define generator contract test scaffolding under `tests/`
- [ ] Define and codify version baseline metadata and update workflow.
- [ ] Add security baseline docs (`.env.example` convention + secret handling rules).

### DoD Gates

- [ ] `btca status` and `btca resources` are valid
- [ ] `docs/BTCA_RESOURCES.md` matches project resources exactly
- [ ] Planning docs exist and are internally consistent
- [ ] Baseline test scaffolding in `tests/` is present and runnable
- [ ] Version baseline policy is codified and covered by tests/CI checks.
- [ ] Security baseline conventions are documented and validated by scaffold tests.

---

## M1 - Always-On Monorepo Foundation

### Tasks

- [ ] Add root workspace config (`package.json` workspaces, `turbo.json`, Bun setup)
- [ ] Add cross-platform-safe scripts (avoid bash-only assumptions for core commands)
- [ ] Implement generator CLI: flags + interactive wizard fallback
- [ ] Implement selectable targets model (always monorepo, selected app types only)
- [ ] Preserve first-class Python lane support in monorepo selection
- [ ] Add contract tests for foundation scaffold shape and scripts
- [ ] Implement non-interactive/CI mode behavior and deterministic validation errors.
- [ ] Implement `--dry-run` behavior for preflight resolution.

### RED Tests (must fail first)

- [ ] Generated repo always has monorepo root shape
- [ ] Turbo tasks are wired for selected targets
- [ ] Bun workspace install works
- [ ] Python-selected target scaffolds expected files and runs baseline checks
- [ ] Invalid flag combinations fail with deterministic error messages.
- [ ] Non-interactive mode missing required choices fails without prompts.

### DoD Gates

- [ ] Foundation scaffold tests pass
- [ ] `dev/build/test/lint/typecheck` commands pass on selected minimal preset
- [ ] Cross-platform script checks pass on Linux/macOS/Windows CI
- [ ] CLI behavior contract tests pass for interactive and non-interactive paths.

---

## M2 - Fullstack Web Preset (TanStack Start + Convex + Auth Choice)

### Tasks

- [ ] Scaffold `apps/web` for TanStack Start
- [ ] Scaffold `apps/backend` for Convex cloud workflow
- [ ] Add explicit auth selection prompt (`clerk` or `better-auth`)
- [ ] Scaffold auth-specific wiring and env templates
- [ ] Add shared package integration where appropriate
- [ ] Implement credentialless CI-safe checks for Convex cloud-first scaffolds.

### RED Tests

- [ ] `fullstack + clerk` scaffold contract test
- [ ] `fullstack + better-auth` scaffold contract test
- [ ] Convex codegen and startup command smoke checks
- [ ] Auth-required env template assertions
- [ ] Auth-required behavior tests for non-interactive mode (error when omitted).
- [ ] Credentialless CI checks validate wiring without external auth keys.

### DoD Gates

- [ ] Both auth presets pass contract tests
- [ ] Local dev flow works for cloud Convex mode
- [ ] Native Windows backend dev/test commands pass in CI
- [ ] Docs updated with fullstack setup and auth decision flow
- [ ] Required CI path remains secret-free for baseline checks.

---

## M3 - Desktop Preset (Electron via Forge)

### Tasks

- [ ] Scaffold dedicated `apps/desktop`
- [ ] Integrate Electron Forge with monorepo/Turbo tasks
- [ ] Reuse shared UI/util packages with web where practical
- [ ] Provide desktop dev/start/build/package scripts
- [ ] Add internal distribution guidance for unsigned artifacts

### RED Tests

- [ ] Desktop scaffold contract test
- [ ] Electron app starts in dev mode
- [ ] Desktop packaging smoke tests per OS (unsigned)

### DoD Gates

- [ ] Desktop dev/build/package passes in CI (macOS/Linux/Windows)
- [ ] Native Windows Electron packaging passes
- [ ] No signing required for milestone completion
- [ ] Internal distribution docs for unsigned binaries are present

---

## M4 - Mobile + AndroidTV Preset (Expo)

### Tasks

- [ ] Scaffold `apps/mobile` with Expo baseline
- [ ] Add AndroidTV-ready configuration path
- [ ] Wire TV-related config/plugin conventions
- [ ] Add TV-focused env/build profile notes and scripts
- [ ] Add focus/navigation baseline patterns checklist

### RED Tests

- [ ] Mobile scaffold contract test
- [ ] TV config contract test (plugin/config presence and expected wiring)
- [ ] Android build profile checks for TV mode

### DoD Gates

- [ ] Expo mobile baseline passes lint/typecheck/tests
- [ ] AndroidTV emulator validation checklist completed
- [ ] Manual Shield checklist completed and logged
- [ ] Docs updated for mobile/TV setup, caveats, and test flow

---

## M5 - Hardening, CI Maturity, and Release Readiness

### Tasks

- [ ] Expand GitHub Actions matrix and cache strategy
- [ ] Add branch protection guidance (required status checks)
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

- [ ] `.github/workflows/ci.yml` (required)
- [ ] `.github/workflows/release.yml` (later)
- [ ] `.github/workflows/nightly.yml` (optional)

### 7.2 Required CI Matrix (initial)

- [ ] OS matrix: `ubuntu-latest`, `macos-latest`, `windows-latest`
- [ ] Foundation tasks: install, lint, typecheck, tests
- [ ] Scaffold contract tests for selected presets
- [ ] Required preset-combination matrix checks
- [ ] Windows-native checks for JS/TS backend workflows
- [ ] Windows-native Electron package smoke check
- [ ] Version baseline compliance check
- [ ] Lightweight secret scan job

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

- [ ] Convex is cloud-first for this template's fullstack lane.
- [ ] Convex local deployments are documented as optional advanced workflow, not default requirement.
- [ ] Primary fullstack backend path is TypeScript + Convex.
- [ ] Python remains first-class but primarily for CLI/TUI and optional local service experimentation.

### 9.1 Convex Cloud-First Testability (No Credentials Required in Baseline CI)

- [ ] Baseline CI uses scaffold contract tests and static wiring checks only.
- [ ] Baseline CI does not require Convex login, `CONVEX_DEPLOY_KEY`, or third-party auth credentials.
- [ ] Credential-dependent smoke tests are optional and separately gated.
- [ ] Generated repos include `.env.example` placeholders for required Convex/auth variables.

### 9.2 Python Lane First-Class Contract

- [ ] Define canonical scaffold shape for Python lane (app dir, source package, tests, config).
- [ ] Define baseline Python commands for generated projects:
  - [ ] `uv sync --group dev`
  - [ ] `uv run pytest`
  - [ ] `uv run ruff check .`
  - [ ] `uv run mypy src`
- [ ] Ensure Python lane participates in required preset matrix tests.
- [ ] Validate Python lane behavior in CI on supported host platforms.

---

## 10) Generator Contract and Test Strategy

### 10.1 Contract-First Tests (in `tests/`)

- [ ] Foundation scaffold contract tests
- [ ] Fullstack auth variant tests
- [ ] Desktop scaffold tests
- [ ] Mobile/TV scaffold tests
- [ ] Python lane scaffold tests
- [ ] Cross-platform command smoke tests
- [ ] Required preset-combination matrix tests (Section 2.1)
- [ ] CLI behavior contract tests (`--no-interactive`, invalid combos, auth-required flow)

### 10.2 Test Rules

- [ ] Tests create disposable temp output dirs
- [ ] No external credentials required for baseline tests
- [ ] Deterministic assertions on files/config/scripts
- [ ] CI-friendly and parallelizable where possible

### 10.3 Security Baseline (Early)

- [ ] Each generated target includes `.env.example` with placeholder values only.
- [ ] Add explicit secret-handling rules to docs (never commit real `.env` or credential files).
- [ ] Ensure generated `.gitignore` covers local env/secret artifacts.
- [ ] Add lightweight secret scanning in CI (advisory first, can become required later).

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
- [ ] **Scope creep:** phased release with strict DoD per milestone.

---

## 13) Final DoD (Program-Level)

The program is complete when:

- [ ] Always-monorepo template generation works with flags + wizard.
- [ ] Presets are available: web/backend/auth variants, desktop Electron, mobile Expo/TV, python lane.
- [ ] Required CI matrix is green on Linux/macOS/Windows.
- [ ] Required preset combination matrix (Section 2.1) is green.
- [ ] Native Windows backend and Electron checks are passing.
- [ ] Contract tests in `tests/` comprehensively cover scaffold outputs.
- [ ] Core docs and trackers are synchronized and current.
- [ ] Phased release notes/checklists are complete.

---

## 14) Immediate Next Actions (Build Mode Step 1)

- [ ] Execute M0 first (BTCA resources + docs baseline + test scaffolding).
- [ ] Create and run first RED contract test for monorepo foundation output.
- [ ] Implement M1 in strict YELLOW-RED-GREEN-BLUE slices.
- [ ] Keep documentation synchronized continuously during implementation.
