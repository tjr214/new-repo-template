# Development Progress

**Last Updated:** 2026-03-12 03:15:28 PM
**Current Phase:** Interactive TUI overhaul complete for `nurt new`

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

## Next Up

- [ ] Optional follow-up: revisit `pytest-textual-snapshot` if an upstream release adds compatibility with the repository's `pytest>=9` baseline.
