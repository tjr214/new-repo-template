# TV Setup

This app is the dedicated Expo AndroidTV baseline for the generated monorepo.

## Local Setup

1. Install workspace dependencies from repo root:
   - `bun install --frozen-lockfile`
2. Start TV app locally from repo root:
   - `bun run --cwd apps/tv tv:start`
3. Run Android TV app build/install from repo root:
   - `bun run --cwd apps/tv tv:android`

`tv:android` runs a deterministic compatibility flow before build/install:

- regenerates Android native project with Expo prebuild
- patches `android/gradle/wrapper/gradle-wrapper.properties` to Gradle `8.14.3`
- uses community autolinking mode during `expo run:android`

If your host shell does not expose Java by default, set `JAVA_HOME` to a local JDK 17+ runtime before running `tv:android`.

## Build Profiles

- Development APK: `bun run --cwd apps/tv tv:build:development`
- Preview APK: `bun run --cwd apps/tv tv:build:preview`

## Validation Flow

Run TV validation in three steps:

1. CI-safe baseline scripts from `apps/tv`:
   - `bun run lint`
   - `bun run typecheck`
   - `bun run test`
2. Android TV Emulator pass (remote-primary navigation and focus checks)
3. NVIDIA Shield pass (remote-primary plus keyboard/mouse/gamepad fallback checks)

Use `TV_INPUT_CHECKLIST.md` for checklist execution and `TV_VALIDATION_LOG.md` to record outcomes.
