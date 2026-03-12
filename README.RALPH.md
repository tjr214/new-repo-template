# RALPH Guide

RALPH is the autonomous execution loop used after BMAD planning has been exported into a task YAML.

## When To Use RALPH

- You already completed the BMAD planning lane.
- You have an exported task file under `docs/tasks/`.
- You want implementation to run from that task definition with minimal supervision.

## Prepare The Task Input

If you have not exported a task yet, run:

`@.opencode/command/project-export-bmad-to-ralph.md`

Important: the export flow is epic/story-centered and uses those artifacts as the source of truth.

## Run The Loop

Run:

`./scripts/RALPH.sh docs/tasks/<task-file>.yaml`

RALPH will iterate implementation and then run closeout synchronization back into BMAD tracking.

## Typical Flow

1. Plan in `README.BMAD-GUIDE.md`.
2. Export BMAD artifacts to `docs/tasks/<task-file>.yaml`.
3. Run `./scripts/RALPH.sh docs/tasks/<task-file>.yaml`.
4. Review the closeout sync results in the BMAD tracking artifacts.

## Practical Rule of Thumb

- Use BMAD when you are shaping the work.
- Use RALPH when the work is already planned and ready for execution.
