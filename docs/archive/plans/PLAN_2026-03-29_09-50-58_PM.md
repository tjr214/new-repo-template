# Feature 10.0 Slice 1 Closeout

**Last Updated:** 2026-03-29 08:20:28 PM
**Status:** Slice 1 implemented / manual RC1 validation next
**Previous Session Summary:** `docs/session-summaries/SESSION_127_SUMMARY.md`
**Current Implementation Summary:** `docs/session-summaries/SESSION_128_SUMMARY.md`

---

## Goal

Complete the first implementation slice inside feature `10.0 FINAL TESTS BEFORE RELEASE CANDIDATE 1`: scaffold and CLI support for the `web + backend` local-dev/auth model.

This slice is now implemented. The next work is runtime/manual validation of the generated outputs and then the remaining RC1 platform checks.

---

## Slice Outcome

- Split local/prod auth selection is now implemented for new backend-capable scaffolds.
- Same-provider shorthand remains supported through `--auth` and `--backend-auth`.
- The supported RC1 auth matrix is enforced in the scaffold layer.
- Generated web scaffolds now include provider-neutral auth boundary files.
- Generated backend scaffolds now emit runtime-aware Convex auth config.
- Generated `web+backend` repos now include `compose.yaml` and `compose.override.yaml` for the local self-hosted Convex path.
- Generated backend/web env examples and backend docs now describe the local/prod auth matrix and Docker local-dev flow.
- Targeted contracts, Ruff, template-assets validation, and the full repository suite are green.

---

## YELLOW

- [x] Re-read `PLAN.md`.
- [x] Re-read `PROGRESS.md`.
- [x] Re-read `docs/LIVING_DOCS.md`.
- [x] Re-read `docs/ARCHITECTURE.md`.
- [x] Re-read `TODO-FEATURES.md`.
- [x] Re-read `docs/session-summaries/SESSION_127_SUMMARY.md`.
- [x] Re-read `src/new_repo_template/scaffold.py`.
- [x] Re-read `src/new_repo_template/nurt_cli.py`.
- [x] Re-read `src/new_repo_template/interactive_ui.py`.
- [x] Re-read `src/new_repo_template/interactive_tui.py`.
- [x] Re-read `src/new_repo_template/add_mode.py`.
- [x] Re-read `src/new_repo_template/btca_config_manager.py`.
- [x] Re-read `src/new_repo_template/snapshot_assets/templates/fullstack/backend_readme.md`.
- [x] Re-read `src/new_repo_template/snapshot_assets/templates/wiring/backend_auth_config.ts`.
- [x] Re-read `src/new_repo_template/snapshot_assets/templates/wiring/web_auth_provider_clerk.ts`.
- [x] Re-read `src/new_repo_template/snapshot_assets/templates/wiring/web_auth_client_better_auth.ts`.
- [x] Re-read `src/new_repo_template/snapshot_assets/templates/workspace_packages/backend_package.json`.
- [x] Re-read `tests/contracts/test_fullstack_auth_wiring_contract.py`.
- [x] Re-read `tests/contracts/test_convex_backend_smoke_contract.py`.
- [x] Re-read `tests/contracts/test_nurt_cli_contract.py`.
- [x] Re-read `tests/contracts/test_interactive_tui_contract.py`.
- [x] Re-read `tests/contracts/test_target_matrix_and_auth_contract.py`.
- [x] Re-read `tests/contracts/test_required_preset_matrix_contract.py`.
- [x] Run `date "+%Y-%m-%d %I:%M:%S %p"`.
- [x] Run `btca status`.
- [x] Use `btca ask` for Better Auth + Convex auth-config shape.
- [x] Use `btca ask` for Better Auth self-hosted env/runtime expectations.
- [x] Use `btca ask` for Clerk custom UI support.
- [x] Use official Convex web docs for Clerk integration details because the current `convex-docs` BTCA resource is still an archived stub.

---

## RED

- [x] Add or expand contract tests for explicit local auth provider selection.
- [x] Add or expand contract tests for explicit prod auth provider selection.
- [x] Add or expand contract tests for supported/unsupported auth-matrix validation.
- [x] Add or expand contract tests for default `local=better-auth`, `prod=clerk` behavior where appropriate.
- [x] Add or expand contract tests for compose baseline generation.
- [x] Add or expand contract tests for local override compose generation.
- [x] Add or expand contract tests for provider-neutral auth boundary files.
- [x] Add or expand contract tests for updated backend/web local-dev docs and env templates.
- [x] Expand the existing fullstack/auth/CLI suites instead of introducing a new standalone contract file.

---

## GREEN

