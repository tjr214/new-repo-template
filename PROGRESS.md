# Development Progress

**Last Updated:** 2026-03-13 03:50:26 PM
**Current Phase:** manifest-driven foundation source-of-truth closeout

## Previous Cycle Archives

- `docs/archive/plans/PLAN_2026-03-12_06-50-03_PM.md`
- `docs/archive/plans/PLAN_2026-03-12_05-15-50_PM.md`
- `docs/archive/plans/PLAN_2026-03-12_02-32-23_PM.md`
- `docs/archive/plans/PLAN_2026-03-08_07-49-04_PM.md`
- `docs/archive/plans/PROGRESS_2026-03-08_07-49-04_PM.md`

---

## Completed

- [x] Archived the previous root `PLAN.md` and `PROGRESS.md` trackers.
- [x] Reset the root trackers as stubs for the next endeavour.
- [x] Synced scaffolded root `.gitignore` output back to the full template-root baseline instead of the stale bundled subset.
- [x] Removed scaffolded root `.python-version` and root `pyproject.toml` so Python metadata now lives only under `apps/python`.
- [x] Moved generated Python lockfile placement from root `uv.lock` to `apps/python/uv.lock` while keeping root `bun.lock` generation for the monorepo workspace.
- [x] Updated bundled snapshot assets/manifests and contract coverage for the lane-only Python metadata model.
- [x] Added the foundation governance baseline to scaffold output: `btca.config.jsonc`, `AGENTS.md`, `PROGRESS.md`, `scripts/RALPH.sh`, `docs/{archive,session-summaries,tasks,workflows}`, `.agent`, and `.opencode/command`.
- [x] Mirrored the new foundation governance assets into bundled snapshot templates and expanded scaffold/snapshot contracts to enforce their presence.
- [x] Restored Python lane compatibility for legacy `uv sync --extra dev` flows while keeping the preferred `[dependency-groups].dev` baseline intact.
- [x] Reproduced the PR-only `Version Baseline Guardrail` failure, ran the YELLOW phase with `btca ask -r bun -r turborepo`, and confirmed the expected fix path is a within-major Turbo refresh plus lockfile revalidation.
- [x] Refreshed the managed Turbo baseline from `2.8.14` to `2.8.16` in the baseline metadata, generated root package template, and contract fixtures.
- [x] Revalidated the version guardrail locally with `uv run nurt versions check --check-lockfiles --check-latest`.
- [x] Verified the full repository test suite with `uv run pytest` (130 passed).
- [x] Archived the previous root `PLAN.md` to `docs/archive/plans/PLAN_2026-03-12_02-32-23_PM.md` and started a new interactive-TUI implementation plan.
- [x] Added project BTCA resources for `textual`, `rich-docs`, and `pytest-textual-snapshot`, then synced `docs/BTCA_RESOURCES.md`.
- [x] Ran the new YELLOW research pass, including `btca status`, `btca resources`, and `btca ask` lookups for Textual wizard architecture, app-result handoff, and testing strategy.
- [x] Added RED/GREEN contract coverage for the real Textual wizard in `tests/contracts/test_interactive_tui_contract.py`.
- [x] Implemented the first Textual wizard slice in `src/new_repo_template/interactive_tui.py` with direct target multi-select, conditional auth, live summary, review/confirm, and CLI handoff wiring in `src/new_repo_template/nurt_cli.py`.
- [x] Hardened UI-mode resolution so explicit rich mode falls back to plain prompts when the session is not running in an interactive terminal.
- [x] Revalidated the repository after the interactive-TUI slice with `uv run pytest` (133 passed).
- [x] Completed the BLUE hardening pass for `src/new_repo_template/interactive_tui.py` with a typed `WizardState`, centralized step transitions, refined review/context copy, and explicit responsive compact-mode layout behavior for narrow terminals and `80x24` sessions.
- [x] Expanded interactive coverage for stale-auth clearing, rich-mode no-TTY fallback, and wide-vs-compact layout invariants in `tests/contracts/test_interactive_tui_contract.py` and `tests/contracts/test_nurt_cli_contract.py`.
- [x] Evaluated `pytest-textual-snapshot` adoption during closeout but intentionally did not add it because the latest available release (`1.1.0`) requires `pytest<9`, which conflicts with the repository baseline `pytest>=9.0.2`.
- [x] Revalidated the repository after the interactive-TUI closeout with `uv run pytest` (137 passed).
- [x] Added a follow-up wizard slice so `nurt new` can omit the positional project name, prompt for it interactively, and normalize it into the final kebab-case output directory before scaffold handoff.
- [x] Removed the superfluous welcome step and replaced it with a project-name entry step in `src/new_repo_template/interactive_tui.py`, while keeping the wizard summary/output path visible as the name resolves.
- [x] Changed auth gating from `web+backend` to `backend` across CLI and scaffold validation, and added an explicit `none` auth path for both interactive and non-interactive flows.
- [x] Updated keyboard behavior so Enter advances/confirms, Escape goes back or exits from the first step, Ctrl+Q and Ctrl+C quit, and the friendly cancel copy now reads `Interactive wizzard cancelled. Maybe next time!`.
- [x] Widened the scaffold summary pane slightly and expanded contract coverage for omitted project-name flow, backend-only auth, Enter/Escape/Ctrl+Q behavior, and the updated cancel message.
- [x] Revalidated the repository after the follow-up slice with `uv run pytest` (143 passed).
- [x] Updated the scaffold summary output rendering so long output paths wrap across multiple lines instead of truncating in the right-hand summary pane, and revalidated the interactive contract coverage afterward.
- [x] Fixed the project-name input stability issue in `src/new_repo_template/interactive_tui.py` by stopping full wizard refresh/refocus behavior on every `Input.Changed` event and replacing it with targeted live summary/output-path updates.
- [x] Updated the Textual wizard flow so the project-name step exists only when the project name is missing; `nurt new <project-name>` now starts directly on target selection and Escape exits from that first real step.
- [x] Expanded interactive contract coverage for rapid project-name typing stability and conditional skipping of the project-name step when the CLI already provided the name.
- [x] Revalidated the repository after the stability fix with `uv run pytest` (146 passed).
- [x] Added `.gitleaksignore` coverage for the branch-specific documentation false positive (`PROGRESS.md` fingerprint `1987fd9e30da377670eae257b23b5f1f778d85e2:PROGRESS.md:generic-api-key:43`) so the advisory secret-scan PR check reports cleanly without masking real findings.
- [x] Split the mixed workflow guidance in `README.md` so `nurt` usage stays in the root README while BMAD and RALPH now have dedicated guides at `README.BMAD-GUIDE.md` and `README.RALPH.md`.
- [x] Synced the documentation split across `docs/LIVING_DOCS.md`, `docs/ARCHITECTURE.md`, and a new session summary.
- [x] Archived the completed root `PLAN.md` to `docs/archive/plans/PLAN_2026-03-12_05-15-50_PM.md`.
- [x] Reset root `PLAN.md` as a fresh next-cycle stub with YELLOW/RED/GREEN/BLUE and documentation-sync sections.
- [x] Synced the plan reset across `PROGRESS.md`, `docs/LIVING_DOCS.md`, `docs/ARCHITECTURE.md`, and `docs/session-summaries/SESSION_84_SUMMARY.md`.
- [x] Ran the new YELLOW phase for the post-create automation slice: reread the relevant CLI/TUI/sync/version files, reviewed the legacy updater scripts for behavioral parity, ran `btca status`, and used `btca ask` for Textual status-table/log-layout, background subprocess, and external-TUI handoff guidance.
- [x] Added RED coverage for the new optional-install wizard state, post-create pipeline ordering, BMAD runner, reusable tool-sync runner, and the new core-tools updater TUI.
- [x] Extended `nurt new` so both the Textual wizard and plain interactive fallback now collect optional core-tools and BMAD decisions, while non-interactive CLI usage can drive the same behavior with explicit flags.
- [x] Added native post-create orchestration in `src/new_repo_template/post_create.py` so generated projects now follow the requested lifecycle: optional BMAD -> lockfiles/revalidation -> `git init` -> `git add .` -> `git commit -m "Initial Commit"` -> optional core-tools updater.
- [x] Added a dedicated BMAD runner in `src/new_repo_template/bmad_runner.py` plus a direct `nurt bmad sync` command for standalone BMAD install/update flows.
- [x] Refactored the native core-tools updater into `src/new_repo_template/tool_sync_runner.py` and `src/new_repo_template/tool_sync_tui.py`, bringing `nurt tools sync` to native parity for `uv`, `bun`, `turbo`, `opencode`, `btca`, `gh`, and `ripgrep` with a persistent Textual status table and live scrolling log output in rich TTY sessions.
- [x] Revalidated the slice with targeted contract coverage and the full repository test suite via `uv run pytest` (158 passed).
- [x] Polished the `nurt tools sync` TUI so the table uses slightly wider Tool/Status columns and the Details column stretches to absorb the remaining width responsively.
- [x] Replaced the plain-text log pane with ANSI-aware Rich rendering so streamed updater output now preserves full color/styling, avoids raw-escape corruption in the scrollable transcript, and stays close to the original legacy updater presentation.
- [x] Added follow-up contracts for RichLog usage, ANSI rendering preservation, and responsive table-width behavior, then revalidated with `uv run pytest` (160 passed) and `uv run ruff check src/new_repo_template tests/contracts`.
- [x] Removed the legacy updater shell scripts `.template_scripts/update-opencode.sh` and `.template_scripts/update-bmad-method.sh` now that `nurt tools sync` and `nurt bmad sync` are the supported native paths.
- [x] Updated the legacy `install.sh` maintainer path to call native repo-local `nurt` commands instead of the deleted shell updaters, while preserving dry-run visibility and setup flow.
- [x] Removed obsolete updater-script contract coverage, updated remaining installer dry-run contracts to assert native `nurt` command usage, and kept the protections/template-maintenance script coverage intact.
- [x] Archived the completed root `PLAN.md` and reset `PLAN.md` to a fresh next-cycle stub, then synced the reset across `PROGRESS.md`, `docs/LIVING_DOCS.md`, `docs/ARCHITECTURE.md`, and a new session summary.
- [x] Renamed the native sync CLI shape from `nurt <target> sync` to `nurt sync <target>` for `tools`, `bmad`, and `template-assets`, while preserving a standalone `nurt template-assets` maintenance utility path.
- [x] Updated installer wiring, TUI labeling, sync-facing output strings, current docs, and contract coverage to the new `nurt sync ...` command order, then revalidated with `pytest tests/contracts/test_nurt_cli_contract.py tests/contracts/test_installer_scripts_dry_run_contract.py` (24 passed).
- [x] Ran the YELLOW pass for the foundation-governance expansion slice by rereading scaffold/snapshot/contracts/live-doc files, checking `btca status`, and using `btca ask` to confirm that explicit manifest-driven scaffold allowlists remain the safer contract than directory auto-copying for deterministic package-resource output.
- [x] Expanded the foundation lane governance baseline so generated repos now also include `PLAN.md`, `README.md`, `README.BMAD-GUIDE.md`, `README.RALPH.md`, `scripts/configure-repo-protections.sh`, `scripts/synthetic-quotas.sh`, `scripts/task-template-schema.json`, `scripts/validate_template.py`, `scripts/visualize_plan.py`, and empty `docs/archive/plans` plus `docs/archive/progress` directories.
- [x] Updated the bundled snapshot manifests/assets to mirror the expanded foundation file set, with scaffolded root `PLAN.md` and `PROGRESS.md` sourced from `docs/markdown-templates/{PLAN,PROGRESS}.template.md`.
- [x] Revalidated the slice with `uv run pytest tests/contracts/test_root_workspace_contract.py tests/contracts/test_snapshot_assets_contract.py tests/contracts/test_nurt_cli_contract.py` (24 passed) and `uv run ruff check src/new_repo_template tests/contracts`.
- [x] Renamed the maintainer validation/metadata-refresh command from `nurt template-assets snapshot` to `nurt template-assets validate`, updated the CLI/help/dry-run messaging to match, and documented `src/new_repo_template/snapshot_assets/templates/` as the canonical bundled-template source of truth behind the repo-root symlink aliases.
- [x] Fixed the snapshot Python-version alias mismatch in `src/new_repo_template/snapshot_assets/source_manifest.json` and documented the canonical-store-plus-alias-entrypoints model, including `templates-content-store-symlink` plus the readable root alias files used by the maintainer manifest.
- [x] Added `docs/markdown-templates/ARCHITECTURE.template.md` as a reusable version of the live architecture document structure and synced that new documentation asset across `PROGRESS.md`, `docs/LIVING_DOCS.md`, `docs/ARCHITECTURE.md`, and `docs/session-summaries/SESSION_93_SUMMARY.md`.
- [x] Added `docs/markdown-templates/LIVING_DOCS.template.md` as a reusable version of the live living-doc structure and synced that new documentation asset across `PROGRESS.md`, `docs/LIVING_DOCS.md`, `docs/ARCHITECTURE.md`, and `docs/session-summaries/SESSION_94_SUMMARY.md`.
- [x] Expanded the foundation scaffold and bundled snapshot manifests to include `docs/ARCHITECTURE.md`, `docs/LIVING_DOCS.md`, and the mirrored `docs/markdown-templates/` directory with both tracked template files (`PLAN.template.md`, `PROGRESS.template.md`).
- [x] Revalidated the docs-baseline follow-up with `uv run pytest tests/contracts/test_root_workspace_contract.py tests/contracts/test_snapshot_assets_contract.py` (5 passed) and `uv run ruff check src/new_repo_template tests/contracts`.
- [x] Expanded the foundation scaffold and bundled snapshot manifests to include `.github/`, `.github/workflows/`, `.github/workflows/ci.yml`, and `.github/workflows/release.yml` as part of the deterministic baseline.
- [x] Added a guardrail note to `src/new_repo_template/snapshot_assets/source_manifest.json` that `templates-snapshot-files/...` alias sources must never be substituted with direct paths for snapshot-managed entries.
- [x] Revalidated the `.github` baseline follow-up with `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."`, `uv run pytest tests/contracts/test_root_workspace_contract.py tests/contracts/test_snapshot_assets_contract.py` (5 passed), and `uv run ruff check src/new_repo_template tests/contracts`.
- [x] Ran the YELLOW pass for the `nurt new` completion-polish slice by rereading `src/new_repo_template/{nurt_cli.py,post_create.py,interactive_tui.py,interactive_ui.py}`, the current `nurt`/post-create/Textual contracts, `docs/{LIVING_DOCS.md,ARCHITECTURE.md}`, and using `btca ask -r rich-docs` to confirm the recommended Rich composition for a polished terminal completion summary.
- [x] Updated the interactive BMAD decision so plain-prompt fallback and the Textual wizard both default to `Yes` when the user accepts the BMAD step without changing it.
- [x] Added a Rich `Setup Complete` overview for successful non-dry-run `nurt new` runs, including project details, post-create accomplishments, and an explicit closing message that the flow is changing into the new project directory.
- [x] Updated successful `nurt new` completion to change the CLI process working directory to the generated project path after printing the completion overview.
- [x] Revalidated the slice with `uv run pytest tests/contracts/test_nurt_cli_contract.py tests/contracts/test_interactive_tui_contract.py tests/contracts/test_post_create_contract.py` (39 passed) and `uv run ruff check src/new_repo_template tests/contracts`; a broader `uv run pytest` pass still reports 5 unrelated repository-baseline failures because `install.sh` and `.template_scripts/configure-repo-protections.sh` are absent and `README.md` no longer contains the placeholder git-install command expected by `tests/contracts/test_nurt_install_contract.py`.
- [x] Corrected the new completion handoff copy so `nurt new` now explicitly instructs the user to run `cd <project-name>` instead of implying that the CLI can move the parent shell into the generated directory.
- [x] Removed the ineffective process-local `os.chdir(...)` step from successful `nurt new` completion and revalidated the updated handoff behavior with `uv run pytest tests/contracts/test_nurt_cli_contract.py tests/contracts/test_post_create_contract.py` (25 passed) plus `uv run ruff check src/new_repo_template tests/contracts`.
- [x] Ran a YELLOW pass for stale contract cleanup by rereading the failing installer/install-doc contracts, current README and branch-protection guidance/script paths, checking `btca status` / `btca resources`, and using `btca ask -r rich-docs` to confirm the README should continue to show exact copyable shell commands.
- [x] Replaced stale repository-baseline expectations in `tests/contracts/test_installer_scripts_dry_run_contract.py`: the suite now asserts the removed root `install.sh` remains absent, treats `scripts/configure-repo-protections.sh` as the supported maintainer script path, and keeps the protections dry-run behavior under contract against that live script.
- [x] Relaxed `tests/contracts/test_nurt_install_contract.py` so README coverage now expects a concrete GitHub `uv tool install git+https://github.com/...` command instead of the old `<org>/<repo>` placeholder, while still rejecting the obsolete `uv tool install --from` syntax.
- [x] Revalidated the refreshed contract slice with `uv run pytest tests/contracts/test_installer_scripts_dry_run_contract.py tests/contracts/test_nurt_install_contract.py` (7 passed) and `uv run pytest` (161 passed).
- [x] Ran a repo-wide brittleness review of the remaining contract suite, including grep-based scans for exact wording/path assertions, an explore-agent pass ranking the most drift-prone tests, and a `btca ask -r textual` lookup confirming interaction/state assertions are generally more stable than layout/copy-coupled checks as terminal UI flows evolve.
- [x] Reduced drift risk in `tests/contracts/test_root_workspace_contract.py` by replacing the large hardcoded dry-run file list with representative governance markers and by validating mirrored governance directories through dynamic source-directory parity instead of a fixed per-file enumeration.
- [x] Reduced drift risk in `tests/contracts/test_branch_protection_guidance_contract.py` by deriving required status-check names from `.github/workflows/ci.yml` rather than pinning a duplicated static list in the test, and synced `docs/BRANCH_PROTECTION.md` plus live docs to the real `scripts/configure-repo-protections.sh` path.
- [x] Revalidated the brittleness-hardening follow-up with `uv run pytest tests/contracts/test_root_workspace_contract.py tests/contracts/test_branch_protection_guidance_contract.py` (5 passed) and `uv run pytest` (161 passed).
- [x] Ran a follow-up YELLOW pass for the next three stale-prone areas by rereading `tests/contracts/test_nurt_cli_contract.py`, `tests/contracts/test_cli_validation_and_python_commands_contract.py`, `tests/contracts/test_mobile_tv_setup_docs_contract.py`, the backing CLI/source templates, and using `btca ask -r textual` to confirm semantic markers and state outcomes are the more stable default for evolving terminal flows.
- [x] Hardened `tests/contracts/test_nurt_cli_contract.py` with shared semantic-plan helpers, looser command/prose checks for update and BMAD dry-runs, and manifest-derived validation expectations for `template-assets validate` instead of a few hardcoded bundled-template filenames.
- [x] Hardened `tests/contracts/test_cli_validation_and_python_commands_contract.py` so the Python README contract asserts the presence of setup/test/lint/typecheck guidance semantically (`uv sync`, `pytest`, `ruff`, `mypy`) instead of pinning every exact command line.
- [x] Hardened `tests/contracts/test_mobile_tv_setup_docs_contract.py` so mobile/TV setup coverage now checks semantic setup/validation markers and fallback-input coverage across README/checklist/log files instead of overfitting exact wording.
- [x] Revalidated the three-file brittleness pass with `uv run pytest tests/contracts/test_nurt_cli_contract.py tests/contracts/test_cli_validation_and_python_commands_contract.py tests/contracts/test_mobile_tv_setup_docs_contract.py` (34 passed) and `uv run pytest` (161 passed).
- [x] Investigated the live merge blocker on PR #6 and confirmed the base branch currently enforces `required_approving_review_count=1` with `enforce_admins=true`, which blocks author-only repos from merging even after all required checks pass.
- [x] Updated `scripts/configure-repo-protections.sh` so PR-based merging remains required but approval count now defaults to `0`, and team repos can opt into stricter review policy with `--required-approvals <n>`.
- [x] Updated `docs/BRANCH_PROTECTION.md` and the branch-protection contract suite to document the solo-friendly default plus explicit team override.
- [x] Revalidated the branch-protection slice with `uv run pytest tests/contracts/test_installer_scripts_dry_run_contract.py tests/contracts/test_branch_protection_guidance_contract.py`.
- [x] Ran a YELLOW pass for the missing foundation OpenCode PR-command slice by rereading `src/new_repo_template/{scaffold.py,snapshot_assets_loader.py,snapshot_builder.py,nurt_cli.py}`, the source/runtime snapshot manifests, the foundation scaffold contracts, and using `btca ask -r bun` to confirm the repo should continue using an explicit manifest/allowlist model for deterministic packaged template assets.
- [x] Expanded RED coverage so foundation dry-run output explicitly mentions `.opencode/command/repo-gh-make-n-merge-PR.md`, and snapshot contract coverage now asserts source-manifest foundation `.opencode/command` entries stay aligned with the packaged runtime manifest.
- [x] Updated the foundation scaffold allowlist and template-file mapping in `src/new_repo_template/scaffold.py` so generated repos now include `.opencode/command/repo-gh-make-n-merge-PR.md`.
- [x] Synced the packaged runtime manifest in `src/new_repo_template/snapshot_assets/manifest.json` so the new command is part of the loadable bundled-template set.
- [x] Revalidated the slice with `uv run pytest tests/contracts/test_root_workspace_contract.py tests/contracts/test_snapshot_assets_contract.py` (6 passed).
- [x] Extended `src/new_repo_template/snapshot_assets/source_manifest.json` to keep the CRITICAL maintenance note intact while adding manifest-declared foundation `empty_directories` for scaffold-only directories.
- [x] Added `src/new_repo_template/foundation_manifest.py` so foundation scaffold file mappings, dry-run path reporting, empty-directory creation, and runtime snapshot-manifest generation all derive from `src/new_repo_template/snapshot_assets/source_manifest.json`.
- [x] Refactored `src/new_repo_template/scaffold.py` to replace hard-coded foundation governance file/path allowlists with manifest-derived foundation data.
- [x] Refactored `src/new_repo_template/snapshot_builder.py` and `src/new_repo_template/nurt_cli.py` so `nurt template-assets validate` regenerates `src/new_repo_template/snapshot_assets/manifest.json`, refreshes metadata, and reports both outputs in dry-run and real execution flows.
- [x] Expanded contract coverage in `tests/contracts/test_root_workspace_contract.py`, `tests/contracts/test_snapshot_assets_contract.py`, and `tests/contracts/test_nurt_cli_contract.py` to guard manifest-driven empty directories, runtime manifest regeneration, and validate-command reporting.
- [x] Regenerated bundled snapshot artifacts with `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."`.
- [x] Revalidated the targeted manifest slice with `uv run pytest tests/contracts/test_root_workspace_contract.py tests/contracts/test_snapshot_assets_contract.py tests/contracts/test_nurt_cli_contract.py` (27 passed).
- [x] Revalidated the repository with `uv run pytest` (164 passed) and `uv run ruff check src/new_repo_template tests/contracts`.

## Next Up

- [ ] Optional follow-up: revisit `pytest-textual-snapshot` if an upstream release adds compatibility with the repository's `pytest>=9` baseline.
