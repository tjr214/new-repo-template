# Living Docs

## Current State

The template is in planning-to-implementation transition for a major expansion:
- Always-on monorepo support
- Fullstack web support
- Desktop support
- Mobile and AndroidTV support

The canonical execution checklist is in `PLAN.md`.

## Active Implementation Rules

- Follow YELLOW-RED-GREEN-BLUE for each implementation slice.
- Use BTCA resource-backed lookups during YELLOW before coding.
- Keep this file, `docs/ARCHITECTURE.md`, and `PROGRESS.md` synchronized during implementation.

## Decisions Snapshot

- Monorepo always-on: yes
- Turbo + Bun: yes
- Convex: cloud-first default
- Auth mode: explicit choice required (`clerk` or `better-auth`)
- Desktop frontend: dedicated Electron app (Forge)
- Mobile: Expo with AndroidTV path
- CI: GitHub Actions with required native Windows checks
- Signing: deferred to hardening; unsigned internal builds allowed in early phases
- Versioning: template tracks latest known-good versions, generated repos lock deterministic install state via lockfiles
- Convex CI baseline: credentialless wiring checks only (no external secrets required)

## Known Constraints

- BTCA project resources are approved and must be added/synced before implementation research begins in earnest.
- Native Windows validation must not be replaced by WSL-only checks.
- AndroidTV support includes emulator automation plus manual Shield checklist.
- Fullstack auth choice has no default and must be explicitly selected in non-interactive runs.
