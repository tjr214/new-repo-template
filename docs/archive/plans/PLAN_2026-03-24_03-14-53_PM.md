# Feature 7.0 Plan - `nurt upgrade`

**Last Updated:** 2026-03-24 01:33:44 PM
**Status:** Completed
**Previous Cycle Archive:** `docs/archive/plans/PLAN_2026-03-20_12-11-26_AM.md`
**Previous Cycle Summary:** `docs/session-summaries/SESSION_116_SUMMARY.md`
**Roadmap Source:** `TODO-FEATURES.md`
**Primary Goal:** Replace the transitional `nurt update` behavior with the real feature `7.0` contract: a supported `nurt upgrade` command for `uv`-managed installs, with no alias and no automatic template-asset sync.

## Outcome

- Feature `7.0` is now complete.
- The live CLI now exposes `nurt upgrade` as the only supported self-update command.
- The old `nurt update` surface has been removed rather than preserved as a compatibility alias.
- Startup notices now use `uv tool list --outdated`, and the real upgrade command targets uv package `nurt-ai` while preserving the operator-facing executable name `nurt`.
- Template-asset sync remains intentionally separate and is only suggested as a follow-up via `nurt sync template-assets`.

---

## Why This Is The Next Slice

- `TODO-FEATURES.md` marks feature `7.0` as the first unfinished roadmap item and explicitly defines the desired end state as `nurt upgrade`.
- `PROGRESS.md` already says the next open work is the YELLOW discussion/planning pass for feature `7.0`.
- Feature `5.0` intentionally stopped short of self-update: `nurt sync template-assets` assumes the operator upgrades `nurt` first and then syncs bundled assets separately.
- The live CLI still contains transitional `update` plumbing, so the repo currently has a mismatch between roadmap intent and actual command surface.

---

## Locked Decisions From The User Discussion

These decisions are already agreed and must be treated as feature contract unless the user explicitly changes them later.

- The official command name is `nurt upgrade`.
- There will be **no** `nurt update` alias. Removing the old name is part of the feature, not optional cleanup.
- V1 officially supports `uv`-managed installs only.
- `nurt upgrade` upgrades the installed `nurt` tool itself; it does **not** perform `nurt sync template-assets` automatically.
- After a successful upgrade, the CLI may suggest `nurt sync template-assets` as a separate next step, but must not run it on the user's behalf.
- If `uv` is missing or the install cannot be upgraded through the supported path, the CLI should fail clearly and give exact manual remediation instead of guessing.

---

## Current Repository State To Preserve In Context

These facts explain why feature `7.0` is needed and where the existing transitional behavior lives.

- `README.md:10` currently documents installation through `uv tool install git+https://github.com/tjr214/new-repo-template.git`.
- `pyproject.toml:6` names the Python distribution `nurt-ai` while `pyproject.toml:16` exposes the console script `nurt`.
- `src/new_repo_template/nurt_cli.py:95` runs a startup update check and currently tells users to run `nurt update`.
- `src/new_repo_template/nurt_cli.py:423` still registers an `update` subcommand.
- `src/new_repo_template/nurt_cli.py:859` currently implements `handle_update()` as a minimal `uv tool upgrade nurt` wrapper.
- `tests/contracts/test_nurt_cli_contract.py:630` still locks the old `nurt update --dry-run` behavior and must be updated as part of RED.
- `docs/LIVING_DOCS.md:42` and `docs/LIVING_DOCS.md:81` already document that the intended future command name is `nurt upgrade`, not `nurt update`.
- `docs/ARCHITECTURE.md:182` also says the eventual self-update UX belongs to feature `7.0` under `nurt upgrade`, but `docs/ARCHITECTURE.md:67` still references an older `nurt update` lifecycle and will need cleanup when implementation lands.

---

## Feature Contract

When feature `7.0` is complete, the repo should satisfy all of the following:

1. `nurt upgrade` exists as the only supported self-update command.
2. `nurt update` is removed rather than preserved as a compatibility alias.
3. `nurt upgrade --dry-run` is non-destructive and clearly reports the supported `uv` upgrade action.
4. Real `nurt upgrade` runs the supported `uv` tool-upgrade flow for the installed `nurt` tool.
5. Startup update notices, if shown, instruct the user to run `nurt upgrade`, never `nurt update`.
6. The command surface, docs, and tests all use the same terminology.
7. The command remains intentionally separate from `nurt sync template-assets`.

