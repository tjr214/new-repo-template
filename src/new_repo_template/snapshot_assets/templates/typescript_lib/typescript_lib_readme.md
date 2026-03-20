# TypeScript Library Setup

This package is the reusable TypeScript library baseline for the generated monorepo.

## Local Setup

1. Install workspace dependencies from repo root:
   - `bun install --frozen-lockfile`
2. Work inside `packages/typescript` for package-local scripts.

## Baseline developer commands

- `bun run build`
- `bun run test`
- `bun run lint`
- `bun run typecheck`

The package is scaffolded with `exports`, `types`, and `dist` output so it can be published later.
