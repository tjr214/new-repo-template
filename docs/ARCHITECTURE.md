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
- Auth integration mode for backend-capable scaffolds: explicit prompt (`clerk`, `better-auth`, or `none`)
- Auth selection rule: any scaffold selecting `backend` must explicitly choose auth, even when `web` is absent
- Desktop packaging tool: Electron Forge
- Convex workflow: cloud-first
- CI platform: GitHub Actions
- Platform support policy: native macOS + Linux + Windows (WSL optional supplemental only)
- Version policy: latest known-good baseline in template, deterministic lockfile state in generated repos
- Scaffold contract: explicit preset-combination matrix and deterministic non-interactive CLI behavior
- Generator write model: failure-atomic scaffolding (transactional writes or cleanup-on-failure)
- TV input contract: remote-primary navigation with keyboard/mouse/gamepad support as secondary inputs
- Root workspace invariant: generated repo roots scaffold shared monorepo files only (`.gitignore`, `package.json`, `turbo.json`, `eslint.config.mjs`, workspace directories), not Python-only metadata
- Python lane metadata boundary: Python app metadata, interpreter pinning, and Python lock state live only under `apps/python/` (`pyproject.toml`, `.python-version`, `uv.lock`) when the Python target is selected
- Security baseline: root `.gitignore` baseline (copied from template root) includes env/secret guards and JS dependency directory ignores (`node_modules/`, `**/node_modules/`); Python-only metadata is isolated to `apps/python`, and selected targets scaffold placeholder-only `.env.example`
- Global UX direction: distribute and run as `nurt` global CLI installed via `uv tool install git+...`; user entrypoint is `nurt new <project-name>`

## Planned Topology

- Root workspace with `apps/*` and `packages/*`
- Shared packages for config and reusable code
- Selectable target generators within an always-on monorepo shell

## Current Implementation Status

