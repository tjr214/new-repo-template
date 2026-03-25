from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TextIO

from new_repo_template.ralph_tasks import (
    RalphExecutionSettings,
    RalphTaskPlan,
    load_ralph_task_plan,
    resolve_execution_settings,
    validate_ralph_task_file,
    visualize_ralph_task_file,
)


@dataclass(frozen=True)
class RalphRunSummary:
    succeeded: bool
    completed: bool
    reached_max_loops: bool
    final_loop: int
    task_file: Path
    archived_path: Path | None
    framework: str


def _emit_log(on_log, line: str) -> None:
    if on_log is not None:
        on_log(line)


def _stream_process(
    command: list[str],
    *,
    on_log,
    cwd: Path,
) -> int:
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(f"required command not found: {command[0]}") from exc

    assert process.stdout is not None
    for raw_line in process.stdout:
        line = raw_line.rstrip("\n")
        if line != "":
            _emit_log(on_log, line)
    return process.wait()


def _build_closeout_prompt(
    *,
    task_name: str,
    timestamp: str,
    task_visualization: str,
    task_file: Path,
) -> str:
    return f"""CH. Load the Bmad-Master.

You are running the automated closeout phase for a completed implementation plan.

Context:
- Timestamp: {timestamp}
- Task name: {task_name}
- Task file: {task_file}

Read and study {task_file} in full before executing closeout actions.

{task_visualization}

---

MANDATORY CLOSEOUT CONTRACT
1) BMAD epic and story artifacts are source-of-truth. Keep them intact.
2) DO NOT delete, move, archive, or rename BMAD epic/story artifacts.
3) If product/architecture context is needed, read BMAD markdown files by path.
4) Reconcile implementation state back into BMAD tracking.

Strict Closeout Sequence (execute in exact order):
1. Verify task completion state
   - Read the task status visualization and the task YAML.
   - Confirm task/phases/steps/instructions are all "done".
   - Confirm no item is "blocked".
   - If any item is not done, stop closeout and report exactly which IDs are incomplete.

2. Synchronize BMAD execution records
   - Align story statuses with implementation reality.
   - Align epic status for this exported epic.
   - Update _bmad-output/implementation-artifacts/sprint-status.yaml to final story/epic states.
   - Do not make assumption-based status changes; every status update must be evidence-driven.

3. Update checkpoint documentation
   - Update PROGRESS.md.
   - Update docs/LIVING_DOCS.md.
   - Update docs/ARCHITECTURE.md if implementation changed architecture details.
   - Create a NEW session summary file (never overwrite any existing SESSION_X_SUMMARY.md).

4. Validate integrity gates
   - Validate task YAML with `nurt ralph validate {task_file}`.
   - Run relevant test/lint/build checks used by this repo.
   - If any validation fails, do not claim closeout complete; report concrete failures and required follow-up.

5. Final consistency check
   - Confirm BMAD statuses, documentation updates, and validation/test outcomes are all in sync.
   - Only then report closeout complete.

Important constraints:
- No destructive cleanup of BMAD artifacts.
- No cleanup actions during closeout (delete/move/archive/rename are forbidden).
- No placeholders; use concrete file paths and concrete updates.
- Keep responses concise and action-oriented.
"""


def _build_bmad_prompt(
    *,
    task_name: str,
    timestamp: str,
    task_visualization: str,
    task_file: Path,
) -> str:
    return f"""CH. First, load the Bmad-Master.

1) Task Context (The Who)
You are the implementation agent operating inside of a Ralph agentic coding loop-harness.
Your mission is to execute the task plan safely and incrementally while keeping task status and BMAD tracking aligned.

2) Background Data / Context
<timestamp>{timestamp}</timestamp>
<task_name>{task_name}</task_name>
<task_file>{task_file}</task_file>
<task_yaml_instruction>Read and study {task_file} in full before any implementation work.</task_yaml_instruction>
<task_visualization>{task_visualization}
</task_visualization>
<bmad_context_paths>
- _bmad-output/implementation-artifacts/sprint-status.yaml
- _bmad-output/implementation-artifacts/*.md
- _bmad-output/planning-artifacts/*epic*.md
- _bmad-output/planning/*epic*.md
- _bmad-output/planning-artifacts/prd.md
- _bmad-output/planning/prd.md
- _bmad-output/planning-artifacts/architecture.md
- _bmad-output/planning/architecture.md
</bmad_context_paths>
<bmad_rules>
- BMAD epic and story artifacts are source-of-truth.
- Do not delete, move, archive, or rename BMAD artifacts.
- Use BMAD PRD and architecture markdown as direct read-only context.
</bmad_rules>

3) Detailed Task Description
- Execute with strict YELLOW-RED-GREEN-BLUE TDD discipline.
- Deterministic work selection:
  - If any instruction is active, work the lowest instruction ID first.
  - Else pick the first eligible pending instruction by ID order and set it to active.
  - Process exactly one instruction per loop iteration unless blocked.
- Status transition rules (strict):
  - pending -> active before implementation begins.
  - active -> done only after tests pass, acceptance criteria are satisfied, and validations pass.
  - pending or active -> blocked only with a concrete blocked_reason that includes dependency, evidence, and next action.
  - Never skip directly from pending -> done.
- Blocked discipline:
  - Do not force work on blocked instructions.
  - Do not clear blocked status without concrete evidence that the blocker is resolved.
- YELLOW: read all directly relevant code/tests/config before writing changes.
- RED: create or update tests first and confirm expected failures when applicable.
- GREEN: implement only what is required for current tests and acceptance criteria.
- BLUE: refactor safely, rerun validations, and verify no regressions.
- Keep task status fields in {task_file} accurate at instruction/step/phase/task levels.
- Validate {task_file} after status updates with `nurt ralph validate {task_file}`.
- Preserve project conventions and do not introduce placeholders. Output full code blocks for search/replace operations.

4) Thinking Directive (Measure Twice, Cut Once)
Take all the time you need to think through dependencies and sequencing before acting.
Before writing or modifying any code, complete a full context pass by reading everything required: the task YAML, the visualization context, BMAD epic/story artifacts, sprint status, and relevant PRD/architecture documents.
If YELLOW discovery identifies additional directly related files, read those too before implementing.
Do not start implementation until the read-and-study pass is complete.
"""


