# Backend (Convex Local + Cloud)

This backend lane keeps Convex in both environments:

- local development uses self-hosted Convex through `compose.override.yaml`
- production uses Convex Cloud

## Auth Matrix

The scaffold locks this backend to the selected local/prod auth matrix:

- local: `clerk`
- prod: `clerk`

The supported provider set for this scaffold remains Convex + Clerk and Convex + Better Auth.

Keep `apps/web/.env.example`, `apps/backend/backend/.env.example`, and `apps/tv/.env.example` aligned to the same local pairing URL shape.

## Device-Link Starter Contract

Feature `14.0` adds the starter files for a provider-neutral TV device-link flow:

- `convex/deviceLink.ts` defines the backend-owned device-link payload and status contract.
- `convex/schema.ts` now reserves a `deviceLinks` table for short-lived linking records.
- `convex/http.ts` records the intended route inventory:
  - `POST /device/code`
  - `POST /device/approve`
  - `POST /device/token`

Replace the route inventory with real Convex handlers when you wire the live auth/session layer.

## Local Development

1. Install workspace dependencies from repo root:
   - `bun install`
2. Review the generated compose files:
   - `compose.yaml`
   - `compose.override.yaml`
   - the base file is the deployment-oriented baseline; the override carries local source mounts, local dependency installation, and self-hosted Convex persistence
3. Update `apps/backend/backend/.env.example`, `apps/web/.env.example`, and `apps/tv/.env.example` with the generated local values you need.
4. Start the local stack from the repo root:
   - `docker compose up`
   - the web service installs Linux-native Bun dependencies into a Docker-managed volume on first startup
   - self-hosted Convex persists its local data in a named Docker volume
5. Run Convex codegen as needed from `apps/backend/backend`:
   - `bun run convex:codegen`

## Production Direction

- Production continues to target Convex Cloud.
- The generated `convex/auth.config.ts` switches between the local/prod auth providers using `NURT_RUNTIME_ENV`.

## CI-Safe Credentialless Smoke Commands

These commands are used by baseline CI and do not require Convex credentials:

- `bun run convex:codegen:smoke`
- `bun run convex:dev:smoke`