- Milestones M0-M5 are complete in tracker state; M4 hardware validation now includes durable emulator evidence plus a physical NVIDIA Shield pass, and the remaining keyboard-only fallback gap was explicitly closed by user direction rather than a direct keyboard hardware run. M5 hardening is complete with required PR checks now green and includes CI matrix/cache strategy expansion, branch-protection guidance, dedicated preset-regression CI coverage, dependency upgrade/versioning policy documentation, optional signing/release checklist design, CI env-template asset reliability hardening, Windows installer-script contract shell-resolution hardening, updater tooling support for GitHub CLI (`gh`), focused Windows-critical CI lane tuning, and advisory secret-scan stability hardening (pinned `gitleaks/gitleaks-action@v2.3.9`, comment/artifact upload API calls disabled, and full-history checkout enabled for commit-range scanning).
- The previous root planning trackers are archived at `docs/archive/plans/PLAN_2026-03-08_07-49-04_PM.md` and `docs/archive/plans/PROGRESS_2026-03-08_07-49-04_PM.md`, and the root `PLAN.md` / `PROGRESS.md` files are now reset as next-cycle stubs without changing the implemented system architecture.
- Project BTCA resource layer is now configured for the locked dependency set captured in `docs/archive/plans/PLAN_2026-03-08_07-49-04_PM.md`.
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
- Script-first UX has been superseded: primary execution is `uv tool install git+...` followed by `nurt new <project-name>` with bundled snapshot assets and explicit `nurt update` lifecycle.
- `nurt` command bootstrap is implemented at `src/new_repo_template/nurt_cli.py` with command routing (`new`, `update`, `tools sync`, `template-assets sync`) and startup update-check hook.
- `nurt new` now includes a real Textual wizard for interactive TTY project-name/target/auth resolution, with deterministic plain prompt fallback for non-interactive or enhanced-UI-unavailable sessions, a typed `WizardState` coordinator for project-name normalization plus target/auth/step validation, and a compact responsive mode for narrow terminals and `80x24` layouts.
- Snapshot assets are bundled under `src/new_repo_template/snapshot_assets/` and loaded at runtime via `importlib.resources`.
- Fresh `nurt new` generation now performs deterministic post-scaffold lockfile creation according to ownership: root outputs include `bun.lock`, while Python-enabled outputs generate `apps/python/uv.lock` from the lane-local Python metadata.
- The user-facing uv install workflow has been revalidated against current uv semantics via local git install smoke coverage: the correct command shape is `uv tool install git+...`, not the older `--from ... nurt` form.
- The local git-install contract implementation now pins the current commit SHA when exercising `git+file://...` installs in CI, avoiding fragile dependence on checkout-provided default-branch refs like `origin/HEAD` while preserving end-to-end validation of the git-based `nurt` install path.
- Managed core-tool versions continue to follow the latest-known-good baseline model rather than exact manifest pinning: after the most recent guardrail refresh, `turbo` now tracks `2.8.16`, while manifest specs remain caret-based and determinism continues to come from committed lockfiles plus the `Version Baseline Guardrail`.
- Governance/workflow assets are now part of the foundation scaffold baseline: fresh `nurt new` output writes bundled copies of `btca.config.jsonc`, `AGENTS.md`, `PROGRESS.md`, `scripts/RALPH.sh`, `docs/{archive,session-summaries,tasks,workflows}`, `.agent`, and `.opencode/command`, while template sync remains available for maintainer update flows.
- Shared infra config packages are now part of the generated monorepo baseline: `packages/typescript-config` provides reusable `base`, `react-app`, `node`, and `expo` presets, while `packages/eslint-config` provides the shared lint baseline consumed by the root `eslint.config.mjs`.
- Generated app/workspace wiring now depends on internal config packages using the Bun workspace protocol where appropriate: app manifests include `@generated/typescript-config` as an internal dev dependency, and generated tsconfigs extend the shared package paths rather than duplicating compiler-option baselines per app.
- Backend scaffold output now includes an explicit `apps/backend/tsconfig.json`, which brings the Convex workspace into the shared infra package model alongside web, desktop, mobile, and TV outputs.
- CI architecture now includes a dedicated foundation-baseline validation lane in addition to the cross-platform matrix, preset regression suite, and version guardrail. That lane generates a foundation-only workspace and verifies install/lint/typecheck/test behavior directly against scaffold output.
- CI trigger coverage now includes `merge_group` for merge-queue compatibility so required checks remain reportable beyond `push` and `pull_request` events.
- Release hardening has moved from docs-only design into secret-gated workflow implementation: `.github/workflows/release.yml` now builds unsigned template distributables by default and exposes optional macOS/Android signing-prep jobs behind `workflow_dispatch` + `enable_signing=true`, while acknowledging that repo-specific downstream app signing/build execution still belongs in generated-app repositories.
- Mobile scaffold architecture now includes explicit EAS iOS packaging baseline support via `apps/mobile/eas.json` and non-interactive iOS build scripts, so generated mobile repos start with a documented Expo/EAS packaging contract instead of requiring ad hoc setup.
- Release architecture now includes a secret-gated `iOS Packaging Preview` path that validates template-generated mobile packaging wiring on `macos-latest`, plus a `Publish Template Release` path that can create or update a draft GitHub release containing the template distribution bundle.
- Snapshot generation command path is implemented at `nurt template-assets snapshot` using manifest-driven source entries and metadata hashing.
- Scaffolded baseline sync is now explicit for shared repo files and Python lane files: bundled snapshot assets include `root_gitignore.txt` for repo root and `python_lane_python_version.txt` for Python-lane interpreter pinning, while Python-lane outputs keep `.python-version` as a lane-local file.
- Script-wrapper migration slice is complete for sync commands: `nurt tools sync` and `nurt template-assets sync` now call native Python operations in `src/new_repo_template/sync_ops.py`.
- Contract coverage now includes non-dry-run sync failure messaging for native `nurt` sync commands (tools sync simulated failure output and template-assets sync validation failures).
- Assistant-specific maintainer assets are intentionally excluded from the repository and sync surface: native template sync no longer copies them, and the legacy shell sync script no longer references them.
- Interactive `nurt new` now handles stdin-closure failure paths with deterministic remediation output instead of raw EOF tracebacks.
- Mixed-combo validation coverage now includes additional unsupported auth/target combinations in mixed presets.
- Required preset-combination matrix coverage is now implemented for all combinations defined in `docs/archive/plans/PLAN_2026-03-08_07-49-04_PM.md` Section 2.1, including both auth variants and all-target (python-inclusive) sanity passes.
- Root workspace scaffold now emits `package.json` and `turbo.json` at repository root for all outputs, with Bun workspaces (`apps/*`, `packages/*`) and Turbo-routed root scripts (`dev`, `build`, `test`, `lint`, `typecheck`).
- Root workspace contract coverage now verifies dry-run visibility and scaffolded workspace/task wiring in `tests/contracts/test_root_workspace_contract.py`.
- JS app targets scaffold workspace-local `package.json` manifests (`apps/web`, `apps/backend`, `apps/desktop`, `apps/mobile`, `apps/tv`) with target-aware script wiring.
- Bun workspace install viability coverage is now active in `tests/contracts/test_bun_workspace_install_contract.py` and verifies generated `web+backend` output supports both `bun install` and `bun install --frozen-lockfile`.
- Minimal selected-preset command-smoke coverage is now active in `tests/contracts/test_turbo_command_smoke_contract.py`, validating root script viability for `dev`, `build`, `test`, `lint`, and `typecheck` after install on generated `web+backend` output.
- Fullstack scaffold baseline now includes concrete framework file layout for `web+backend`: TanStack-style web routing/app entry files and Convex-style backend `http.ts`/`schema.ts` baseline files.
- Fullstack web scaffold now includes additional TanStack Start-style app shell/config files (`apps/web/app.config.ts`, `vite.config.ts`, `tsconfig.json`, `index.html`, `src/routeTree.gen.ts`, `src/styles.css`) to move beyond minimal route-only baseline output.
- Fullstack auth variant contract coverage is now concrete in `tests/contracts/test_fullstack_auth_wiring_contract.py`, with Clerk and Better Auth assertions on provider-aware backend auth config and frontend auth client/provider stubs.
- Shared-package integration is now part of the fullstack baseline for `web+backend` selections: scaffold emits `packages/shared` (`@generated/shared`) and wires both `apps/web` and `apps/backend` manifests via `workspace:*` dependencies.
- Convex backend smoke coverage now validates generated backend script viability for credentialless CLI help commands (`convex codegen --help`, `convex dev --help`) in `tests/contracts/test_convex_backend_smoke_contract.py`.
- Generated backend outputs now include `apps/backend/README.md` with cloud-first local Convex workflow guidance and auth decision alignment notes.
- Backend script model now separates credentialed local commands (`convex:dev`, `convex:codegen`) from CI-safe wrappers (`convex:*:smoke`), with `dev`/`test` mapped to smoke-safe commands for cross-platform CI determinism.
- Fullstack setup and auth decision flow are now documented in `docs/FULLSTACK_SETUP.md`.
- Version baseline metadata/workflow is implemented with `version-baseline.json` and native `nurt versions check/update` commands in `src/new_repo_template/version_baseline.py`.
- Version baseline workflow now includes lockfile lifecycle controls: update-time regeneration (with dry-run/summaries) and check-time lockfile presence validation.
- CI workflow wiring now enforces version/lockfile governance using `nurt versions check --check-lockfiles --check-latest`, sets up Bun on matrix runners, runs cross-platform script smoke contracts on native Linux/macOS/Windows, and includes a non-blocking advisory secret scan job.
- CI workflow now also includes top-level workflow concurrency cancellation (`cancel-in-progress: true`), dependency cache restoration for uv/Bun via `actions/cache@v4`, explicit TV HID/input contract execution in cross-platform smoke steps, and an explicit required preset-matrix contract step in guardrail flow.
- Branch-protection policy is now documented in `docs/BRANCH_PROTECTION.md` with required status checks aligned to the CI workflow job names and advisory-only secret scan handling.
- Preset-combination regression policy is now documented in `docs/REGRESSION_SUITE.md`, and CI includes a dedicated `Preset Regression Suite` job that runs required preset-matrix/auth/fullstack contract subsets.
- Dependency lifecycle governance is now documented in `docs/DEPENDENCY_UPGRADE_POLICY.md`, including cadence tiers, `workspace:*`/`^` range strategy, lockfile rules, and maintainer `nurt versions check/update` workflow.
- Optional signing design is now documented in `docs/OPTIONAL_SIGNING_PIPELINE.md`, with secret-name map and disabled-by-default enablement strategy.
- Manual release workflow scaffolding now includes `.github/workflows/release.yml` with `workflow_dispatch` and guarded signing path (`enable_signing` defaults to `false`), plus phased rollout criteria captured in `docs/RELEASE_CHECKLIST.md`.
- CI reliability hardening now explicitly protects scaffold env seed assets used for generated `.env.example` files: `.gitignore` unignores `src/new_repo_template/snapshot_assets/templates/env/*.env`, and security-baseline contracts assert these files exist and are not git-ignored.
- Installer script dry-run contracts now use explicit POSIX-shell resolution (`bash` preferred, `sh` fallback, skip when unavailable) to keep Windows full-suite CI behavior deterministic.
- Installer script dry-run shell contracts are explicitly POSIX-scoped for CI determinism and are skipped on Windows runners; Windows-required coverage remains focused on scaffold/runtime workflows.
- Updater tooling in `.template_scripts/update-opencode.sh` now manages GitHub CLI (`gh`) alongside existing core tools, with dry-run status-table visibility and OS/package-manager specific install/update flows.
- CI matrix execution model now uses non-Windows full-suite confidence lanes and a focused `windows-latest` critical-contract lane to keep native Windows validation intact while reducing runtime overhead.
- Repository hardening automation now includes `.template_scripts/configure-repo-protections.sh`, which applies branch-protection baseline controls (PR + required checks + linear history + conversation resolution + no force-push/delete), auto-detects the repo when `--repo` is omitted, defaults the target branch to `main` when `--branch` is omitted, and enables repository-level Dependabot security updates.
- Interactive TUI architecture now splits cleanly between UI-mode resolution/plain prompt fallback in `src/new_repo_template/interactive_ui.py` and the real Textual wizard implementation in `src/new_repo_template/interactive_tui.py`.
- Interactive wizard flow now begins with project-name entry instead of a welcome screen, uses Enter as the forward/confirm key, keeps `SelectionList` selection on Space, uses Escape for back-or-exit semantics, and exposes Ctrl+Q / Ctrl+C as explicit quit bindings.
- Visual snapshot adoption for the wizard was evaluated during closeout but deferred: the latest available `pytest-textual-snapshot` release (`1.1.0`) depends on `pytest<9`, which conflicts with the repository baseline `pytest>=9.0.2`, so layout confidence currently stays in semantic contract tests.
- Project BTCA resources now also include `textual`, `rich-docs`, and `pytest-textual-snapshot` so YELLOW research for the interactive wizard can stay grounded in official framework/testing sources.
- Desktop scaffold baseline is now concrete for `desktop` target: generated outputs include Electron entry files (`src/main.ts`, `src/preload.ts`, `src/renderer.ts`), `forge.config.ts`, `tsconfig.json`, `index.html`, and desktop README distribution notes.
- Desktop workspace scripts now include local Forge commands (`desktop:start`, `desktop:package`, `desktop:make`) and CI-safe smoke wrappers (`desktop:start:smoke`, `desktop:package:smoke`, `desktop:make:smoke`) wired through root task scripts for non-GUI determinism.
- Desktop Forge package/make scripts now include deterministic unsigned output locations (`out/unsigned/package`, `out/unsigned/make`) with parallel smoke-path assertions (`out/unsigned-smoke/*`) for contract-level validation.
- Shared workspace reuse is now applied across web+desktop scaffolds: `packages/shared` is generated for web-bearing presets, desktop manifests include `@generated/shared` for web+desktop selections, and renderer baseline wiring imports shared utility values.
- Desktop runtime smoke contract now executes start, package, and make smoke commands, completing milestone confidence for cross-platform dev/build/package behavior.
- Mobile and TV scaffold baselines are now concrete: generated `apps/mobile` and `apps/tv` outputs include Expo app entry/config files (`app.json`, `babel.config.js`, `index.js`, `App.tsx`, `tsconfig.json`) rather than package-manifest-only placeholders.
- TV plugin/config isolation is now explicit in scaffolded TV config: `apps/tv/app.json` includes `@react-native-tvos/config-tv`, while mobile config remains plugin-free.
- Mobile/TV workspace manifests now include Expo-oriented script surfaces and dependency baselines (`expo`, `react`, `react-native`, `expo-status-bar`, plus TV-specific `react-native-tvos` and `@react-native-tvos/config-tv`).
- TV Android build-profile baseline is now scaffolded as dedicated TV config: `apps/tv/eas.json` includes `development` + `preview` EAS profiles with internal APK Android settings, and TV workspace scripts include profile-specific Android build commands.
- TV HID/input baseline is now scaffolded as part of TV app output: `apps/tv/App.tsx` includes remote-primary focus/event starter wiring and generated TV outputs include `apps/tv/TV_INPUT_CHECKLIST.md` for keyboard/mouse/gamepad fallback validation steps.
- Mobile/TV setup documentation is now scaffolded in-app: generated output includes `apps/mobile/README.md` (mobile setup and CI-safe validation commands) and `apps/tv/README.md` (Android TV Emulator + NVIDIA Shield validation flow).
- TV input checklist guidance is now expanded with explicit Android TV Emulator and NVIDIA Shield validation sections while preserving remote-primary plus keyboard/mouse/gamepad fallback criteria.
- Template-level setup and caveat guidance for this lane is now captured in `docs/MOBILE_TV_SETUP.md` and linked from `README.md`.
- Mobile/TV runtime smoke coverage is now active in `tests/contracts/test_mobile_tv_runtime_smoke_contract.py`: generated `mobile+tv` scaffold installs with Bun and app-local `lint`/`typecheck`/`test` scripts execute in CI-safe mode for both targets.
- Mobile/TV workspace script model now maps baseline commands to explicit smoke wrappers (`mobile|tv:lint:smoke`, `mobile|tv:typecheck:smoke`, `mobile|tv:test:smoke`) with scaffolded app-local smoke tests (`smoke.test.js`) for deterministic `test` viability.
- TV scaffold output now includes `apps/tv/TV_VALIDATION_LOG.md` to record emulator and Shield execution metadata/results alongside checklist completion.
- Generated TV Android run flow now includes a compatibility patch step: `apps/tv/scripts/patch-android-wrapper.mjs` pins the generated Android wrapper to Gradle `8.14.3`, and `tv:android` executes with community autolinking enabled (`EXPO_USE_COMMUNITY_AUTOLINKING=1`) after deterministic prebuild.
- Generated Expo mobile/TV TypeScript manifests now explicitly carry template-required dev tooling (`babel-preset-expo`, `@types/react`), and generated TV manifests additionally pin `@react-native-community/cli` plus `@react-native-community/cli-platform-android` so local Android autolinking produces `project.android.packageName` correctly.
- Generated TV starter UI is now intentionally focus-first rather than low-level event-hook-driven: it uses `Pressable` items with `hasTVPreferredFocus`, `onFocus`, and `onPress` to provide a stable Android TV starter surface for manual remote-primary and fallback-input validation.
- Local Android TV emulator evidence now confirms the generated TV baseline supports initial focus placement, deterministic D-pad progression across the starter rail, select stability, back-to-home behavior with relaunch focus recovery, and pointer/tap activation for the same controls.
- Physical NVIDIA Shield validation now confirms the generated TV baseline launches successfully on-device, supports remote-primary control, exits cleanly via Back, relaunches correctly, and accepts mouse and gamepad fallback input on the same focus-first UI.
- Keyboard fallback was not directly exercised during the Shield run because no keyboard was available; tracker closeout for that final checkbox was accepted by explicit user direction.
- M5 milestone closeout state is now explicit in the archived planning record: required PR checks were confirmed green and the remaining M5 DoD gate in `docs/archive/plans/PLAN_2026-03-08_07-49-04_PM.md` is checked complete.
- The maintainer OpenCode updater path now distinguishes install vs upgrade semantics: `.template_scripts/update-opencode.sh` runs `opencode upgrade` when the CLI is already present in `PATH`, while retaining the installer curl flow only for first-time bootstrap.

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
  - Contract intent: non-interactive `--dry-run` foundation scaffold path succeeds, reports monorepo shape (`apps`, `packages`, `.gitignore`), and writes no files.
