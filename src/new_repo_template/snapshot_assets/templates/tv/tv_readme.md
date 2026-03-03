# TV Setup

This app is the dedicated Expo AndroidTV baseline for the generated monorepo.

## Local Setup

1. Install workspace dependencies from repo root:
   - `bun install --frozen-lockfile`
2. Start TV app locally from repo root:
   - `bun --cwd apps/tv run tv:start`

## Build Profiles

- Development APK: `bun --cwd apps/tv run tv:build:development`
- Preview APK: `bun --cwd apps/tv run tv:build:preview`

## Validation Flow

Run TV validation in three steps:

1. CI-safe baseline scripts from `apps/tv`:
   - `bun run lint`
   - `bun run typecheck`
   - `bun run test`
2. Android TV Emulator pass (remote-primary navigation and focus checks)
3. NVIDIA Shield pass (remote-primary plus keyboard/mouse/gamepad fallback checks)

Use `TV_INPUT_CHECKLIST.md` for checklist execution and `TV_VALIDATION_LOG.md` to record outcomes.
