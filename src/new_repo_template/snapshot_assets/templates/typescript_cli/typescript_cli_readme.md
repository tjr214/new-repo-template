# TypeScript CLI Setup

This app is the dedicated Bun-native TypeScript CLI baseline for the generated monorepo.

## Local Setup

1. Install workspace dependencies from repo root:
   - `bun install --frozen-lockfile`
2. Run the CLI locally from `apps/typescript-cli`:
   - `bun run dev -- --help`

## Baseline developer commands

- `bun run build`
- `bun run test`
- `bun run lint`
- `bun run typecheck`

The package also exposes a `bin` entry so the CLI can be linked as `typescript-cli` inside Bun workspaces.
