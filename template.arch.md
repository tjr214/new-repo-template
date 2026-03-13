# [PROJECT NAME GOES HERE] Architecture

## Scope

This repository is [describe the system, product, or template under design].

The target architecture is [describe the intended operating model, deployment model, or repository shape].

Key product or platform lanes:

- [Lane or target 1]
- [Lane or target 2]
- [Lane or target 3]

## Core Decisions

- Repository/workspace model: [single package, monorepo, multi-repo, etc.]
- Orchestration/build system: [tool or n/a]
- Package/dependency management: [tooling choice]
- Primary runtime languages: [Python, TypeScript, etc.]
- Backend/data architecture: [decision]
- Auth integration mode: [decision]
- Packaging/distribution model: [decision]
- CI/CD platform: [decision]
- Platform support policy: [decision]
- Version/lockfile policy: [decision]
- Scaffold/generator contract: [decision or n/a]
- Write/failure model: [decision]
- Metadata/config boundary: [decision]
- Security baseline: [decision]
- Primary user or developer entrypoint: [decision]

## Planned Topology

- Root layout: [for example `apps/*`, `packages/*`, `services/*`]
- Shared packages/libraries: [describe]
- App/service boundaries: [describe]
- External integrations: [describe]

## Current Implementation Status

- Milestone or release status: [current state]
- Planning/archive state: [active plan, progress tracker, session summary, or archive references]
- Supported targets/workspaces: [list current supported outputs or surfaces]
- Current command/runtime entrypoints: [list key commands or operator paths]
- Packaging/release posture: [state]
- Outstanding gaps or deferred items:
  - [Gap or follow-up 1]
  - [Gap or follow-up 2]

## Validation Model

Implementation follows a strict YELLOW-RED-GREEN-BLUE loop:

- YELLOW: read the relevant repo files, docs, and test surfaces first; use BTCA-backed asks when dependency or framework context matters
- RED: add or update failing tests or contracts first
- GREEN: implement the smallest change set that satisfies the slice
- BLUE: refactor, harden, and rerun validation

DoD is enforced by [tests, contracts, CI gates, review policy, or equivalent].

Baseline CI model:

- [credentialless checks, matrix coverage, protected-branch rules, release gates, etc.]

Current contract or verification coverage:

- `[path/to/test_or_check]`
  - Contract intent: [describe]
- `[path/to/test_or_check]`
  - Contract intent: [describe]
- Add additional entries as needed.
