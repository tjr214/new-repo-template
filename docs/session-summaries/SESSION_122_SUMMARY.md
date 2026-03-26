# Session 122 Summary

## Date and Time

2026-03-25 08:23:05 PM

## Scope

Completed the feature `9.0` YELLOW discussion/planning pass and locked the ownership/merge design for composition-aware BTCA configuration before implementation begins.

## Inputs

- `PLAN.md`
- `PROGRESS.md`
- `docs/LIVING_DOCS.md`
- `docs/ARCHITECTURE.md`
- `TODO-FEATURES.md`
- `docs/session-summaries/SESSION_121_SUMMARY.md`
- `btca.config.jsonc`
- `docs/BTCA_RESOURCES.md`
- `src/new_repo_template/scaffold.py`
- `src/new_repo_template/add_mode.py`
- `src/new_repo_template/nurt_cli.py`
- `src/new_repo_template/foundation_manifest.py`
- `src/new_repo_template/snapshot_builder.py`
- `src/new_repo_template/snapshot_assets_loader.py`
- `src/new_repo_template/repo_identity.py`
- `src/new_repo_template/snapshot_assets/source_manifest.json`
- `src/new_repo_template/snapshot_assets/templates/foundation/btca.config.jsonc`
- `tests/contracts/test_root_workspace_contract.py`

## YELLOW Pass

- Re-read the current planning trackers, living docs, architecture notes, roadmap, and latest completed session summary before editing any planning artifacts.
- Re-read the live BTCA files (`btca.config.jsonc`, `docs/BTCA_RESOURCES.md`) plus the current scaffold/add/foundation/snapshot/repo-identity paths that will shape feature `9.0` implementation.
- Ran `btca status`.
- Used `btca ask` with plain/simple query strings to check config-extensibility signals and config-ownership guidance before finalizing the plan.

## Findings

- `btca ask` suggested extra fields may be tolerated in practice, but that is not a safe enough contract for a file that `nurt` does not own.
- The safer and now-locked design is to keep `btca.config.jsonc` pure BTCA and store `nurt` ownership/drift metadata in a separate `.nurt/btca-managed-resources.json` sidecar.
- The additive merge model is also locked: `nurt new` seeds managed resources from the selected project mix, `nurt add` patches only tracked managed resources by stable resource name, user-added BTCA resources are preserved, and drifted managed entries warn instead of being overwritten.
- The planning pass also surfaced a current scaffold gap: generated governance guidance references `docs/BTCA_RESOURCES.md`, but the foundation scaffold does not yet write that file. Feature `9.0` now includes closing that gap.

## Documentation Updates

- Updated `PROGRESS.md` with the completed feature `9.0` YELLOW pass, the locked sidecar design, and the new RED/GREEN next step.
- Updated `docs/LIVING_DOCS.md` with the locked BTCA ownership/merge model and the newly identified `docs/BTCA_RESOURCES.md` scaffold gap.
- Updated `docs/ARCHITECTURE.md` with the BTCA ownership boundary, additive merge policy, and feature `9.0` implementation direction.
- Updated `TODO-FEATURES.md` to record the completed feature `9.0` discussion decisions.
- Replaced the root `PLAN.md` stub with a restart-safe feature `9.0` implementation plan.

## Outcome

- Feature `9.0` is ready to move from YELLOW into RED/GREEN.
- The implementation path is now explicit, restart-safe, and constrained to a pure BTCA config plus a `nurt`-owned sidecar metadata file.
