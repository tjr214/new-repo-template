# Development Progress

**Last Updated:** 2026-03-11 10:37:16 PM
**Current Phase:** Completed Turbo baseline refresh follow-up for PR guardrail recovery

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

## Next Up

- [ ] Define the next endeavour's scope, deliverables, and success criteria.
- [ ] Start the next YELLOW research pass, including `btca status` and any dependency-specific `btca ask` lookups.
