# Optional Signing Pipeline

This document defines the signing design for release hardening.

Signing is disabled by default for normal development and baseline CI.

The current implementation lives in the template repo release workflow and provides secret-gated preflight/signing-prep lanes plus unsigned template release artifacts. Downstream generated app repos still need repo-specific packaging and signing execution for their own desktop/mobile/TV artifacts.

## Disabled-by-Default Model

- Default path: unsigned artifacts remain valid for internal testing and milestone validation.
- Signing is enabled only through manual release workflow dispatch with explicit input.
- No signing secrets are required for `CI` workflow execution.

## Workflow Entry Point

- Workflow: `.github/workflows/release.yml`
- Trigger: `workflow_dispatch`
- Signing gate input: `enable_signing`
  - default: `false`
  - signing jobs run only when `enable_signing=true`
- Unsigned artifact lane: `Unsigned Release Readiness` builds template distributables and uploads a release bundle via `actions/upload-artifact@v4`.
- Optional signing-prep lanes:
  - `Desktop Signing Prep`
  - `Android Signing Prep`

## Secrets Map

Configure these repository secrets only when enabling signing.

### Desktop (macOS code signing/notarization)

- `MACOS_CERTIFICATE_P12_BASE64`
- `MACOS_CERTIFICATE_PASSWORD`
- `APPLE_DEVELOPER_ID`
- `APPLE_TEAM_ID`

Optional for notarization tooling flows (if used):

- `APPLE_NOTARY_APPLE_ID`
- `APPLE_NOTARY_APP_PASSWORD`

### Android (Expo/TV signing)

- `ANDROID_KEYSTORE_BASE64`
- `ANDROID_KEYSTORE_PASSWORD`
- `ANDROID_KEY_ALIAS`
- `ANDROID_KEY_PASSWORD`

## Enablement Steps

1. Add required secrets in repository settings.
2. Run `Release (Optional Signing)` via `workflow_dispatch`.
3. Set `enable_signing` to `true`.
4. Confirm the release workflow validates required secrets before signing steps.
5. Keep unsigned artifact paths available for fallback/internal distribution.
6. Treat the template workflow as signing-prep infrastructure; implement repo-specific build/sign commands in downstream generated app repos before public distribution.

## Safety Rules

- Never print secret values in logs.
- Keep signing jobs out of required PR checks until fully hardened.
- Keep this file synchronized with workflow inputs, secret names, and release policy docs.
- Use uploaded prep artifacts for operator/debug validation only; they must not contain secrets.

## Unsigned Artifact Trust/Warning Expectations

- Unsigned desktop artifacts will show platform trust warnings and should be treated as internal-distribution builds.
- Release notes must explicitly call out whether artifacts are signed or unsigned.
- Unsigned paths remain valid for development phases, but external/public distribution should use signed artifacts.
