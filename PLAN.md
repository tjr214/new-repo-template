# Feature 9 Plan

**Last Updated:** 2026-03-25 08:36:07 PM
**Status:** YELLOW complete / ready for RED
**Roadmap Item:** `TODO-FEATURES.md` feature `9.0`
**Latest Session Summary:** `docs/session-summaries/SESSION_123_SUMMARY.md`
**Previous Cycle Archive:** `docs/archive/plans/PLAN_2026-03-25_06-30-37_PM.md`

---

## Goal

Implement feature `9.0`: generate a monorepo-composition-aware `btca.config.jsonc` during `nurt new`, patch it safely during `nurt add`, and keep BTCA ownership tracking separate from the BTCA config schema that `nurt` does not own.

---

## Locked Decisions

- `btca.config.jsonc` must remain a pure BTCA file. `nurt` will not add custom metadata fields to BTCA resource objects.
- `nurt` ownership/drift metadata for managed BTCA resources will live in `.nurt/btca-managed-resources.json`.
- `nurt new` will generate both files from the selected project mix.
- `nurt add` will read both files and patch only `nurt`-managed BTCA resources additively by stable resource `name`.
- User-added BTCA resources must be preserved.
- Drifted managed BTCA resources must be preserved and warned about rather than overwritten silently.
- `docs/BTCA_RESOURCES.md` must be generated from the final project-level `btca.config.jsonc`, not from the sidecar file.
- The current planning pass exposed a scaffold gap: generated governance guidance already references `docs/BTCA_RESOURCES.md`, but the foundation scaffold does not currently write that file. Feature `9.0` must close that gap.
- Every materially used scaffolded framework/library/tool should have BTCA coverage in the generated configuration for that target composition.
- Desktop explicitly needs Electron Forge BTCA coverage under that rule.

---

## Explicit Non-Goals

- Do not rely on undocumented BTCA-schema extensibility for `nurt` metadata.
- Do not auto-delete user BTCA resources.
- Do not auto-delete drifted managed BTCA resources.
- Do not implement a legacy-repo migration/bootstrap path for repos that predate the feature `9.0` sidecar unless RED coverage proves it is required; there are no known field repos that require a compatibility layer.
- Do not add or remove project BTCA resources during implementation without explicit user confirmation if the missing dependency is not already in project BTCA resources.

---

## YELLOW Record

The YELLOW pass is complete and included all required parts:

- File reads:
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
- BTCA runtime validation:
  - `btca status`
- `btca ask` usage:
  - `btca ask -q "Does btca config allow extra fields in resource objects" --sub-agent --no-thinking --no-tools`
  - `btca ask -q "Should a tool keep user metadata in a separate file instead of extending another tool config it does not own" --sub-agent --no-thinking --no-tools`

YELLOW conclusions:

- BTCA ask suggested extra fields may be tolerated in practice, but that is not a safe enough contract for a file `nurt` does not own.
- The safer and now-locked design is a separate `nurt` sidecar file.
- The foundation scaffold currently mirrors a static root `btca.config.jsonc` and does not scaffold `docs/BTCA_RESOURCES.md`; feature `9.0` needs to make both outputs composition-aware.

---

## Implementation Shape

### 1. New BTCA planner/manager module

Create a dedicated Python module (recommended name: `src/new_repo_template/btca_config_manager.py`) that owns:

- the project-kind-to-BTCA-resource mapping table
- rendering `btca.config.jsonc`
- rendering/parsing `.nurt/btca-managed-resources.json`
- managed-resource fingerprinting/drift detection
- additive merge logic for `nurt add`
- rendering `docs/BTCA_RESOURCES.md` from resolved BTCA config data

### 2. `nurt new` / scaffold integration

Replace the static foundation copy behavior for BTCA files with generated output:

- write `btca.config.jsonc` from the resolved scaffold project mix
- write `.nurt/btca-managed-resources.json`
- write `docs/BTCA_RESOURCES.md`

