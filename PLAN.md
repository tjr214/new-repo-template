# Feature 10.0 Pre-Build Plan

**Last Updated:** 2026-03-29 08:08:46 PM
**Status:** Discussion locked / ready for implementation YELLOW
**Previous Session Summary:** `docs/session-summaries/SESSION_126_SUMMARY.md`
**Current Planning Summary:** `docs/session-summaries/SESSION_127_SUMMARY.md`

---

## Goal

Lock the release-candidate `10.0` implementation plan before coding, with enough detail that a fresh-context restart can resume directly into the next YELLOW pass.

The first execution slice is `web + backend` local-dev/auth validation. This slice must establish the local/prod topology, compose model, auth-provider boundary, and validation order that the later desktop/mobile/TV/manual RC1 checks will build on.

---

## Why This Is Next

- `TODO-FEATURES.md` shows features `1.0` through `9.0` complete.
- The only remaining roadmap item is `10.0 FINAL TESTS BEFORE RELEASE CANDIDATE 1`.
- The highest-leverage first step inside `10.0` is the web/backend local-dev/auth path because it exercises the shared Convex/auth/runtime contracts that the rest of the platform validations depend on.

---

## YELLOW Pass Completed In This Session

This planning session already completed the required YELLOW pass before any documentation edits.

### Files Read During YELLOW

- `PLAN.md`
- `PROGRESS.md`
- `docs/LIVING_DOCS.md`
- `docs/ARCHITECTURE.md`
- `TODO-FEATURES.md`
- `docs/session-summaries/SESSION_126_SUMMARY.md`
- `src/new_repo_template/scaffold.py` (auth/fullstack sections)
- `src/new_repo_template/snapshot_assets/templates/fullstack/backend_readme.md`
- `src/new_repo_template/snapshot_assets/templates/wiring/backend_auth_config.ts`
- `src/new_repo_template/snapshot_assets/templates/wiring/web_auth_provider_clerk.ts`
- `src/new_repo_template/snapshot_assets/templates/wiring/web_auth_client_better_auth.ts`

### BTCA Checks Run During YELLOW

- `btca status`
- `btca ask -r clerk-docs -q "Do Clerk development and production instances keep users separate" --sub-agent`
- Attempted additional BTCA lookups around self-hosted Convex + Clerk viability

### YELLOW Findings

- Clerk development and production instances keep users separate by default. This addresses the concern about local/dev users conflating with production users.
- Clerk widgets are not required. Clerk supports custom UI and custom auth flows, which means the scaffold does not need to hard-code Clerk widgets to use Clerk in production.
- Better Auth is the practical route for truly offline local auth when paired with self-hosted Convex.
- The current project `convex-docs` BTCA resource is insufficient for self-hosted auth research because it is an archived stub. The next implementation YELLOW pass must use authoritative docs for self-hosted Convex or update the BTCA resource set with user confirmation.
- The `clerk-docs` resource intermittently fetches successfully. One lookup succeeded and one failed. Treat Clerk-specific BTCA lookups as usable but not perfectly reliable until the next session confirms stability.

---

## Locked Decisions

- Feature `10.0` is the next roadmap item.
- The first implementation slice is `web + backend` local-dev/auth validation.
- Convex is mandatory in all environments.
- Local development always uses self-hosted Convex via the official Docker image in a local compose override.
- Production always uses Convex Cloud.
- The base `compose.yaml` is the deployment baseline.
- Local development uses an override compose file to add self-hosted/local-only services.
- Local startup UX should be one command from the repo root.
- Auth is always integrated through the Convex path for the chosen provider.
- Generated apps should expose a provider-neutral auth boundary instead of coupling app code to Clerk widgets.
- The supported RC1 auth combinations are:
  - `local=better-auth`, `prod=clerk`
  - `local=better-auth`, `prod=better-auth`
  - `local=clerk`, `prod=clerk`
- The unsupported combination is:
  - `local=clerk`, `prod=better-auth`