- `tests/contracts/test_python_lane_contract.py`
  - Contract intent: Python target dry-run/write flows keep Python metadata exclusively inside `apps/python` (`pyproject.toml` and `.python-version`), keep root Python metadata absent, and baseline lane commands execute for both preferred and compatibility sync flows (`uv sync --group dev`, `uv sync --extra dev`, `uv run pytest`, `uv run ruff check .`, `uv run mypy src`).
- `tests/contracts/test_cli_validation_and_python_commands_contract.py`
  - Contract intent: deterministic CLI validation failures (including missing `--no-interactive` across foundation/python/web+backend/mobile+tv modes, missing required args, and invalid choice handling) and Python lane baseline command documentation generation.
- `tests/contracts/test_failure_atomicity_contract.py`
  - Contract intent: simulated mid-generation failure leaves no partial output at the final scaffold path.
- `tests/contracts/test_target_matrix_and_auth_contract.py`
  - Contract intent: multi-target validation/auth rules, duplicate target rejection, unsupported mixed-combo auth validation, auth-variant env placeholders, minimal auth wiring placeholders, and separate mobile/TV app scaffolding behavior.
- `tests/contracts/test_required_preset_matrix_contract.py`
  - Contract intent: full required preset matrix from `docs/archive/plans/PLAN_2026-03-08_07-49-04_PM.md` Section 2.1 scaffolds successfully with root Python metadata absent, expected target directories, python-lane metadata inclusion when selected, and auth-variant wiring assertions.