This likely requires updating `src/new_repo_template/scaffold.py` so BTCA-related outputs are generated dynamically instead of copied verbatim from the current root template snapshot.

### 3. `nurt add` integration

Extend add-mode planning/execution to:

- read current `btca.config.jsonc`
- read `.nurt/btca-managed-resources.json`
- compute required resources for the combined project inventory
- add missing managed resources
- update unchanged managed resources when the fingerprint still matches
- preserve and warn on drifted managed resources
- leave user-added BTCA resources untouched
- rewrite `docs/BTCA_RESOURCES.md` from the final merged BTCA config

### 4. Foundation/snapshot baseline alignment

Feature `9.0` will likely need to change the current foundation baseline contract because BTCA files are no longer a pure static mirror of root repo files.

Expected effects:

- stop treating generated `btca.config.jsonc` as a byte-for-byte mirror of root `btca.config.jsonc`
- add generated `docs/BTCA_RESOURCES.md` to the foundation output baseline
- decide whether `.nurt/btca-managed-resources.json` should be generated dynamically only or also represented in snapshot governance expectations

---

## Open Mapping Work Before RED

Before writing the RED tests, confirm the resource mapping table for each target using only already-approved project BTCA resources, and flag any missing resource decisions for user confirmation.

The mapping rule is now strict: do not treat BTCA coverage as optional convenience context. If a target materially uses a framework, library, or tool, include it in the target mapping or explicitly document why it is out of scope.

Current likely mapping direction:

- `foundation`
  - `turborepo`
  - `bun`
- `python`
  - `uv`
  - `textual`
  - `rich-docs`
- `python-lib`
  - `uv`
- `typescript-cli`
  - `bun`
- `typescript-lib`
  - `bun`
- `web`
  - `tanstack-router-start`
  - `bun`
- `backend`
  - `convex-docs`
  - auth-specific: `clerk-docs` or `better-auth-core`
  - add `convex-better-auth` only when backend auth is `better-auth`
- `mobile`
  - `expo-docs`
- `tv`
  - `expo-docs`
  - `react-native-tvos`
  - `expo-tv-config`
- `desktop`
  - Electron Forge resource coverage is required; propose the missing project BTCA resource(s) to the user before implementation because they are not currently present in the template's BTCA config

Also audit the other targets against the same rule during RED so the final mapping is comprehensive rather than desktop-only. Decide then whether `pytest-textual-snapshot` belongs in generated Python-app BTCA defaults. Current recommendation: no, unless an explicit generated testing workflow depends on it.

---

## RED Plan

Add or update failing contract coverage for the following behaviors:

- new unit/contract coverage for BTCA config planning/rendering
  - recommended file: `tests/contracts/test_btca_config_contract.py`
- foundation scaffold contract updates in `tests/contracts/test_root_workspace_contract.py`
  - generated `btca.config.jsonc` content should be composition-aware rather than a root-file mirror
  - generated `.nurt/btca-managed-resources.json` should exist
  - generated `docs/BTCA_RESOURCES.md` should exist
- `nurt add` contract coverage in `tests/contracts/test_nurt_add_contract.py`
  - additive managed-resource merge
  - user-resource preservation
  - drift-preserving warning behavior
- CLI/dry-run contract coverage in `tests/contracts/test_nurt_cli_contract.py`
  - dry-run output should mention BTCA config, sidecar, and docs updates when relevant

Specific RED scenarios to cover:

- `foundation`-only scaffold gets only the baseline BTCA resources
- `python` scaffold adds `uv` + Textual/Rich resources
- `web + backend` scaffold adds TanStack + Convex + auth-specific resources
- `tv` scaffold adds TV-specific resources on top of Expo docs
- `nurt add` adds new managed resources without deleting user-added ones
- `nurt add` updates an unchanged managed resource when the fingerprint matches
- `nurt add` preserves a drifted managed resource and surfaces a warning
- generated `docs/BTCA_RESOURCES.md` reflects the final resolved BTCA config exactly

