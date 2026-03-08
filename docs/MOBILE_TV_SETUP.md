# Mobile + TV Setup

This template scaffolds mobile and TV as separate Expo apps:

- `apps/mobile` for handheld/mobile workflows
- `apps/tv` for AndroidTV workflows

TV-specific plugin/config wiring stays isolated to `apps/tv`.

## Scaffold Command

Example:

```bash
nurt new my-mobile-tv-app --target mobile --target tv --no-interactive
```

## Mobile Validation (CI-safe)

From `apps/mobile`:

- `bun run lint`
- `bun run typecheck`
- `bun run test`

Smoke alternatives already scaffolded:

- `bun run mobile:lint:smoke`
- `bun run mobile:start:smoke`
- `bun run mobile:export:smoke`

## TV Validation (CI-safe + manual)

From `apps/tv`:

- `bun run lint`
- `bun run typecheck`
- `bun run test`
- `bun run tv:android` (local emulator/device build + install)

`tv:android` now includes a compatibility preflight for local Android TV runs:

- runs `expo prebuild --clean --platform android`
- patches the generated Android wrapper to Gradle `8.14.3`
- executes `expo run:android --no-install` with community autolinking enabled

TV build-profile scripts:

- `bun run tv:build:development`
- `bun run tv:build:preview`

Manual validation:

1. Android TV Emulator pass
   - verify remote-primary focus and D-pad navigation
2. NVIDIA Shield pass
   - verify remote-primary behavior
   - verify keyboard/mouse/gamepad fallback behavior

Use both files during manual validation:

- `apps/tv/TV_INPUT_CHECKLIST.md` for checklist completion
- `apps/tv/TV_VALIDATION_LOG.md` for run metadata, pass/fail status, and evidence links

## Caveats

- Do not merge TV plugin/config into `apps/mobile`.
- Keep remote-first behavior as the primary TV UX contract.
- Treat keyboard/mouse/gamepad as fallback paths that must not break remote focus state.
