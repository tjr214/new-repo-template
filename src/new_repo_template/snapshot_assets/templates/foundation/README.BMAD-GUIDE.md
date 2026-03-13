# BMAD Guide

This repo supports two BMAD delivery lanes:

1. Quick lane (`quick-spec` -> `quick-dev`) for fast, interactive shipping.
2. Full lane (brainstorm -> PRD -> architecture -> epics/stories -> sprint -> export) for larger planned work before RALPH execution.

Use this guide to choose the right BMAD lane and run the right planning commands.

## Which Lane Should I Use?

### Use Quick Lane (`quick-spec` / `quick-dev`) when:

- You are at the console and want to drive the work now.
- Scope is small-to-medium and bounded.
- You want lightweight planning plus rapid implementation.
- You do not need full epic/story governance before coding starts.

### Use Full Lane (BMAD planning lane) when:

- Work is large, multi-phase, or cross-cutting.
- You want comprehensive planning artifacts before implementation.
- You want epic/story tracking and sprint status as the source of truth.
- You want to hand execution off only after planning is complete.

## Quick Lane: How To Use `quick-spec` and `quick-dev`

### Step 1: Create a tech spec

Run:

`/bmad-bmm-quick-spec`

Then describe the feature/change. The workflow will:

- Investigate relevant code.
- Build an implementation-ready tech spec.
- Save it under `_bmad-output/implementation-artifacts/tech-spec-<slug>.md`.

### Step 2: Implement from the tech spec

Run:

`/bmad-bmm-quick-dev`

Then provide either:

- A tech-spec path (recommended), for example:
  - `quick-dev _bmad-output/implementation-artifacts/tech-spec-my-feature.md`
- Or direct instructions for a simple task.

Notes:

- `quick-dev` can escalate you back to planning if scope looks too large.
- Quick lane does not automatically convert tech specs into epic/story artifacts.

## Full Lane: BMAD Planning Flow

Run these in order for comprehensive planning before export.

### 1) Brainstorm

`/bmad-core-brainstorming`

### 2) Create or update PRD

`/bmad-bmm-prd`

Tip: This PRD workflow supports create/validate/edit modes. Use it both for first drafts and updates.

### 3) Create or update architecture

`/bmad-bmm-create-architecture`

Tip: Re-run this workflow to evolve architecture decisions as scope changes.

### 4) Generate epics and stories

`/bmad-bmm-create-epics-and-stories`

### 5) Generate sprint status tracking

`/bmad-bmm-sprint-planning`

Optional status check command:

`/bmad-bmm-sprint-status`

### 6) Export BMAD artifacts to RALPH task YAML

`/project-export-bmad-to-ralph`

Important: the current export workflow is epic/story-centered and uses those artifacts as the source of truth.

## Command Cheat Sheet

- Brainstorm: `/bmad-core-brainstorming`
- PRD (create/update): `/bmad-bmm-prd`
- Architecture (create/update): `/bmad-bmm-create-architecture`
- Epics + stories: `/bmad-bmm-create-epics-and-stories`
- Sprint generation: `/bmad-bmm-sprint-planning`
- Sprint status view: `/bmad-bmm-sprint-status`
- Export to RALPH: `/project-export-bmad-to-ralph`
- Quick spec: `/bmad-bmm-quick-spec`
- Quick dev: `/bmad-bmm-quick-dev`

## Practical Rule of Thumb

- If you are saying, "I need this done now while I supervise," pick quick lane.
- If you are saying, "I want thorough planning before execution," pick full lane.

## Next Step After Export

Once export produces a task file under `docs/tasks/`, switch to `README.RALPH.md` for the execution loop.