- [x] Update CLI flows to collect or accept local/prod auth provider choices for backend-capable setups.
- [x] Support explicit scaffold flags for split auth selection: `--local-auth`, `--prod-auth`, `--backend-local-auth`, and `--backend-prod-auth`.
- [x] Preserve same-provider shorthand through `--auth` and `--backend-auth`.
- [x] Generate the deployment-baseline `compose.yaml`.
- [x] Generate the local override file that adds self-hosted Convex backend/dashboard services.
- [x] Update scaffolded backend/web env examples and docs to match the new local/prod auth/runtime model.
- [x] Replace the old single-provider placeholder model with a provider-neutral web auth boundary and runtime-aware backend auth config.
- [x] Update BTCA generation so backend auth resources cover both sides of the selected local/prod matrix.

---

## BLUE

- [x] Refactor the auth-matrix parsing and provider selection so legacy shorthand and split auth options can coexist cleanly.
- [x] Re-check docs sync across `PROGRESS.md`, `docs/LIVING_DOCS.md`, `docs/ARCHITECTURE.md`, and `TODO-FEATURES.md`.
- [x] Add a new session summary for the implementation slice.
- [x] Refresh bundled snapshot metadata with `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."`.
- [x] Re-run targeted tests, Ruff, and the full suite.

---

## Validation Completed

- [x] `uv run pytest tests/contracts/test_target_matrix_and_auth_contract.py tests/contracts/test_fullstack_auth_wiring_contract.py tests/contracts/test_convex_backend_smoke_contract.py tests/contracts/test_nurt_cli_contract.py tests/contracts/test_required_preset_matrix_contract.py`
- [x] `uv run ruff check src/new_repo_template tests/contracts`
- [x] `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."`
- [x] `uv run pytest`

---

## Remaining RC1 Work

- [ ] Manually validate `local=better-auth`, `prod=clerk` on a generated repo.
- [ ] Manually validate `local=better-auth`, `prod=better-auth` on a generated repo.
- [ ] Manually validate `local=clerk`, `prod=clerk` on a generated repo.
- [ ] Explicitly validate the `local=clerk` plus self-hosted Convex path with authoritative docs and/or empirical runtime checks before calling it RC1-ready.
- [ ] Test that the generated TanStack web app actually boots and runs.
- [ ] Test that the generated backend actually runs against the intended Convex/auth combinations.
- [ ] Continue with the remaining feature `10.0` runtime matrix: Electron, iOS mobile, and TV runtime validation.

---

## Fresh-Context Restart Checklist

- [ ] Read `PLAN.md`.
- [ ] Read `PROGRESS.md`.
- [ ] Read `docs/LIVING_DOCS.md`.
- [ ] Read `docs/ARCHITECTURE.md`.
- [ ] Read `TODO-FEATURES.md`.
- [ ] Read `docs/session-summaries/SESSION_128_SUMMARY.md`.
- [ ] Re-read `src/new_repo_template/scaffold.py`.
- [ ] Re-read `src/new_repo_template/nurt_cli.py`.
- [ ] Re-read `src/new_repo_template/btca_config_manager.py`.
- [ ] Re-read `src/new_repo_template/snapshot_assets/templates/fullstack/backend_readme.md`.
- [ ] Re-read `src/new_repo_template/snapshot_assets/templates/wiring/backend_auth_config.ts`.
- [ ] Re-read `src/new_repo_template/snapshot_assets/templates/wiring/web_app_auth.ts`.
- [ ] Re-read `src/new_repo_template/snapshot_assets/templates/wiring/web_auth_runtime.ts`.
- [ ] Re-read `src/new_repo_template/snapshot_assets/templates/fullstack/compose.yaml`.
- [ ] Re-read `src/new_repo_template/snapshot_assets/templates/fullstack/compose.override.yaml`.
- [ ] Re-read `tests/contracts/test_target_matrix_and_auth_contract.py`.
- [ ] Re-read `tests/contracts/test_fullstack_auth_wiring_contract.py`.
- [ ] Re-read `tests/contracts/test_convex_backend_smoke_contract.py`.
- [ ] Run `date "+%Y-%m-%d %I:%M:%S %p"`.
- [ ] Run `btca status`.
- [ ] Re-check the self-hosted Convex documentation authority issue before treating `local=clerk` as fully validated.

---

## Notes For The Next Session

- [ ] Mention explicitly that the new YELLOW pass included file reads, `btca status`, `btca ask`, and official Convex web-doc lookups.
- [ ] Keep documentation in sync as runtime/manual validation proceeds.
- [ ] Do not overwrite `docs/session-summaries/SESSION_128_SUMMARY.md`; create a newer session summary for the next slice.
