# Feature 5.0 Plan

**Last Updated:** 2026-03-19 04:10:11 PM
**Status:** Completed
**Previous Cycle Archive:** `docs/archive/plans/PLAN_2026-03-19_12-45-13_PM.md`
**Previous Cycle Summary:** `docs/session-summaries/SESSION_111_SUMMARY.md`

---

## Goal

Implement feature `5.0` so `nurt sync template-assets` becomes a real native, manifest-driven maintenance command for existing nurt-generated repositories, replacing only the explicitly managed template assets while preserving all user-specific repo content.

---

## Fresh-Context Restart Checklist

If a future session starts with no conversational memory, reread these files in this order before coding:

1. `PLAN.md`
2. `TODO-FEATURES.md`
3. `PROGRESS.md`
4. `docs/LIVING_DOCS.md`
5. `docs/ARCHITECTURE.md`
6. `docs/session-summaries/SESSION_113_SUMMARY.md`
7. `src/new_repo_template/sync_ops.py`
8. `src/new_repo_template/nurt_cli.py`
9. `src/new_repo_template/foundation_manifest.py`
10. `src/new_repo_template/snapshot_builder.py`
11. `src/new_repo_template/snapshot_assets_loader.py`
12. `src/new_repo_template/snapshot_assets/source_manifest.json`
13. `tests/contracts/test_nurt_cli_contract.py`
14. `tests/contracts/test_snapshot_assets_contract.py`

Then run the required YELLOW lookup steps:

- `btca status`
- `btca ask -r uv -q "For a CLI tool installed with uv tool install git plus a repository URL, is uv tool upgrade the standard way to refresh the installed tool version later?" --sub-agent`

Those reads and asks are the minimum context required to resume feature `5.0` implementation safely.

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

## Exact Managed File Inventory

As of this plan, the approved sync scope is the following exact repo-root destinations only. These should be represented by entries in `src/new_repo_template/snapshot_assets/source_manifest.json` and eventually marked with `management` metadata that includes `sync`.

- `AGENTS.md`
- `README.BMAD-GUIDE.md`
- `README.RALPH.md`
- `.agent/rules/general-rules.md`
- `.agent/workflows/project/project-export-bmad-to-ralph.md`
- `.opencode/command/project-export-bmad-to-ralph.md`
- `.opencode/command/project-resume-progress-from-last-checkpoint.md`
- `.opencode/command/project-save-progress-to-checkpoint.md`
- `.opencode/command/project-setup-or-update-btca.md`
- `.opencode/command/project-where-did-we-leave-off.md`
- `.opencode/command/repo-git-commit-and-push.md`
- `.opencode/command/repo-git-difference-between-branch-and-main.md`
- `.opencode/command/repo-git-merge.md`
- `.opencode/command/repo-git-new-branch.md`
- `.opencode/command/repo-git-what-has-changed.md`
- `.opencode/command/repo-gh-make-n-merge-PR.md`
- `docs/workflows/export-to-ralph/workflow.md`
- `docs/workflows/export-to-ralph/steps/step-01-detect-context.md`
- `docs/workflows/export-to-ralph/steps/step-02-extract.md`
- `docs/workflows/export-to-ralph/steps/step-03-transform.md`
- `docs/workflows/export-to-ralph/steps/step-04-write-file.md`

If another file is not explicitly listed here and not explicitly marked for sync in the manifest, it is out of scope for feature `5.0` sync writes.

---

## Explicit Non-Goals

- Do not sync `README.md`, `PLAN.md`, `PROGRESS.md`, `docs/ARCHITECTURE.md`, or `docs/LIVING_DOCS.md`.
- Do not delete files that exist in an end-user repo but are not part of the managed sync inventory.
- Do not touch custom sibling files in `.opencode/`, `.agent/`, or `docs/workflows/`.
- Do not create empty optional namespaces such as `.opencode/agent/` when there are no managed files for them.
- Do not implement remote template-repo cloning as the primary sync source.
- Do not fold the future self-update work into feature `5.0`; `nurt upgrade` remains feature `7.0` territory.

---

## Current Behavior To Replace

The implementation that exists today in `src/new_repo_template/sync_ops.py` is intentionally incomplete and still shaped by the legacy flow. The next implementation slice must replace these behaviors:

- root validation still checks for `.opencode/` and `.template_scripts/`
- non-dry-run sync still requires a live template-repo clone
- copied paths are hard-coded in Python rather than derived from the manifest
- the current logic is not yet driven by bundled installed assets plus per-entry sync eligibility metadata

The final feature `5.0` implementation should leave those legacy assumptions behind.

---

## First Execution Steps

When the implementation session starts, do this in order:

1. Complete the YELLOW rereads and BTCA checks listed above.
2. Update `source_manifest.json` design expectations in tests first, not code first.
3. Add RED coverage for exact managed-file sync scope and custom-file preservation.
4. Add RED coverage for `.nurt/repo.json` root validation and clean-git enforcement.
5. Only then refactor the sync engine to use bundled assets and manifest-derived sync targets.

