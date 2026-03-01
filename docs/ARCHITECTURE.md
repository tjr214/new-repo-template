# Architecture

## Scope

This repository is a project template that generates new repositories. The template itself is the system under design.

The target architecture is an always-on monorepo template that can scaffold:
- Web fullstack apps (TanStack Start + Convex)
- Desktop apps (Electron)
- Mobile apps (Expo, including AndroidTV path)
- Python-oriented projects (CLI/TUI-first)

## Core Decisions

- Monorepo orchestration: Turborepo (`turbo`)
- JS/TS package manager and workspaces: Bun
- Auth integration mode for Convex fullstack scaffolds: explicit prompt (`clerk` or `better-auth`)
- Desktop packaging tool: Electron Forge
- Convex workflow: cloud-first
- CI platform: GitHub Actions
- Platform support policy: native macOS + Linux + Windows (WSL optional supplemental only)

## Planned Topology

- Root workspace with `apps/*` and `packages/*`
- Shared packages for config and reusable code
- Selectable target generators within an always-on monorepo shell

## Validation Model

Implementation follows a strict YELLOW-RED-GREEN-BLUE loop:
- YELLOW: read/lookup first (including BTCA resource-backed asks)
- RED: failing contract tests for scaffold output
- GREEN: minimal implementation to pass tests
- BLUE: refactor and harden

DoD is enforced by contract tests under `tests/` plus CI matrix checks across Linux/macOS/Windows.
