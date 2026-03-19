# Feature 5.0 Plan

**Last Updated:** 2026-03-19 02:57:08 PM
**Status:** Ready for Implementation
**Previous Cycle Archive:** `docs/archive/plans/PLAN_2026-03-19_12-45-13_PM.md`
**Previous Cycle Summary:** `docs/session-summaries/SESSION_111_SUMMARY.md`

---

## Goal

Implement feature `5.0` so `nurt sync template-assets` becomes a real native, manifest-driven maintenance command for existing nurt-generated repositories, replacing only the explicitly managed template assets while preserving all user-specific repo content.

---

## Locked Decisions

- `nurt sync template-assets` updates only an explicit managed subset: `AGENTS.md`, `README.BMAD-GUIDE.md`, `README.RALPH.md`, selected `.opencode/command/*`, selected `.agent/rules/*`, selected `.agent/workflows/*`, and selected `docs/workflows/*` files.
- Sync must never behave like a directory mirror: no broad subtree copy, no delete/prune pass, and no touching custom sibling files that are not explicitly listed as managed.
- Sync eligibility stays inside `src/new_repo_template/snapshot_assets/source_manifest.json`; each entry will gain `management` metadata so scaffold and sync behavior derive from one source of truth.
- Sync content comes from the bundled snapshot assets shipped with the currently installed `nurt` version, not from a live template-repo clone.
- Real sync execution requires a clean git working tree so template-maintenance diffs remain isolated from feature work; `--dry-run` stays non-destructive.
- Repo validation should align with current nurt identity rules and use `.nurt/repo.json` rather than the older `.template_scripts/`-based root heuristic.
- The future self-update feature remains separate: the long-term command name is `nurt upgrade`, and feature `5.0` should not expand into remote self-update behavior.

---

## YELLOW

- [ ] Reread the current sync/scaffold/runtime-manifest implementation files before editing: `src/new_repo_template/sync_ops.py`, `src/new_repo_template/nurt_cli.py`, `src/new_repo_template/foundation_manifest.py`, `src/new_repo_template/snapshot_builder.py`, and `src/new_repo_template/snapshot_assets_loader.py`.
- [ ] Reread the manifest and packaged-template source-of-truth files that affect this slice: `src/new_repo_template/snapshot_assets/source_manifest.json` and the current bundled foundation template paths under `src/new_repo_template/snapshot_assets/templates/foundation/`.
- [ ] Reread the current sync-facing contracts and any snapshot/root-validation tests that the new behavior will replace or extend, including `tests/contracts/test_nurt_cli_contract.py`, `tests/contracts/test_snapshot_assets_contract.py`, and any new dedicated template-sync contract coverage added for this feature.
- [ ] Run `btca status` and use `btca ask` for any dependency or library guidance that affects implementation details for this slice; at minimum, preserve the current understanding that `uv tool upgrade` is the standard Git-installed tool refresh path so feature `5.0` and feature `7.0` remain cleanly separated.
- [ ] Confirm the manifest schema update plan before coding: existing source-manifest consumers must continue to work once `management` metadata is added.
- [ ] Confirm validation targets and out-of-scope boundaries: feature `5.0` implements manifest-driven bundled-asset sync plus legacy updater retirement, but does not implement the future `nurt upgrade` product surface.

## RED

- [ ] Add or update failing contract coverage for the source-manifest schema so entries can declare `management` metadata without breaking existing scaffold/runtime-manifest flows.
- [ ] Add failing coverage for a manifest-derived sync allowlist that filters to exact file paths marked for sync, rather than hard-coded directory rules or a second sync-specific manifest.
- [ ] Add failing coverage for `nurt sync template-assets --dry-run` so it reports the manifest-derived sync plan using the bundled-asset source model and does not reference the legacy clone script behavior.
- [ ] Add failing coverage for non-dry-run root validation using `.nurt/repo.json` instead of the current `.template_scripts/`-based check.
- [ ] Add failing coverage for the strict clean-git requirement so real sync refuses to run when the repo has uncommitted changes.
- [ ] Add failing coverage proving that sync updates managed files while preserving custom sibling files in `.opencode/command/`, `.agent/`, and `docs/workflows/`.
- [ ] Add failing coverage proving that sync does not delete unlisted files and does not create empty optional namespaces such as `.opencode/agent/` when there are no managed files for them.

## GREEN

- [ ] Extend source-manifest parsing to understand per-entry `management` metadata while preserving the existing scaffold and snapshot-builder consumers.
- [ ] Add helper logic that derives the syncable subset from `source_manifest.json`, maps `templates/foundation/...` entries back to repo-root destinations, and rejects entries that do not belong to the approved sync scope.
- [ ] Replace the current clone-based template sync flow in `src/new_repo_template/sync_ops.py` with bundled-asset exact-path copy behavior driven by the manifest-derived sync subset.
- [ ] Update repo-root validation for template sync so it uses the explicit nurt repo marker `.nurt/repo.json`.
- [ ] Keep dry-run output useful and non-destructive by reporting the manifest-derived sync targets and bundled-asset source model clearly.
- [ ] Preserve the strict clean-working-tree guard for non-dry-run sync execution.
- [ ] Remove the remaining runtime dependency on live cloning for template-asset sync.

## BLUE

- [ ] Refactor the new manifest helper code so scaffold-oriented and sync-oriented path derivation stay centralized, typed, and easy to extend.
- [ ] Harden failure messaging so operators get clear remediation for invalid repo roots, dirty git state, or manifest/path inconsistencies.
- [ ] Review the legacy `.template_scripts/update-template-from-git.sh` script after the native path is complete and manually confirm it is safe to retire.
- [ ] Remove the legacy updater script only after the native implementation and contracts make it redundant.
- [ ] Rerun targeted validation for the touched contracts plus broader repository validation as appropriate.

## Validation Targets

- [ ] `uv run pytest tests/contracts/test_nurt_cli_contract.py`
- [ ] `uv run pytest tests/contracts/test_snapshot_assets_contract.py`
- [ ] `uv run pytest <new-or-updated-template-sync-contracts>`
- [ ] `uv run ruff check src/new_repo_template tests/contracts`
- [ ] `uv run pytest`

## Documentation Sync

- [ ] Update `TODO-FEATURES.md` as implementation choices or follow-up scope evolve.
- [ ] Update `PROGRESS.md`.
- [ ] Update `docs/LIVING_DOCS.md`.
- [ ] Update `docs/ARCHITECTURE.md`.
- [ ] Create a new session summary in `docs/session-summaries/`.