def _build_standalone_prompt(
    *,
    task_name: str,
    timestamp: str,
    task_visualization: str,
    task_file: Path,
) -> str:
    return f"""CH. Load the build agent.

1) Task Context (The Who)
You are the implementation agent operating inside of a Ralph agentic coding loop-harness.
Your mission is to execute the task plan safely and incrementally while keeping task status aligned with real implementation progress.

2) Background Data / Context
<timestamp>{timestamp}</timestamp>
<task_name>{task_name}</task_name>
<task_file>{task_file}</task_file>
<task_yaml_instruction>Read and study {task_file} in full before any implementation work.</task_yaml_instruction>
<task_visualization>{task_visualization}
</task_visualization>

3) Detailed Task Description
- Execute with strict YELLOW-RED-GREEN-BLUE TDD discipline.
- Deterministic work selection:
  - If any instruction is active, work the lowest instruction ID first.
  - Else pick the first eligible pending instruction by ID order and set it to active.
  - Process exactly one instruction per loop iteration unless blocked.
- Status transition rules (strict):
  - pending -> active before implementation begins.
  - active -> done only after tests pass, acceptance criteria are satisfied, and validations pass.
  - pending or active -> blocked only with a concrete blocked_reason that includes dependency, evidence, and next action.
  - Never skip directly from pending -> done.
- Blocked discipline:
  - Do not force work on blocked instructions.
  - Do not clear blocked status without concrete evidence that the blocker is resolved.
- YELLOW: read all directly relevant code/tests/config before writing changes.
- RED: create or update tests first and confirm expected failures when applicable.
- GREEN: implement only what is required for current tests and acceptance criteria.
- BLUE: refactor safely, rerun validations, and verify no regressions.
- Keep task status fields in {task_file} accurate at instruction/step/phase/task levels.
- Validate {task_file} after status updates with `nurt ralph validate {task_file}`.
- Preserve project conventions and do not introduce placeholders. Output full code blocks for search/replace operations.

4) Thinking Directive (Measure Twice, Cut Once)
Take all the time you need to think through dependencies and sequencing before acting.
Before writing or modifying any code, complete a full context pass by reading everything required: the task YAML, the visualization context, and any directly related project files needed for the current slice.
If YELLOW discovery identifies additional directly related files, read those too before implementing.
Do not start implementation until the read-and-study pass is complete.
"""


def build_ralph_prompt(
    *,
    plan: RalphTaskPlan,
    settings: RalphExecutionSettings,
    timestamp: str,
    task_visualization: str,
) -> str:
    if settings.framework == "bmad":
        return _build_bmad_prompt(
            task_name=plan.task_name,
            timestamp=timestamp,
            task_visualization=task_visualization,
            task_file=plan.path,
        )

    return _build_standalone_prompt(
        task_name=plan.task_name,
        timestamp=timestamp,
        task_visualization=task_visualization,
        task_file=plan.path,
    )


def render_ralph_dry_run_summary(
    *,
    plan: RalphTaskPlan,
    settings: RalphExecutionSettings,
    model: str,
    max_loops: int,
) -> str:
    closeout_label = "enabled" if settings.bmad_closeout else "disabled"
    return (
        "RALPH execution plan\n"
        f"- Task: {plan.path}\n"
        f"- Framework: {plan.framework}\n"
        f"- Agent: {settings.agent}\n"
        f"- Model: {model}\n"
        f"- Max Loops: {max_loops}\n"
        f"- BMAD Closeout: {closeout_label}\n"
    )