- `tests/contracts/test_root_workspace_contract.py`
  - Contract intent: root workspace config files (`package.json`, `turbo.json`) are present in dry-run/scaffold output, include baseline cross-platform script/task wiring for `dev`, `build`, `test`, `lint`, and `typecheck`, and mirror the foundation governance/agent asset baseline (`btca.config.jsonc`, `AGENTS.md`, `PROGRESS.md`, `scripts/RALPH.sh`, `docs/tasks`, `docs/workflows`, `.agent`, and `.opencode/command`).
- `tests/contracts/test_bun_workspace_install_contract.py`
  - Contract intent: JS workspace manifests are scaffolded for `web+backend` outputs and generated workspace installs remain viable via `bun install` and `bun install --frozen-lockfile`.
- `tests/contracts/test_turbo_command_smoke_contract.py`
  - Contract intent: selected minimal JS preset passes root Turbo-routed command scripts (`dev`, `build`, `test`, `lint`, `typecheck`) after Bun install.
- `tests/contracts/test_fullstack_auth_wiring_contract.py`
  - Contract intent: `web+backend` scaffold outputs include concrete TanStack/Convex baseline files, expanded web app shell/config files, shared-package wiring, and auth-variant-specific frontend/backend wiring for both Clerk and Better Auth, with dry-run path visibility.
