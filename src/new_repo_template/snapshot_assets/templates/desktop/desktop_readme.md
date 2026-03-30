# Desktop App (Electron Forge)

This target scaffolds a dedicated Electron app in `apps/desktop` with a Vite-powered
React renderer and `@tanstack/react-router` using `createHashHistory()` as the default
desktop routing strategy.

## Commands

- `bun run dev` -> CI-safe desktop smoke command
- `bun run desktop:start` -> start Electron in local development mode
- `bun run build` -> CI-safe packaging smoke command
- `bun run desktop:package` -> create local unsigned package artifacts
- `bun run desktop:make` -> build local unsigned distributables

## Shared Foundations

- Shared design tokens live in `packages/design-tokens`.
- Shared copy and route intent live in `packages/shared`.
- Rendered desktop UI stays desktop-specific even while it consumes those shared
  foundations.

## Unsigned Artifacts

Desktop outputs are unsigned by default for internal testing and local validation.
On macOS and Windows, unsigned binaries can trigger security warnings; this is expected
for the current milestone and does not block internal distribution.
