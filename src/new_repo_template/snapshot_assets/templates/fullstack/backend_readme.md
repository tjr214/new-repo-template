# Backend (Convex Local + Cloud)

This backend lane keeps Convex in both environments:

- local development uses self-hosted Convex through `compose.override.yaml`
- production uses Convex Cloud

## Auth Matrix

The scaffold locks this backend to the selected local/prod auth matrix:

- local: `{{LOCAL_AUTH_PROVIDER}}`
- prod: `{{PROD_AUTH_PROVIDER}}`

The supported provider set for this scaffold remains Convex + Clerk and Convex + Better Auth.

Keep `apps/web/.env.example` and `apps/backend/.env.example` aligned to the same runtime matrix.

## Local Development

1. Install workspace dependencies from repo root:
   - `bun install`
2. Review the generated compose files:
   - `compose.yaml`
   - `compose.override.yaml`
   - the base file is the deployment-oriented baseline; the override carries local source mounts, local dependency installation, and self-hosted Convex persistence
3. Update `apps/backend/.env.example` and `apps/web/.env.example` with the generated local values you need.
4. Start the local stack from the repo root:
   - `docker compose up`
   - the web service installs Linux-native Bun dependencies into a Docker-managed volume on first startup
   - self-hosted Convex persists its local data in a named Docker volume
5. Run Convex codegen as needed from `apps/backend`:
   - `bun run convex:codegen`

## Production Direction

- Production continues to target Convex Cloud.
- The generated `convex/auth.config.ts` switches between the local/prod auth providers using `NURT_RUNTIME_ENV`.

## CI-Safe Credentialless Smoke Commands

These commands are used by baseline CI and do not require Convex credentials:

- `bun run convex:codegen:smoke`
- `bun run convex:dev:smoke`