- `tests/contracts/test_desktop_scaffold_contract.py`
  - Contract intent: `desktop` scaffold outputs include concrete Electron Forge baseline files and scripts/dependencies, plus dry-run path visibility for desktop framework wiring.
- `tests/contracts/test_desktop_runtime_smoke_contract.py`
  - Contract intent: generated `desktop` workspace installs cleanly, executes Forge start/package smoke commands, validates root `dev`/`build` desktop smoke paths, and asserts deterministic unsigned output path wiring.
- `tests/contracts/test_mobile_tv_scaffold_contract.py`
  - Contract intent: generated `mobile` and `tv` scaffold outputs include concrete Expo baseline files, TV plugin/config isolation is enforced to `apps/tv`, and `mobile+tv` dry-run output reports distinct app wiring paths.
- `tests/contracts/test_tv_android_build_profile_contract.py`
  - Contract intent: generated `tv` scaffold includes Android EAS build profile config (`apps/tv/eas.json`), profile-aware TV Android build scripts, and dry-run visibility for TV build-profile output paths.
- `tests/contracts/test_tv_input_hid_contract.py`
  - Contract intent: generated `tv` scaffold includes remote-primary focus wiring markers in app baseline, includes a TV HID checklist covering keyboard/mouse/gamepad fallback validation, and reports checklist path in dry-run planning output.
