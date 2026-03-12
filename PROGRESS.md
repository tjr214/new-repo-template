# Development Progress

**Last Updated:** 2026-03-12 04:45:09 PM
**Current Phase:** Interactive TUI stability fixes complete for `nurt new`

## Previous Cycle Archives

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

## Next Up

- [ ] Optional follow-up: revisit `pytest-textual-snapshot` if an upstream release adds compatibility with the repository's `pytest>=9` baseline.