- The default generated-repo auth posture for the next slice is `local=better-auth`, `prod=clerk`.
- Local Clerk mode remains a valid supported path, but it is not the offline path. Only local Better Auth is expected to satisfy true offline local development.

---

## Explicit Non-Goals For The Next Slice

- Do not support `local=clerk`, `prod=better-auth`.
- Do not make the scaffold depend on Clerk widgets as the core auth UI surface.
- Do not start by implementing platform-specific runtime fixes for desktop/mobile/TV before the web/backend local-dev/auth foundation is updated.
- Do not change the repo's always-Convex direction.
- Do not assume self-hosted Convex + Clerk local viability without verification just because it is a desired supported combination.
- Do not promise offline local development when the local auth provider is Clerk.
- Do not collapse local and prod auth/user stores into one system; provider-neutral means app-contract neutrality, not shared identity storage.

---

## Current Gaps Between Locked Direction And Current Scaffold

- The current CLI/scaffold model exposes only a single backend auth choice (`clerk`, `better-auth`, or `none`). It does not yet support separate local/prod provider selection.
- The current fullstack backend README is explicitly cloud-first and does not mention compose-based local self-hosted Convex.
- The current auth wiring templates are placeholders, not a provider-neutral app auth boundary.
- The current templates do not define a deployment-baseline `compose.yaml` plus local override model.
- The current docs do not yet describe the three supported RC1 local/prod auth combinations.
- The current BTCA `convex-docs` resource does not provide authoritative self-hosted documentation.

---

## Risks And Validation Gaps

- Highest risk: self-hosted Convex + Clerk local compatibility is still not confirmed from authoritative docs in the current BTCA resource set.
- Medium risk: the local/prod auth matrix may require generator changes across CLI prompts, TUI prompts, env templates, scaffold templates, and contract coverage rather than just one code path.
- Medium risk: the compose baseline may need to distinguish clearly between deployable services and local-only infrastructure so the deployment file stays useful instead of becoming local-dev-only.
- Medium risk: provider-neutral auth is only safe if generated app code uses a narrow shared contract rather than direct vendor-specific APIs.

---

## Next Execution Plan

### YELLOW

- Re-read the restart file set listed below.
- Re-read the current implementation surfaces:
  - `src/new_repo_template/scaffold.py`
  - `src/new_repo_template/nurt_cli.py`
  - `src/new_repo_template/interactive_ui.py`
  - `src/new_repo_template/interactive_tui.py`
  - `src/new_repo_template/add_mode.py`
  - `src/new_repo_template/btca_config_manager.py`
  - `src/new_repo_template/snapshot_assets/templates/fullstack/backend_readme.md`
  - `src/new_repo_template/snapshot_assets/templates/wiring/backend_auth_config.ts`
  - `src/new_repo_template/snapshot_assets/templates/wiring/web_auth_provider_clerk.ts`
  - `src/new_repo_template/snapshot_assets/templates/wiring/web_auth_client_better_auth.ts`
  - `src/new_repo_template/snapshot_assets/templates/workspace_packages/backend_package.json`
- Re-read the current contract surfaces most likely to change:
  - `tests/contracts/test_fullstack_auth_wiring_contract.py`
  - `tests/contracts/test_convex_backend_smoke_contract.py`
  - `tests/contracts/test_nurt_cli_contract.py`
  - `tests/contracts/test_interactive_tui_contract.py`
  - `tests/contracts/test_target_matrix_and_auth_contract.py`
  - `tests/contracts/test_required_preset_matrix_contract.py`
- Run `btca status` again.
- Re-run the Clerk separation query if needed:
  - `btca ask -r clerk-docs -q "Do Clerk development and production instances keep users separate" --sub-agent`
- Obtain authoritative self-hosted Convex guidance before coding the local Clerk path. If the current BTCA resource is still insufficient, either:
  - use official docs via direct fetch for the implementation session, or
  - propose updating/adding the Convex docs BTCA resource with explicit user confirmation.

### RED

