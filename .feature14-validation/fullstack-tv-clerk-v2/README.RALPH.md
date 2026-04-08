# RALPH Guide

RALPH is the autonomous execution loop for framework-aware task YAML files.

## When To Use RALPH

- You have an exported task file under `docs/tasks/`.
- You want implementation to run from that task definition with minimal supervision.
- The task file explicitly declares `metadata.framework: bmad` or `metadata.framework: standalone`.

## Prepare The Task Input

If you want a BMAD-backed task file, run:

`/project-export-bmad-to-ralph`

Important: the export flow is epic/story-centered, uses those artifacts as the source of truth, and should emit `metadata.framework: bmad`.

Standalone Ralph task files should instead declare `metadata.framework: standalone`.

## Run The Loop

Run:

`nurt ralph`

This opens the fullscreen Ralph TUI, detects available task files, lets you pick a configured model, and lets you adjust the loop limit before the run starts.

To run a specific task file directly:

`nurt ralph run docs/tasks/<task-file>.yaml`

BMAD tasks run BMAD closeout automatically when the task reaches `done`. Standalone tasks skip BMAD closeout.

Utility commands:

- `nurt ralph validate docs/tasks/<task-file>.yaml`
- `nurt ralph visualize docs/tasks/<task-file>.yaml`

## Typical Flow

1. Plan in `README.BMAD-GUIDE.md` when the work is BMAD-driven.
2. Export BMAD artifacts to `docs/tasks/<task-file>.yaml`, or author a standalone task file with `metadata.framework: standalone`.
3. Run `nurt ralph` or `nurt ralph run docs/tasks/<task-file>.yaml`.
4. Review the loop logs and, for BMAD tasks, review the BMAD closeout results.

## Ralph Config

RALPH reads configuration from:

1. `./ralph.config.yaml`
2. the user-level `nurt` config directory
3. built-in defaults

The config controls the available models, the default model, and the default `max_loops` value.

## Practical Rule of Thumb

- Use BMAD when you are shaping the work and want BMAD-aware closeout.
- Use standalone Ralph tasks when the work is already planned and does not need BMAD context.
