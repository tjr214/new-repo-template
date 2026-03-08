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

## Optional iOS Packaging Commands

When Expo/EAS credentials are configured for a real project, these commands provide non-interactive iOS packaging entrypoints:

- `bun run mobile:build:ios:development`
- `bun run mobile:build:ios:preview`

The default `test` command runs `smoke.test.ts` for a deterministic, device-free baseline.