---

## Explicit Non-Goals

- Do not add a `nurt update` alias.
- Do not fold template-asset sync into the upgrade command.
- Do not add support for every possible installer/channel in v1.
- Do not change BTCA resources unless YELLOW proves a new project-level resource is truly needed and the user explicitly confirms it.
- Do not broaden feature `7.0` into a general release-management workflow.

---

## YELLOW

The YELLOW phase must be completed and documented before implementation edits beyond planning.

### YELLOW objectives

- Re-read all repo files that define the current install, update, release, and contract surfaces.
- Reconfirm the supported `uv` self-upgrade semantics with BTCA before changing the command contract.
- Resolve the naming/source questions around `uv tool upgrade`, especially because the install docs use a Git URL while the project metadata names the distribution `nurt-ai` and the executable is `nurt`.
- Lock the validation plan, user-visible copy targets, and out-of-scope boundaries before writing tests.

### Files to read during YELLOW

- `TODO-FEATURES.md`
- `PLAN.md`
- `PROGRESS.md`
- `README.md`
- `pyproject.toml`
- `docs/LIVING_DOCS.md`
- `docs/ARCHITECTURE.md`
- `.github/workflows/release.yml`
- `src/new_repo_template/nurt_cli.py`
- Any helper modules referenced by the CLI after inspection if upgrade logic needs extraction
- `tests/contracts/test_nurt_cli_contract.py`
- Any additional contract files that mention install/update wording after grep confirms them

### BTCA work required during YELLOW

- Run `btca status`.
- Run `btca resources`.
- Use `btca ask` with plain, simple query strings to answer at least these questions:
  - What is the recommended `uv` self-upgrade flow for a tool installed with `uv tool install` from a Git URL?
  - Should the upgrade target refer to the tool executable name, the distribution name, or the original Git source?
  - What dry-run or inspection behavior is safe and stable enough for startup update checks and user-facing remediation?
  - What output/exit-code expectations from `uv` should the CLI treat as success, no-op, or unsupported-install guidance?

### YELLOW completion checklist

- [x] Reread the full file set above.
- [x] Run `btca status`.
- [x] Run `btca resources`.
- [x] Run the required `btca ask` lookups for `uv` self-upgrade semantics.
- [x] Confirm the exact supported upgrade command shape.
- [x] Confirm whether the startup check can stay as `uv tool upgrade --dry-run ...` or needs a safer/clearer variant.
- [x] Confirm all user-visible wording to replace `update` with `upgrade`.
- [x] Record any remaining risks before starting RED.

---

## RED

Add or update failing tests/contracts so the desired feature surface is locked before GREEN.

### RED targets

- Update the existing old-name contract in `tests/contracts/test_nurt_cli_contract.py` from `nurt update` to `nurt upgrade`.
- Add explicit contract coverage that `nurt update` is no longer a valid subcommand.
- Update startup-notice expectations so simulated update availability points users to `nurt upgrade`.
- Add or adjust dry-run expectations so the output remains non-destructive, explicit, and clearly tied to the supported `uv` path.
- Add failure-path coverage for missing `uv` if no such contract exists yet.
- If implementation introduces helper functions for parsing upgrade outcomes, add focused unit/contract coverage at the smallest stable seam.

### RED candidate assertions

- `nurt upgrade --dry-run` exits successfully and prints a non-destructive plan.
- The dry-run output references `uv tool upgrade` and `nurt`.
- A simulated startup update notice says `Run `nurt upgrade`.` rather than `Run `nurt update`.`
- `nurt update` fails because the command no longer exists.
- A missing-`uv` real run fails with a clear remediation message.
- The command does not claim to run template sync.

### RED completion checklist

- [x] Replace old-name dry-run test coverage with `nurt upgrade` coverage.
- [x] Add explicit rejection coverage for `nurt update`.
- [x] Update startup-notice contract wording.
- [x] Add missing-`uv` failure coverage if absent.
- [x] Ensure RED fails for the right reasons before GREEN begins.

---

## GREEN

Implement the minimum change set required to satisfy the RED contracts without broadening scope.

### GREEN implementation targets

