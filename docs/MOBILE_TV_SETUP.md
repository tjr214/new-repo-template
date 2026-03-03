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

- `expo lint`
- `tsc --noEmit`
- `expo export --non-interactive`

Smoke alternatives already scaffolded:

- `bun run mobile:start:smoke`
- `bun run mobile:export:smoke`

## TV Validation (CI-safe + manual)

From `apps/tv`:

- `expo lint`
- `tsc --noEmit`
- `expo export --non-interactive`

TV build-profile scripts:

- `bun run tv:build:development`
- `bun run tv:build:preview`

Manual validation:

1. Android TV Emulator pass
   - verify remote-primary focus and D-pad navigation
2. NVIDIA Shield pass
   - verify remote-primary behavior
   - verify keyboard/mouse/gamepad fallback behavior

Use `apps/tv/TV_INPUT_CHECKLIST.md` to track pass/fail notes for both passes.

## Caveats

- Do not merge TV plugin/config into `apps/mobile`.
- Keep remote-first behavior as the primary TV UX contract.
- Treat keyboard/mouse/gamepad as fallback paths that must not break remote focus state.
