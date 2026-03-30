# Session 128 Summary

## Date and Time

2026-03-29 08:20:28 PM

## Scope

Implemented feature `10.0` slice 1 for generated `web + backend` repos: split local/prod auth scaffolding, provider-neutral web auth boundary files, runtime-aware backend auth config, and compose-based local self-hosted Convex assets.

## YELLOW Pass

- Re-read `PLAN.md`, `PROGRESS.md`, `docs/LIVING_DOCS.md`, `docs/ARCHITECTURE.md`, `TODO-FEATURES.md`, and `docs/session-summaries/SESSION_127_SUMMARY.md` before editing code.
- Re-read the current scaffold/CLI/auth implementation files and the current fullstack/auth contract suites.
- Ran `btca status`.
- Used `btca ask` for Better Auth + Convex auth-config shape, Better Auth self-hosted env/runtime expectations, and Clerk custom-UI support.
- Used official Convex web docs for Clerk integration details because the current BTCA `convex-docs` resource is still an archived stub.

## Implementation

- Extended `src/new_repo_template/scaffold.py` to support split local/prod auth configuration for backend projects, while preserving same-provider shorthand through legacy auth flags.
- Extended `src/new_repo_template/nurt_cli.py` so `nurt new` can drive the same split auth model.
- Updated `src/new_repo_template/btca_config_manager.py` so backend auth resources are derived from both sides of the selected local/prod auth matrix.
- Replaced the old single-provider fullstack placeholder model with generated provider-neutral web auth boundary files (`app-auth.ts`, `auth-runtime.ts`) plus provider-specific placeholder modules only when needed.
- Updated generated backend auth config to switch by `NURT_RUNTIME_ENV` between Clerk and Better Auth wiring.
- Added generated `compose.yaml` and `compose.override.yaml` for `web+backend` repos, with the local override carrying the self-hosted Convex backend/dashboard services.
- Updated generated backend/web `.env.example` files and `apps/backend/README.md` to document the local self-hosted Convex path and the local/prod auth matrix.

## RED / BLUE Coverage

- Expanded the auth/runtime contract suites to cover split auth validation, unsupported auth-matrix rejection, provider-neutral auth boundary files, mixed-provider fullstack scaffolds, compose generation, and updated local-dev docs/env placeholders.
- Refreshed bundled snapshot metadata with `nurt template-assets validate` after adding the new template files.

## Validation

- `uv run pytest tests/contracts/test_target_matrix_and_auth_contract.py tests/contracts/test_fullstack_auth_wiring_contract.py tests/contracts/test_convex_backend_smoke_contract.py tests/contracts/test_nurt_cli_contract.py tests/contracts/test_required_preset_matrix_contract.py`
- `uv run ruff check src/new_repo_template tests/contracts`
- `uv run python -m new_repo_template.nurt_cli template-assets validate --source-root "."`
- `uv run pytest`

## Outcome

- Feature `10.0` slice 1 is now implemented and fully green in automated validation.
- The next RC1 work is no longer scaffold/CLI planning for this slice; it is manual/runtime validation of the three supported generated auth combinations and then the remaining platform runtime checks.