- Add or expand contract tests for:
  - explicit local auth provider selection
  - explicit prod auth provider selection
  - supported/unsupported auth-matrix validation
  - default `local=better-auth`, `prod=clerk` behavior where appropriate
  - compose baseline generation
  - local override compose generation
  - provider-neutral auth boundary files
  - updated backend/web local-dev docs and env templates
- Decide whether to introduce new contract files or expand existing fullstack/auth/CLI suites.

### GREEN

- Update CLI/TUI flows to collect local/prod auth provider choices for backend-capable setups.
- Generate the deployment-baseline `compose.yaml`.
- Generate the local override file that adds self-hosted Convex and any other required local services.
- Update scaffolded backend/web env examples and docs to match the new local/prod auth/runtime model.
- Replace placeholder auth wiring with a provider-neutral app boundary appropriate for the supported RC1 matrix.

### BLUE

- Refactor any awkward generator branching introduced by the new auth matrix.
- Re-check docs sync across `PROGRESS.md`, `docs/LIVING_DOCS.md`, `docs/ARCHITECTURE.md`, and `TODO-FEATURES.md`.
- Add a new session summary for the implementation slice.
- Re-run targeted tests and then the full suite.

---

## Expected Validation Path After Implementation Starts

- Targeted contracts for the touched CLI/TUI/fullstack surfaces.
- Full repository test suite: `uv run pytest`
- Targeted scaffold smoke on the generated web/backend combinations.
- Manual/runtime validation order after the first slice lands:
  1. `local=better-auth`, `prod=clerk`
  2. `local=better-auth`, `prod=better-auth`
  3. `local=clerk`, `prod=clerk`
- Only after the web/backend local-dev/auth foundation is credible should the RC1 pass move on to desktop, mobile, and TV runtime testing.

---

## Fresh-Context Restart Checklist

If the context window is cleared, do this before making changes:

1. Read these files in order:
   - `PLAN.md`
   - `PROGRESS.md`
   - `docs/LIVING_DOCS.md`
   - `docs/ARCHITECTURE.md`
   - `TODO-FEATURES.md`
   - `docs/session-summaries/SESSION_127_SUMMARY.md`
2. Re-read the implementation files most relevant to the next slice:
   - `src/new_repo_template/scaffold.py`
   - `src/new_repo_template/nurt_cli.py`
   - `src/new_repo_template/interactive_ui.py`
   - `src/new_repo_template/interactive_tui.py`
   - `src/new_repo_template/add_mode.py`
   - `src/new_repo_template/snapshot_assets/templates/fullstack/backend_readme.md`
   - `src/new_repo_template/snapshot_assets/templates/wiring/backend_auth_config.ts`
   - `src/new_repo_template/snapshot_assets/templates/wiring/web_auth_provider_clerk.ts`
   - `src/new_repo_template/snapshot_assets/templates/wiring/web_auth_client_better_auth.ts`
   - `src/new_repo_template/snapshot_assets/templates/workspace_packages/backend_package.json`
3. Re-read the likely contract surfaces:
   - `tests/contracts/test_fullstack_auth_wiring_contract.py`
   - `tests/contracts/test_convex_backend_smoke_contract.py`
   - `tests/contracts/test_nurt_cli_contract.py`
   - `tests/contracts/test_interactive_tui_contract.py`
   - `tests/contracts/test_target_matrix_and_auth_contract.py`
4. Run the mandatory YELLOW commands:
   - `date "+%Y-%m-%d %I:%M:%S %p"`
   - `btca status`
5. Re-run BTCA/library guidance before finalizing implementation details:
   - `btca ask -r clerk-docs -q "Do Clerk development and production instances keep users separate" --sub-agent`
   - Re-check authoritative self-hosted Convex guidance for the local Convex path before treating `local=clerk` as verified.
6. Start RED only after the above is complete.

---

## Notes For The Next Session

- Mention explicitly that the YELLOW pass included file reads, `btca status`, and `btca ask` usage.
- Keep documentation in sync as implementation advances.
- Do not overwrite `docs/session-summaries/SESSION_127_SUMMARY.md`; create a newer session summary when coding begins.
