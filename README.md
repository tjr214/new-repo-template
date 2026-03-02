# BMAD + RALPH Workflow Guide

This repo supports two delivery lanes:

1. Quick lane (`quick-spec` -> `quick-dev`) for fast, interactive shipping.
2. Full lane (brainstorm -> PRD -> architecture -> epics/stories -> sprint -> export -> RALPH loop) for larger autonomous execution.

Use this guide to choose the right lane and run the right commands.

## Template Bootstrap (User Flow)

For end users generating a new project from this template, the canonical flow is the global `nurt` CLI.

1. Install `nurt` from git:
   - `uv tool install --from git+https://github.com/<org>/<repo>.git nurt`
2. Generate a project:
   - `nurt new <project-name>`

`install.sh` is retained for internal/legacy maintenance workflows, not as the primary end-user bootstrap path.

For fullstack template setup/auth flow details, see `docs/FULLSTACK_SETUP.md`.

## Which Lane Should I Use?

### Use Quick Lane (`quick-spec` / `quick-dev`) when:

- You are at the console and want to drive the work now.
- Scope is small-to-medium and bounded.
- You want lightweight planning plus rapid implementation.
- You do not need full epic/story governance before coding starts.

### Use Full Lane (BMad planning -> RALPH) when:

- Work is large, multi-phase, or cross-cutting.
- You want comprehensive planning artifacts before implementation.
- You want epic/story tracking and sprint status as the source of truth.
- You want to hand execution to the RALPH loop with minimal supervision.

## Quick Lane: How To Use `quick-spec` and `quick-dev`

### Step 1: Create a tech spec

Run:

`@.opencode/command/bmad-bmm-quick-spec.md`

Then describe the feature/change. The workflow will:

- Investigate relevant code.
- Build an implementation-ready tech spec.
- Save it under `_bmad-output/implementation-artifacts/tech-spec-<slug>.md`.

### Step 2: Implement from the tech spec

Run:

`@.opencode/command/bmad-bmm-quick-dev.md`

Then provide either:

- A tech-spec path (recommended), for example:
  - `quick-dev _bmad-output/implementation-artifacts/tech-spec-my-feature.md`
- Or direct instructions for a simple task.

Notes:

- `quick-dev` can escalate you back to planning if scope looks too large.
- Quick lane does not automatically convert tech specs into epic/story artifacts.

## Full Lane: Planning to Autonomous RALPH Execution

Run these in order for comprehensive planning and autonomous implementation.

### 1) Brainstorm

`@.opencode/command/bmad-core-brainstorming.md`

### 2) Create or update PRD

`@.opencode/command/bmad-bmm-prd.md`

Tip: This PRD workflow supports create/validate/edit modes. Use it both for first drafts and updates.

### 3) Create or update architecture

`@.opencode/command/bmad-bmm-create-architecture.md`

Tip: Re-run this workflow to evolve architecture decisions as scope changes.

### 4) Generate epics and stories

`@.opencode/command/bmad-bmm-create-epics-and-stories.md`

### 5) Generate sprint status tracking

`@.opencode/command/bmad-bmm-sprint-planning.md`

Optional status check command:

`@.opencode/command/bmad-bmm-sprint-status.md`

### 6) Export BMad artifacts to RALPH task YAML

`@.opencode/command/project-export-bmad-to-ralph.md`

Important: current export workflow is epic/story-centered and uses these artifacts as source of truth.

### 7) Run RALPH loop

`./scripts/RALPH.sh docs/tasks/<task-file>.yaml`

RALPH will iterate implementation and then run closeout synchronization back into BMad tracking.

## Command Cheat Sheet

- Brainstorm: `@.opencode/command/bmad-core-brainstorming.md`
- PRD (create/update): `@.opencode/command/bmad-bmm-prd.md`
- Architecture (create/update): `@.opencode/command/bmad-bmm-create-architecture.md`
- Epics + stories: `@.opencode/command/bmad-bmm-create-epics-and-stories.md`
- Sprint generation: `@.opencode/command/bmad-bmm-sprint-planning.md`
- Sprint status view: `@.opencode/command/bmad-bmm-sprint-status.md`
- Export to RALPH: `@.opencode/command/project-export-bmad-to-ralph.md`
- Quick spec: `@.opencode/command/bmad-bmm-quick-spec.md`
- Quick dev: `@.opencode/command/bmad-bmm-quick-dev.md`

## Practical Rule of Thumb

- If you are saying, "I need this done now while I supervise," pick quick lane.
- If you are saying, "I want thorough planning and then mostly autonomous execution," pick full lane.
