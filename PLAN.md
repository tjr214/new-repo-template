# New Project Post-Create Automation + Installer TUI Slice

**Last Updated:** 2026-03-12 05:57:15 PM
**Status:** Planned
**Previous Cycle Archive:** `docs/archive/plans/PLAN_2026-03-12_05-15-50_PM.md`
**Previous Cycle Summary:** `docs/session-summaries/SESSION_84_SUMMARY.md`

---

## Goal

Extend the `nurt` new-project flow so the wizard and CLI can optionally run BMAD installation before repo initialization, create the initial git repository and commit for every generated project, and optionally launch a native `nurt` core-tools updater TUI after the initial commit, while also exposing direct CLI entrypoints for both the core-tools updater and BMAD updater flows.

---

## YELLOW

- [ ] Reread `src/new_repo_template/nurt_cli.py`, `src/new_repo_template/interactive_tui.py`, `src/new_repo_template/interactive_ui.py`, `src/new_repo_template/sync_ops.py`, and `src/new_repo_template/version_baseline.py` before editing.
- [ ] Reread `.template_scripts/update-opencode.sh`, `.template_scripts/update-bmad-method.sh`, `tests/contracts/test_nurt_cli_contract.py`, `tests/contracts/test_interactive_tui_contract.py`, and any installer-related contract files before editing.
- [ ] Reread `PLAN.md`, `PROGRESS.md`, `docs/LIVING_DOCS.md`, and `docs/ARCHITECTURE.md` before editing.
- [ ] Run `btca status` and use `btca ask` for Textual guidance on `DataTable` plus live log layouts, worker-driven subprocess streaming, and clean external-TUI handoff patterns for the BMAD installer.
- [ ] Confirm the exact lifecycle and preserve it through implementation: scaffold -> optional BMAD -> lockfiles/revalidation -> `git init` -> `git add .` -> `git commit -m "Initial Commit"` -> optional core-tools updater.
- [ ] Confirm the implementation scope stays centered on native `nurt` flows (`nurt new`, tools updater command, BMAD updater command), with legacy shell scripts treated as behavioral references unless follow-up work is explicitly needed.

## RED

- [ ] Add CLI contract coverage for the new `nurt new` option flow, including wizard-selected and flag-selected BMAD/core-tools choices, lifecycle ordering, and deterministic dry-run output.
- [ ] Add or extend Textual wizard contracts so the two new yes/no sections appear in the right order, participate in review state, and resolve correctly for both project-name-supplied and project-name-omitted flows.
- [ ] Add contracts for post-create orchestration, including success and failure paths for BMAD install, lockfile generation/revalidation, git init/add/commit, and post-commit core-tools updating.
- [ ] Add contracts for the native core-tools updater engine and TUI, covering persistent status-table updates, scrolling log output, dry-run planning, success/failure summaries, and non-interactive fallback behavior.
- [ ] Add contracts for the BMAD updater command path, including clean handoff to the external installer/TUI and deterministic error propagation when the installer command fails or is unavailable.

## GREEN

- [ ] Add a focused post-create orchestration layer so `handle_new()` coordinates the lifecycle without absorbing all implementation details directly.
- [ ] Update the wizard and plain interactive flow to ask `Do you want to install/update the core set of tools?` and `Do you want to install the BMAD Method?`.
- [ ] Add matching CLI flags/options so non-interactive usage can drive the same two decisions without the wizard.
- [ ] Preserve the requested lifecycle exactly: run BMAD first when selected, then run lockfile generation/revalidation, then initialize git and create the initial commit, then run the core-tools updater when selected.
- [ ] Add native git helpers that operate inside the generated project directory and perform `git init`, `git add .`, and `git commit -m "Initial Commit"`.
- [ ] Refactor the current native tools-sync implementation into reusable task definitions and a streaming runner that can power both text-mode CLI output and a Textual TUI.
- [ ] Bring native core-tools updater parity with `.template_scripts/update-opencode.sh`, including `uv`, `bun`, `turbo`, `opencode`, `btca`, `gh`, and `ripgrep`, plus install-vs-update behavior where applicable.
- [ ] Build a dedicated Textual updater app for the core-tools flow with a persistent status table, real-time row updates, and a scrolling log pane that streams subprocess output while work runs.
- [ ] Add a direct `nurt` CLI entrypoint for the core-tools updater so users can trigger install/update outside project creation.
- [ ] Add a separate native BMAD updater command path so users can trigger the BMAD installer/update flow from `nurt` outside project creation.
- [ ] Implement the BMAD updater as a clean external-process handoff rather than attempting to re-render its existing full-screen UI inside the core-tools TUI.

## BLUE

- [ ] Tighten failure handling so unsuccessful BMAD, lockfile, git, or updater steps leave clear diagnostics and do not silently report success.
- [ ] Keep rich interactive behavior deterministic across TTY, non-TTY, explicit plain mode, and explicit rich mode fallback paths.
- [ ] Refactor shared command-running and status-rendering code to avoid duplicating lifecycle logic between `nurt new`, the core-tools updater command, and the BMAD updater command.
- [ ] Re-run targeted contract subsets first, then run the full `uv run pytest` suite once the slice is stable.

## Documentation Sync

- [ ] Update `PROGRESS.md`.
- [ ] Update `docs/LIVING_DOCS.md`.
- [ ] Update `docs/ARCHITECTURE.md`.
- [ ] Create a new session summary in `docs/session-summaries/`.