- `tests/contracts/test_mobile_tv_setup_docs_contract.py`
  - Contract intent: generated `mobile` and `tv` scaffolds include setup/validation README docs, TV docs explicitly cover Android TV Emulator and NVIDIA Shield flow, and mobile+tv dry-run output reports README paths.
- `tests/contracts/test_mobile_tv_runtime_smoke_contract.py`
  - Contract intent: generated `mobile+tv` scaffold supports Bun install and app-local `lint`/`typecheck`/`test` command execution in CI-safe mode for both targets, with deterministic script wiring assertions.
- `tests/contracts/test_convex_backend_smoke_contract.py`
  - Contract intent: generated backend workspace includes local Convex commands (`convex:codegen`, `convex:dev`), CI-safe smoke wrappers (`convex:*:smoke`), smoke-safe `dev`/`test` execution, and backend README cloud-dev/auth flow guidance.
- `tests/contracts/test_security_baseline_contract.py`
  - Contract intent: root `.gitignore` exactly matches the template-root baseline, and per-target `.env.example` placeholder generation remains intact.
- `tests/contracts/test_installer_scripts_dry_run_contract.py`
  - Contract intent: non-destructive `--dry-run` behavior for installer/updater scripts and turborepo updater visibility.
- `tests/contracts/test_nurt_cli_contract.py`
  - Contract intent: `nurt` command routing, new-project dry-run parity, project-name prompting/normalization when omitted, startup update notice behavior, dry-run safety for `update`/`tools sync`/`template-assets sync`, deterministic non-dry-run failure messaging for native sync paths, and deterministic interactive stdin-failure remediation.
