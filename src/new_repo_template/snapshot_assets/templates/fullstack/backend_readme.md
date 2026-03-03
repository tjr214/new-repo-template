# Backend (Convex Cloud-First)

This backend lane is scaffolded for a cloud-first Convex workflow.

## Auth Decision Flow

Set `AUTH_PROVIDER` in `apps/backend/.env.example` to one of:

- `clerk` (Clerk)
- `better-auth` (Better Auth)

Keep `apps/web/.env.example` and `apps/backend/.env.example` aligned to the same auth mode.

## Local Development

1. Install workspace dependencies from repo root:
   - `bun install`
2. Configure environment variables:
   - update `apps/backend/.env.example` values (`CONVEX_DEPLOYMENT`, `AUTH_PROVIDER`, provider-specific vars)
3. Run Convex codegen as needed:
   - `bun run convex:codegen`
4. Start Convex cloud dev loop:
   - `bun run convex:dev`

## CI-Safe Credentialless Smoke Commands

These commands are used by baseline CI and do not require Convex credentials:

- `bun run convex:codegen:smoke`
- `bun run convex:dev:smoke`
