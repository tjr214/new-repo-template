# Fullstack Setup (Web + Backend)

This template's fullstack lane is cloud-first and targets `web + backend` with an explicit auth choice.

## Auth Decision Flow

When selecting both `web` and `backend`, choose exactly one auth provider:

- `clerk`
- `better-auth`

The selected provider must be reflected in both `apps/web/.env.example` and `apps/backend/.env.example`.

## Scaffold Command

Example:

```bash
nurt new my-fullstack-app --target web --target backend --auth clerk --no-interactive
```

## Cloud-First Local Dev Flow

From generated repo root:

1. Install workspace dependencies:
   - `bun install`
2. Configure `.env.example` values for web/backend (especially `CONVEX_DEPLOYMENT`, `AUTH_PROVIDER`, and auth-provider-specific variables).
3. Generate Convex artifacts as needed:
   - `bun run --cwd apps/backend convex:codegen`
4. Start Convex dev loop:
   - `bun run --cwd apps/backend convex:dev`
5. Start app workspace dev tasks as needed:
   - `bun run dev`

## CI-Safe Smoke Path (No Secrets)

Baseline CI intentionally stays credentialless and uses help-command smokes:

- `bun run --cwd apps/backend convex:codegen:smoke`
- `bun run --cwd apps/backend convex:dev:smoke`

These verify Convex CLI wiring without requiring Convex login, `CONVEX_DEPLOY_KEY`, or third-party auth keys.

## Optional Advanced Path

Credential-dependent Convex workflows (for example, authenticated deploy and real cloud-connected dev loops with non-placeholder credentials) are optional advanced checks and are intentionally not part of baseline CI.