If the session is interrupted, the next restart should begin from this section and then continue into the RED checklist below.

---

## YELLOW

- [x] Reread the current sync/scaffold/runtime-manifest implementation files before editing: `src/new_repo_template/sync_ops.py`, `src/new_repo_template/nurt_cli.py`, `src/new_repo_template/foundation_manifest.py`, `src/new_repo_template/snapshot_builder.py`, and `src/new_repo_template/snapshot_assets_loader.py`.
- [x] Reread the manifest and packaged-template source-of-truth files that affect this slice: `src/new_repo_template/snapshot_assets/source_manifest.json` and the current bundled foundation template paths under `src/new_repo_template/snapshot_assets/templates/foundation/`.
- [x] Reread the current sync-facing contracts and any snapshot/root-validation tests that the new behavior will replace or extend, including `tests/contracts/test_nurt_cli_contract.py`, `tests/contracts/test_snapshot_assets_contract.py`, and any new dedicated template-sync contract coverage added for this feature.
- [x] Run `btca status` and use `btca ask` for any dependency or library guidance that affects implementation details for this slice; at minimum, preserve the current understanding that `uv tool upgrade` is the standard Git-installed tool refresh path so feature `5.0` and feature `7.0` remain cleanly separated.
- [x] Confirm the manifest schema update plan before coding: existing source-manifest consumers must continue to work once `management` metadata is added.
- [x] Confirm validation targets and out-of-scope boundaries: feature `5.0` implements manifest-driven bundled-asset sync plus legacy updater retirement, but does not implement the future `nurt upgrade` product surface.

## RED

- [x] Add or update failing contract coverage for the source-manifest schema so entries can declare `management` metadata without breaking existing scaffold/runtime-manifest flows.
- [x] Add failing coverage for a manifest-derived sync allowlist that filters to exact file paths marked for sync, rather than hard-coded directory rules or a second sync-specific manifest.
- [x] Add failing coverage for `nurt sync template-assets --dry-run` so it reports the manifest-derived sync plan using the bundled-asset source model and does not reference the legacy clone script behavior.
- [x] Add failing coverage for non-dry-run root validation using `.nurt/repo.json` instead of the current `.template_scripts/`-based check.
- [x] Add failing coverage for the strict clean-git requirement so real sync refuses to run when the repo has uncommitted changes.
- [x] Add failing coverage proving that sync updates managed files while preserving custom sibling files in `.opencode/command/`, `.agent/`, and `docs/workflows/`.
- [x] Add failing coverage proving that sync does not delete unlisted files and does not create empty optional namespaces such as `.opencode/agent/` when there are no managed files for them.

## GREEN

- [x] Extend source-manifest parsing to understand per-entry `management` metadata while preserving the existing scaffold and snapshot-builder consumers.
- [x] Add helper logic that derives the syncable subset from `source_manifest.json`, maps `templates/foundation/...` entries back to repo-root destinations, and rejects entries that do not belong to the approved sync scope.
- [x] Replace the current clone-based template sync flow in `src/new_repo_template/sync_ops.py` with bundled-asset exact-path copy behavior driven by the manifest-derived sync subset.
- [x] Update repo-root validation for template sync so it uses the explicit nurt repo marker `.nurt/repo.json`.
- [x] Keep dry-run output useful and non-destructive by reporting the manifest-derived sync targets and bundled-asset source model clearly.
- [x] Preserve the strict clean-working-tree guard for non-dry-run sync execution.
- [x] Remove the remaining runtime dependency on live cloning for template-asset sync.

## BLUE

- [x] Refactor the new manifest helper code so scaffold-oriented and sync-oriented path derivation stay centralized, typed, and easy to extend.
- [x] Harden failure messaging so operators get clear remediation for invalid repo roots, dirty git state, or manifest/path inconsistencies.
- [x] Review the legacy `.template_scripts/update-template-from-git.sh` script after the native path is complete and manually confirm it is safe to retire.
- [x] Remove the legacy updater script only after the native implementation and contracts make it redundant.
- [x] Rerun targeted validation for the touched contracts plus broader repository validation as appropriate.

## Validation Targets

- [x] `uv run pytest tests/contracts/test_nurt_cli_contract.py`
- [x] `uv run pytest tests/contracts/test_snapshot_assets_contract.py`
- [x] `uv run pytest tests/contracts/test_template_asset_sync_contract.py tests/contracts/test_installer_scripts_dry_run_contract.py`
- [x] `uv run ruff check src/new_repo_template tests/contracts`
- [x] `uv run pytest`

## Documentation Sync

- [x] Update `TODO-FEATURES.md` as implementation choices or follow-up scope evolve.
- [x] Update `PROGRESS.md`.
- [x] Update `docs/LIVING_DOCS.md`.
- [x] Update `docs/ARCHITECTURE.md`.
- [x] Create a new session summary in `docs/session-summaries/`.