- Replace the `update` subcommand registration in `src/new_repo_template/nurt_cli.py` with `upgrade`.
- Rename `handle_update()` to `handle_upgrade()` or equivalent and update internal routing accordingly.
- Update startup update-check messaging from `nurt update` to `nurt upgrade`.
- Keep the supported upgrade path limited to `uv`-managed installs.
- Preserve `--dry-run` behavior with clear explicit output.
- Ensure real execution errors are translated into actionable human-readable guidance when `uv` is unavailable or the supported path cannot proceed.
- Keep the implementation separate from `nurt sync template-assets`.

### GREEN design guidance

- Prefer the smallest CLI-local change unless YELLOW proves a helper extraction makes testing much cleaner.
- Avoid speculative support for install channels we are not officially supporting in v1.
- If user-visible messages mention a next step, suggest `nurt sync template-assets` only as optional follow-up after upgrade.
- Keep the copy consistent with the roadmap and docs: use `upgrade` everywhere.

### GREEN completion checklist

- [x] Parser exposes `upgrade`, not `update`.
- [x] Startup notice text uses `nurt upgrade`.
- [x] Dry-run output is explicit and non-destructive.
- [x] Missing-`uv` and unsupported-path failures are clear.
- [x] No implementation path auto-runs template sync.

---

## BLUE

Refactor, harden, and align copy/docs after the feature works.

### BLUE targets

- Clean up naming so there is no lingering `update` wording in the live upgrade feature surface.
- Improve command/result messaging for no-op, success, and failure cases.
- Reduce brittle coupling in tests where exact wording is not the real contract.
- Re-scan the repo for stale `nurt update` references and either remove them or clearly preserve them only in historical/archive context.

### BLUE repo scan targets

- `src/new_repo_template/**/*.py`
- `tests/**/*.py`
- `README.md`
- `docs/LIVING_DOCS.md`
- `docs/ARCHITECTURE.md`
- `PROGRESS.md`
- Non-archive docs that still mention the old command name

### BLUE completion checklist

- [x] No live CLI/docs/tests reference `nurt update` as a supported command.
- [x] User-visible success/failure copy is concise and actionable.
- [x] Tests assert stable behavior rather than fragile prose where possible.
- [x] Full validation passes.

---

## Validation Plan

These commands are the expected validation path unless YELLOW finds a better-targeted subset first.

### Required targeted validation

- `uv run pytest tests/contracts/test_nurt_cli_contract.py`
- `uv run ruff check src/new_repo_template tests/contracts`

### Likely additional validation

- Any extra focused pytest command for newly added upgrade-helper coverage
- `uv run pytest` after targeted validation succeeds

### Optional manual checks

- Run `uv run python -m new_repo_template.nurt_cli upgrade --dry-run`
- Run a simulated startup-notice invocation with `NURT_UPDATE_CHECK_SIMULATE=<version>` and confirm the message points to `nurt upgrade`
- Confirm `uv run python -m new_repo_template.nurt_cli update` now fails as an unknown command

---

## Documentation Sync

When implementation begins or completes, keep the living docs synchronized. This is mandatory, not optional.

- [x] Update `PROGRESS.md` with the YELLOW findings, implementation progress, validation commands, and feature `7.0` state.
- [x] Update `docs/LIVING_DOCS.md` to reflect the real `nurt upgrade` contract and current implementation status.
- [x] Update `docs/ARCHITECTURE.md` to remove transitional `nurt update` language from live sections and document the supported `uv`-managed self-upgrade workflow.
- [x] Create a brand-new session summary in `docs/session-summaries/` with the current date/time in the required format; never overwrite an existing summary.

---

## Resume-From-Blank-Context Notes

If a future agent resumes from scratch, these are the most important facts to recover quickly without this conversation.

- The user explicitly approved feature `7.0` as the next work item.
- The user explicitly approved the narrow v1 strategy: support `uv`-managed installs only.
- The user explicitly rejected keeping a `nurt update` alias because it would create unnecessary extra work.
- Therefore the implementation must remove or replace the old `update` command surface rather than preserving it.
- `nurt sync template-assets` remains a separate feature path and must not be auto-invoked from `nurt upgrade`.
- The plan must be executed using YELLOW-RED-GREEN-BLUE, including repo-file rereads plus `btca ask` during YELLOW.

---

## Definition Of Done

- `nurt upgrade` is the only supported self-update command in the live CLI.
- `nurt update` no longer exists as a supported command or alias.
- Startup update notices point to `nurt upgrade`.
- Docs, tests, and CLI help all agree on the new command name and supported scope.
- The v1 path is clearly documented as `uv`-managed only.
- Validation passes and the living docs/session records are updated.
