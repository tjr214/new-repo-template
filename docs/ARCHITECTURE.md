# Architecture

## Scope

This repository is a project template that generates new repositories. The template itself is the system under design.

The target architecture is an always-on monorepo template that can scaffold:
- Web fullstack apps (TanStack Start + Convex)
- Desktop apps (Electron)
- Mobile apps (Expo, dedicated app)
- TV apps (Expo AndroidTV, dedicated app separate from mobile)
- Python-oriented projects (CLI/TUI-first)

## Core Decisions

- Monorepo orchestration: Turborepo (`turbo`)
- JS/TS package manager and workspaces: Bun
- Auth integration mode for Convex fullstack scaffolds: explicit prompt (`clerk` or `better-auth`)
- Auth selection rule: any scaffold selecting both `web` and `backend` must explicitly choose auth
- Desktop packaging tool: Electron Forge
- Convex workflow: cloud-first
- CI platform: GitHub Actions
- Platform support policy: native macOS + Linux + Windows (WSL optional supplemental only)
- Version policy: latest known-good baseline in template, deterministic lockfile state in generated repos
- Scaffold contract: explicit preset-combination matrix and deterministic non-interactive CLI behavior
- Generator write model: failure-atomic scaffolding (transactional writes or cleanup-on-failure)
- TV input contract: remote-primary navigation with keyboard/mouse/gamepad support as secondary inputs
- Root metadata invariant: `pyproject.toml` exists at repository root for all generated repos regardless of selected targets
- Python lane metadata boundary: Python app metadata/deps live in lane-local `apps/python/pyproject.toml`, while root `pyproject.toml` remains monorepo/tooling-level

## Planned Topology

- Root workspace with `apps/*` and `packages/*`
- Shared packages for config and reusable code
- Selectable target generators within an always-on monorepo shell

## Current Implementation Status

- Milestone M0 is active.
- Project BTCA resource layer is now configured for the locked dependency set in `PLAN.md`.
- Initial contract-test harness now exists under `tests/` with a first RED test for monorepo foundation dry-run behavior.
- The initial RED test is now GREEN via a bootstrap CLI implementation at `src/new_repo_template/scaffold.py`.
- Python lane RED/GREEN slice is complete with `tests/contracts/test_python_lane_contract.py`.
- Current scaffold implementation supports `foundation` and `python` targets with non-interactive mode and dry-run support.

## Validation Model

Implementation follows a strict YELLOW-RED-GREEN-BLUE loop:
- YELLOW: read/lookup first (including BTCA resource-backed asks)
- RED: failing contract tests for scaffold output
- GREEN: minimal implementation to pass tests
- BLUE: refactor and harden

DoD is enforced by contract tests under `tests/` plus CI matrix checks across Linux/macOS/Windows.

Baseline CI is credentialless for cloud-first Convex wiring checks; credential-dependent deployment tests are optional and separately gated.

Current RED anchor test:

- `tests/contracts/test_monorepo_foundation_contract.py`
  - Contract intent: non-interactive `--dry-run` foundation scaffold path succeeds, reports monorepo shape (`apps`, `packages`, `pyproject.toml`), and writes no files.
- `tests/contracts/test_python_lane_contract.py`
  - Contract intent: Python target dry-run and write flows preserve root/lane pyproject separation (`pyproject.toml` and `apps/python/pyproject.toml`).