---

## GREEN Plan

Implement the smallest passing version in this order:

1. Add `src/new_repo_template/btca_config_manager.py` with:
   - resource definitions
   - mapping resolution
   - JSON/JSONC rendering helpers
   - sidecar rendering/parsing
   - fingerprint helpers
   - docs rendering for `docs/BTCA_RESOURCES.md`
2. Integrate BTCA generation into `src/new_repo_template/scaffold.py`.
3. Integrate BTCA merge/update into `src/new_repo_template/add_mode.py`.
4. Update any CLI dry-run/reporting text in `src/new_repo_template/nurt_cli.py` if RED requires it.
5. Update foundation/scaffold expectations where the old snapshot-mirror assumption no longer applies.

---

## BLUE Plan

After GREEN is passing:

- refactor resource definitions and mapping helpers for clarity
- make sidecar fingerprint scope explicit and deterministic
- harden error and warning messages for drifted managed resources and missing sidecar cases
- verify that generated docs rendering stays stable and deterministic
- rerun targeted and then full validation

---

## Documentation Sync Requirements

When implementation begins and each slice closes, update all of the following together:

- `PROGRESS.md`
- `docs/LIVING_DOCS.md`
- `docs/ARCHITECTURE.md`
- `TODO-FEATURES.md` (as feature `9.0` milestones are discussed/implemented)
- `docs/session-summaries/SESSION_*.md` (create a new file; never overwrite)

If project BTCA resources themselves are added/removed for this repository during implementation, also sync:

- `btca.config.jsonc`
- `docs/BTCA_RESOURCES.md`

and revalidate with:

- `btca status`

---

## Validation Plan

Minimum targeted validation once code exists:

```bash
uv run pytest tests/contracts/test_btca_config_contract.py
uv run pytest tests/contracts/test_root_workspace_contract.py tests/contracts/test_nurt_add_contract.py tests/contracts/test_nurt_cli_contract.py
uv run ruff check src/new_repo_template tests/contracts
```

Full validation at slice closeout:

```bash
uv run pytest
```

If scaffold/snapshot-governance files change materially, also run:

```bash
uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."
```

---

## Fresh-Context Restart

If context is cleared before implementation, do this exact restart sequence first.

### Read First

- `PLAN.md`
- `PROGRESS.md`
- `docs/LIVING_DOCS.md`
- `docs/ARCHITECTURE.md`
- `TODO-FEATURES.md`
- `docs/session-summaries/SESSION_123_SUMMARY.md`
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
- `tests/contracts/test_nurt_add_contract.py`
- `tests/contracts/test_nurt_cli_contract.py`

### Re-run YELLOW Runtime Checks

```bash
date "+%Y-%m-%d %I:%M:%S %p"
btca status
btca ask -q "Does btca config allow extra fields in resource objects" --sub-agent --no-thinking --no-tools
btca ask -q "Should a tool keep user metadata in a separate file instead of extending another tool config it does not own" --sub-agent --no-thinking --no-tools
```

### Resume Execution Order

1. Confirm the project-kind-to-BTCA-resource mapping table and identify any missing project BTCA resources that would require user confirmation before implementation.
   - This now includes Electron Forge for desktop and the same mismatch audit for all other targets.
2. Write RED tests/contracts for dynamic BTCA config generation, sidecar tracking, additive add-mode patching, drift warnings, and `docs/BTCA_RESOURCES.md` generation.
3. Implement the BTCA planner/manager module and scaffold/add integration.
4. Run targeted validation, then BLUE refactor/hardening, then full validation.
5. Sync docs again and write a new session summary.

### Restart Safety Notes

- Do not forget that the YELLOW pass already included file reads, `btca status`, and `btca ask` usage; repeat them after context reset before editing.
- Do not put `nurt` metadata into `btca.config.jsonc`.
- Do not delete user BTCA resources.
- Do not overwrite existing session summaries.
