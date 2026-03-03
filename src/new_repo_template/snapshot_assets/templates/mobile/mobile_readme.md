# Mobile Setup

This app is the dedicated Expo mobile baseline for the generated monorepo.

## Local Setup

1. Install workspace dependencies from repo root:
   - `bun install --frozen-lockfile`
2. Start mobile app locally from repo root:
   - `bun --cwd apps/mobile run mobile:start`

## CI-Safe Validation Commands

Run these from `apps/mobile` for non-interactive baseline verification:

- `bun run lint`
- `bun run typecheck`
- `bun run test`

Additional smoke helpers:

- `bun run mobile:lint:smoke`
- `bun run mobile:start:smoke`
- `bun run mobile:export:smoke`

The default `test` command runs `smoke.test.ts` for a deterministic, device-free baseline.
