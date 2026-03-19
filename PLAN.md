# Nurt Add Plan

**Last Updated:** 2026-03-19 12:41:36 PM
**Status:** Completed
**Previous Cycle Archive:** `docs/archive/plans/PLAN_2026-03-15_12-30-32_PM.md`
**Previous Cycle Summary:** `docs/session-summaries/SESSION_106_SUMMARY.md`

---

## Goal

Implement `nurt add` so existing nurt-generated monorepos can gain new named project instances in place, with both CLI and Textual wizard flows, while refusing to run outside nurt-made repos.

---

## Guardrails

- `nurt add` only works from the root of a nurt-made repository.
- Repo identity is explicit, not heuristic: the repo root must contain `.nurt/repo.json`.
- Repo-root validation is strict: if inside a git repo, the current working directory must equal `git rev-parse --show-toplevel`; add mode must not walk upward looking for the root.
- Running in a normal directory, a nested subdirectory, or an unrelated repository must fail with a clear remediation message.
- `foundation` is not addable.
- Add mode is additive-first: it may patch existing files only when required to make a supported combination work, but it must not broadly rewrite existing starter code for cosmetic parity.
- Add mode must not run the `nurt new` post-create lifecycle (`git init`, `Initial Commit`, BMAD install prompt, or core-tools prompt).
- Repo validation must not require `pyproject.toml`, `uv.lock`, or existing project directories; foundation-only nurt repos remain valid add targets.

## YELLOW

- [x] Read the repo files, tests, and docs relevant to feature `4.0`, including `TODO-FEATURES.md`, `PROGRESS.md`, `docs/{LIVING_DOCS.md,ARCHITECTURE.md}`, `src/new_repo_template/{nurt_cli.py,scaffold.py,interactive_ui.py,interactive_tui.py,version_baseline.py,post_create.py,sync_ops.py}`, and the contract suites covering CLI routing, root workspaces, lockfiles, auth wiring, shared-package wiring, Python library wiring, and failure atomicity.
- [x] Run `btca status`, `btca resources`, and targeted `btca ask` lookups for `uv`, `bun`, `turborepo`, and `textual` so the add workflow follows official guidance for in-place workspace mutation, lockfile regeneration, and wizard behavior.
- [x] Confirm the repo-identity contract for “nurt-made repo” and lock the explicit marker contract before `nurt add` proceeds:
  - [x] `.nurt/repo.json` must exist at the repo root
  - [x] the marker file must parse successfully
  - [x] `tool` must equal `nurt`
  - [x] `schema_version` must be a supported version
- [x] Confirm the strict root rule for add mode:
  - [x] if inside a git repo, `cwd` must equal `git rev-parse --show-toplevel`
  - [x] add mode must not search parent directories for a valid root
  - [x] foundation-only repos with no existing app/library directories are still valid when `.nurt/repo.json` is present
- [x] Confirm the add-mode mutation model and the highest-risk retrofit cases:
  - adding the first Python lane into a JS-only repo
  - adding `python-lib` into a repo that already has one Python app
  - adding `web` or `backend` when `packages/shared` does not yet exist
  - adding `web` into a repo that already has `desktop`
  - adding `web` when multiple backends already exist
- [x] Lock the planning decisions for build work:
  - CLI shape: `nurt add` plus repeatable `--project <type>:<name>`
  - compatibility support for `--backend-auth` and `--web-backend`
  - TUI wizard mode for add should mirror `nurt new` where appropriate, but without the repo-name step or post-create prompts
  - repo validation happens before either the CLI add path or the wizard path can proceed
  - add mode gets a dedicated post-add lifecycle for lockfile regeneration and reporting only
  - new repos scaffold `.nurt/repo.json` as the durable repo-identity marker for future `nurt add` runs

## RED

