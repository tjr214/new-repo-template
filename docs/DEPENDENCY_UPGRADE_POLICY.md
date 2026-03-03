# Dependency Upgrade and Versioning Policy

This policy defines how template dependency versions are maintained during M5 hardening.

## Goals

- Keep generated repos stable and deterministic.
- Keep dependency drift visible and intentional.
- Preserve fast update flow for maintainers.

## Cadence

- weekly: review and apply patch/minor dependency updates for template-owned runtime and tooling dependencies.
- monthly: review core toolchain baselines (`bun`, `turbo`, `typescript`, `python`) and refresh known-good versions when needed.
- Quarterly or on demand: plan major upgrades as explicit migration slices.
- Immediate: security updates with known CVEs bypass normal cadence.

## Version Range Rules

- Internal workspace dependencies must use `workspace:*`.
- JS/TS dependencies in template manifests use `^` ranges.
- Python dependencies must remain compatible with Python `>=3.14`.
- Determinism is provided by committed lockfiles, not by freezing every dependency spec to an exact version.

## Lockfile Governance

- `bun.lock` and `uv.lock` are required and must be committed when dependency manifests change.
- CI must validate lockfile presence and version baseline freshness.
- Mixed JavaScript lockfiles (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`) are not allowed in this template.

## Maintainer Commands

- Validate baseline metadata + lockfiles + latest checks:
  - `uv run nurt versions check --check-lockfiles --check-latest`
- Refresh baseline metadata and regenerate lockfiles:
  - `uv run nurt versions update`
- Preview version/lockfile changes without mutation:
  - `uv run nurt versions update --dry-run`

## PR Expectations

- Dependency update PRs must include:
  - updated baseline metadata (when relevant)
  - regenerated lockfiles
  - CI pass across required jobs
- Upgrade PR descriptions should summarize risk and rollback path.

## CI Alignment

- `Version Baseline Guardrail` enforces baseline and lockfile policy.
- `Preset Regression Suite` validates high-signal scaffold combinations after updates.
