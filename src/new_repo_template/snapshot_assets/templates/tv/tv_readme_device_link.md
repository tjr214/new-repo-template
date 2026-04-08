# TV Setup

This app is the dedicated Expo AndroidTV baseline for the generated monorepo.

Feature `14.0` changes the unauthenticated TV surface when this repo also includes `web + backend`: the TV app now starts on a QR-first pairing screen instead of the earlier multi-card operator-console layout.

## Local Setup

1. Install workspace dependencies from repo root:
   - `bun install --frozen-lockfile`
2. Review `apps/tv/.env.example` and set the verification URL you want the QR code to use.
3. Start TV app locally from repo root:
   - `bun run --cwd apps/tv tv:start`
4. Run Android TV app build/install from repo root:
   - `bun run --cwd apps/tv tv:android`

`tv:android` runs a deterministic compatibility flow before build/install:

- regenerates Android native project with Expo prebuild
- patches `android/gradle/wrapper/gradle-wrapper.properties` to Gradle `8.14.3`
- uses community autolinking mode during `expo run:android`

If your host shell does not expose Java by default, set `JAVA_HOME` to a local JDK 17+ runtime before running `tv:android`.

## Device-Link Starter Contract

The starter TV app now shows:

- a QR code for `verification_uri_complete`
- visible `verification_uri` fallback text
- visible `user_code` fallback text
- polling/expiry status
- one focusable `Refresh code` control

Customize these values through `apps/tv/.env.example`:

- `EXPO_PUBLIC_DEVICE_LINK_BASE_URL`
- `EXPO_PUBLIC_DEVICE_LINK_EXPIRES_IN_SECONDS`
- `EXPO_PUBLIC_DEVICE_LINK_POLL_INTERVAL_SECONDS`
- `EXPO_PUBLIC_DEVICE_LINK_DEMO_AUTO_LINK`

The generated screen is a starter baseline. Replace the local demo behavior with real backend polling and app-session persistence when you wire the live device-link flow.

## Build Profiles

- Development APK: `bun run --cwd apps/tv tv:build:development`
- Preview APK: `bun run --cwd apps/tv tv:build:preview`

## Validation Flow

Run TV validation in three steps:

1. CI-safe baseline scripts from `apps/tv`:
   - `bun run lint`
   - `bun run typecheck`
   - `bun run test`
2. Android TV Emulator pass (QR rendering, remote-primary pairing-screen focus, and expiry/refresh behavior)
3. NVIDIA Shield pass (remote-primary plus keyboard/mouse/gamepad fallback checks)

Use `TV_INPUT_CHECKLIST.md` for checklist execution and `TV_VALIDATION_LOG.md` to record outcomes.