def archive_completed_task_file(task_file: Path) -> Path:
    completed_dir = task_file.parent / "completed"
    completed_dir.mkdir(parents=True, exist_ok=True)
    target_path = completed_dir / task_file.name
    if target_path.exists():
        timestamp_suffix = datetime.now().strftime("%Y%m%d-%H%M%S")
        target_path = (
            completed_dir / f"{task_file.stem}-{timestamp_suffix}{task_file.suffix}"
        )
    task_file.rename(target_path)
    return target_path


def _should_archive_completed_task(
    *,
    task_file: Path,
    no_interactive: bool,
    archive_completed: bool | None,
    stdin: TextIO | None,
) -> bool:
    if archive_completed is not None:
        return archive_completed
    if no_interactive:
        return False

    active_stdin = sys.stdin if stdin is None else stdin
    if not active_stdin.isatty():
        return False

    response = input(
        f"Archive completed task file to {task_file.parent / 'completed'}? [y/N]: "
    )
    return response.strip().lower() in {"y", "yes"}


def run_ralph_loop(
    *,
    task_file: Path,
    model: str,
    max_loops: int,
    cwd: Path,
    on_log=None,
    on_loop_change=None,
    on_visualization=None,
    no_interactive: bool,
    archive_completed: bool | None = None,
    stdin: TextIO | None = None,
) -> RalphRunSummary:
    validation = validate_ralph_task_file(task_file, cwd=cwd)
    if not validation.is_valid:
        raise RuntimeError(validation.output.strip())

    archived_path: Path | None = None
    loop_counter = 1
    latest_plan = load_ralph_task_plan(task_file)
    settings = resolve_execution_settings(latest_plan)

    while True:
        if loop_counter > max_loops:
            _emit_log(
                on_log, f"Maximum iterations reached ({max_loops}). Stopping loop."
            )
            return RalphRunSummary(
                succeeded=False,
                completed=False,
                reached_max_loops=True,
                final_loop=max_loops,
                task_file=task_file,
                archived_path=None,
                framework=settings.framework,
            )

        latest_plan = load_ralph_task_plan(task_file)
        settings = resolve_execution_settings(latest_plan)
        task_visualization = visualize_ralph_task_file(task_file)
        if on_visualization is not None:
            on_visualization(task_visualization)

        if latest_plan.task_status == "done":
            _emit_log(on_log, f"Task completed: {latest_plan.task_name}")
            succeeded = True
            if settings.bmad_closeout and settings.closeout_agent is not None:
                closeout_prompt = _build_closeout_prompt(
                    task_name=latest_plan.task_name,
                    timestamp=datetime.now().strftime("%Y-%m-%d-%I:%M %p"),
                    task_visualization=task_visualization,
                    task_file=task_file,
                )
                closeout_return_code = _stream_process(
                    [
                        "opencode",
                        "run",
                        "-m",
                        model,
                        "--title",
                        f"RALPH: {latest_plan.task_name} [CLOSEOUT PHASE]",
                        "--agent",
                        settings.closeout_agent,
                        closeout_prompt,
                    ],
                    on_log=on_log,
                    cwd=cwd,
                )
                succeeded = closeout_return_code == 0

            if _should_archive_completed_task(
                task_file=task_file,
                no_interactive=no_interactive,
                archive_completed=archive_completed,
                stdin=stdin,
            ):
                archived_path = archive_completed_task_file(task_file)
                _emit_log(on_log, f"Archived task file: {archived_path}")

            return RalphRunSummary(
                succeeded=succeeded,
                completed=True,
                reached_max_loops=False,
                final_loop=max(loop_counter - 1, 0),
                task_file=task_file,
                archived_path=archived_path,
                framework=settings.framework,
            )

        if on_loop_change is not None:
            on_loop_change(loop_counter)

        _emit_log(on_log, f"Loop Number: {loop_counter}")
        _emit_log(on_log, f"Active Task: {latest_plan.task_name} ({task_file})")
        _emit_log(on_log, f"Selected Model: {model}")

        prompt = build_ralph_prompt(
            plan=latest_plan,
            settings=settings,
            timestamp=datetime.now().strftime("%Y-%m-%d-%I:%M %p"),
            task_visualization=task_visualization,
        )
        return_code = _stream_process(
            [
                "opencode",
                "run",
                "-m",
                model,
                "--title",
                f"RALPH: {latest_plan.task_name} [{loop_counter}]",
                "--agent",
                settings.agent,
                prompt,
            ],
            on_log=on_log,
            cwd=cwd,
        )
        if return_code != 0:
            raise RuntimeError(f"opencode run failed with exit code {return_code}")
        loop_counter += 1