- [x] Extend `tests/contracts/test_nurt_cli_contract.py` for `nurt add` command routing, dry-run planning, repo-root validation, nurt-repo validation, and `foundation` rejection.
- [x] Add dedicated add-mode contract coverage for in-place mutations, including:
  - [x] add one JS app to an existing nurt repo
  - [x] add repeated same-type projects to an existing nurt repo
  - [x] fail on path/name collisions with existing project instances
  - [x] fail outside repo root and inside unrelated repos
  - [x] add first Python app into a JS-only repo and create the required root uv workspace files plus `uv.lock`
  - [x] add `python-lib` into a repo with one Python app and patch the existing app dependency plus `[tool.uv.sources]`
  - [x] add `backend` and enforce auth selection
  - [x] add `web` when multiple backends exist and require explicit `--web-backend`
  - [x] add `web` or `backend` and create `packages/shared` when missing
  - [x] add `web` into a repo that already has `desktop` and retrofit the required shared-package dependency/wiring
- [x] Add interactive add-wizard coverage in the Textual contract suite for target selection, per-target name entry, backend auth selection, web-backend binding selection, review rendering, and cancel behavior.
- [x] Add failure-atomicity coverage for add mode so partial project trees, partial manifest edits, and partial root-workspace upgrades do not remain after a simulated failure.
- [x] Extend lockfile-generation coverage so add mode is contract-tested for correct `bun.lock` and `uv.lock` behavior after in-place workspace changes.

## GREEN

- [x] Add `add` subcommand parsing and orchestration in `src/new_repo_template/nurt_cli.py`.
- [x] Introduce shared planning helpers so `nurt new` and `nurt add` both reuse the `ProjectSpec`-based parsing and validation model where possible.
- [x] Add repo-root and nurt-repo validation helpers that confirm the current directory is the root of a nurt-generated repo before add mode proceeds.
- [x] Scaffold `.nurt/repo.json` into new repos so future generated repos carry the explicit add-mode identity marker.
- [x] Add an existing-repo inventory model that discovers current project instances under `apps/*/*` and `packages/*/*`, then validates requested additions against those live instances.
- [x] Build an add planner that merges requested new projects with existing repo state and computes:
  - [x] new project directories/files to create
  - [x] root files that must be created or patched
  - [x] shared support packages that must be introduced
  - [x] existing manifests that must be patched for supported combinations
  - [x] lockfiles that must be regenerated
- [x] Implement a dedicated add mutation engine for existing repos instead of reusing the fresh-repo-only `execute_scaffold()` path.
- [x] Support the first-Python-lane upgrade path by creating and/or patching root uv workspace metadata before regenerating `uv.lock`.
- [x] Support `python-lib` retrofits by patching existing Python app metadata when exactly one existing Python app should now depend on the new workspace library.
- [x] Support shared-package retrofits for supported JS combinations by creating `packages/shared` when needed and patching existing manifests/wiring only where required.
- [x] Add a plain interactive add flow and a dedicated Textual add wizard path that mirrors `nurt new` interaction quality while omitting project-name creation and post-create prompts.
- [x] Add a dedicated post-add lifecycle that regenerates/revalidates lockfiles from the repo root and prints a completion overview without attempting repo initialization or commits.

## BLUE

- [x] Refactor shared `new`/`add` planning code so validation, dry-run rendering, auth/binding rules, and project-name parsing stay aligned.
- [x] Centralize repo-root and repo-identity checks so future repo-mutating commands can reuse the same logic.
- [x] Harden add-mode rollback behavior for partial failures, especially around root manifest edits, shared-package introduction, and Python workspace upgrades.
- [x] Refine `nurt add --dry-run` output so it clearly separates detected repo state, requested additions, required retrofits, and lockfile actions.
- [x] Reconcile all add-mode docs, tests, and runtime helpers with the additive-only retrofit policy.
- [x] Keep repo-identity logic strict and explicit; do not reintroduce heuristic or legacy fallback detection without an explicit decision.
- [x] Rerun targeted contracts for `nurt add`, lockfiles, root workspaces, shared-package wiring, Python library wiring, and the Textual wizard.
- [x] Rerun `uv run ruff check src/new_repo_template tests/contracts`.
- [x] Rerun full `uv run pytest`.

## Documentation Sync

- [x] Update `PROGRESS.md`.
- [x] Update `docs/LIVING_DOCS.md`.
- [x] Update `docs/ARCHITECTURE.md`.
- [x] Update `TODO-FEATURES.md` when `4.0` is complete.
- [x] Create a new session summary in `docs/session-summaries/`.