- `tests/contracts/test_interactive_tui_contract.py`
  - Contract intent: the real Textual wizard supports project-name entry/normalization, keyboard-driven target multi-select, `foundation` exclusivity, backend-driven explicit auth (including `none`), Escape/Ctrl+Q navigation semantics, wide-vs-compact layout invariants, and resolved-plan handoff on review confirmation.
- `tests/contracts/test_snapshot_assets_contract.py`
  - Contract intent: packaged snapshot template availability and deterministic snapshot metadata generation for the shared root `.gitignore` baseline and the Python-lane `.python-version` baseline.
- `tests/contracts/test_version_baseline_contract.py`
  - Contract intent: codified version baseline metadata validation and maintainer update/check workflow behavior (including stale detection, lockfile regeneration/check guardrails, and dry-run non-destructive updates).
- `tests/contracts/test_ci_versions_guardrail_contract.py`
  - Contract intent: CI workflow includes required version guardrail command, cross-platform matrix smoke-check wiring (including desktop runtime smoke contract), and advisory secret-scan job presence.
- `tests/contracts/test_branch_protection_guidance_contract.py`
  - Contract intent: branch-protection policy docs include required status checks aligned to CI job names, advisory secret-scan treatment, and README discoverability link.
- `tests/contracts/test_preset_regression_suite_contract.py`
  - Contract intent: CI includes a dedicated preset-regression job with required matrix/auth/fullstack contract commands, and regression policy docs are present and linked from README.
