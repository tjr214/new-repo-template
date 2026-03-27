from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import yaml
from jsonschema import SchemaError, ValidationError, validate

from new_repo_template.snapshot_assets_loader import load_template_text


STATUS_ICONS = {"pending": "⭕", "active": "🔵", "blocked": "🔴", "done": "✅"}
STATUS_NAMES = {
    "pending": "PENDING",
    "active": "ACTIVE",
    "blocked": "BLOCKED",
    "done": "DONE",
}
FRAMEWORK_VALUES = {"bmad", "standalone"}


@dataclass(frozen=True)
class RalphTaskPlan:
    path: Path
    framework: str
    task_name: str
    task_status: str
    data: dict[str, object]


@dataclass(frozen=True)
class RalphExecutionSettings:
    framework: str
    agent: str
    bmad_closeout: bool
    closeout_agent: str | None


@dataclass(frozen=True)
class RalphValidationResult:
    is_valid: bool
    output: str
    schema_path: Path | None


@dataclass(frozen=True)
class RalphDashboardEntry:
    kind: str
    item_id: str
    title: str
    status: str
    blocked_reason: str | None


@dataclass(frozen=True)
class RalphDashboardSnapshot:
    task_name: str
    framework: str
    task_status: str
    done_count: int
    active_count: int
    blocked_count: int
    pending_count: int
    percent_complete: float
    active_items: tuple[RalphDashboardEntry, ...]
    blocked_items: tuple[RalphDashboardEntry, ...]
    up_next_items: tuple[RalphDashboardEntry, ...]
    recent_completions: tuple[RalphDashboardEntry, ...]


def discover_ralph_task_files(project_root: Path) -> tuple[Path, ...]:
    tasks_root = project_root / "docs" / "tasks"
    if not tasks_root.exists():
        return ()

    return tuple(
        sorted(
            path
            for path in tasks_root.glob("*.yaml")
            if path.name not in {"task-template.yaml", "task-template-example.yaml"}
        )
    )


def _read_yaml_mapping(path: Path) -> dict[str, object]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"YAML parsing error in {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be an object in {path}")
    return data


def _load_packaged_schema() -> dict[str, object]:
    schema_text = load_template_text("foundation/docs/tasks/task-template-schema.json")
    schema_obj = json.loads(schema_text)
    if not isinstance(schema_obj, dict):
        raise ValueError("packaged Ralph task schema must be a JSON object")
    return schema_obj


def resolve_task_schema_path(
    *,
    task_file: Path,
    cwd: Path,
    explicit_schema_path: Path | None = None,
) -> Path | None:
    if explicit_schema_path is not None:
        return explicit_schema_path

    local_schema = cwd / "docs" / "tasks" / "task-template-schema.json"
    if local_schema.exists():
        return local_schema

    sibling_schema = task_file.parent / "task-template-schema.json"
    if sibling_schema.exists():
        return sibling_schema

    return None


def load_ralph_task_plan(task_file: Path) -> RalphTaskPlan:
    data = _read_yaml_mapping(task_file)

    metadata = data.get("metadata")
    if not isinstance(metadata, dict):
        raise ValueError(f"metadata must be an object in {task_file}")

    framework = metadata.get("framework")
    if not isinstance(framework, str) or framework not in FRAMEWORK_VALUES:
        raise ValueError(
            f"metadata.framework must be one of {sorted(FRAMEWORK_VALUES)} in {task_file}"
        )

    task_obj = data.get("task")
    if not isinstance(task_obj, dict):
        raise ValueError(f"task must be an object in {task_file}")

    task_name = task_obj.get("name")
    task_status = task_obj.get("status")
    if not isinstance(task_name, str) or task_name.strip() == "":
        raise ValueError(f"task.name must be a non-empty string in {task_file}")
    if not isinstance(task_status, str) or task_status.strip() == "":
        raise ValueError(f"task.status must be a non-empty string in {task_file}")

    return RalphTaskPlan(
        path=task_file,
        framework=framework,
        task_name=task_name,
        task_status=task_status,
        data=data,
    )


def resolve_execution_settings(plan: RalphTaskPlan) -> RalphExecutionSettings:
    if plan.framework == "bmad":
        return RalphExecutionSettings(
            framework=plan.framework,
            agent="bmad-master",
            bmad_closeout=True,
            closeout_agent="bmad-master",
        )

    return RalphExecutionSettings(
        framework=plan.framework,
        agent="build",
        bmad_closeout=False,
        closeout_agent=None,
    )


def _count_phase_items(phase: dict[str, object]) -> tuple[int, int]:
    total_steps = 0
    total_instructions = 0

    steps_obj = phase.get("steps", [])
    if isinstance(steps_obj, list):
        total_steps += len(steps_obj)
        for step_obj in steps_obj:
            if isinstance(step_obj, dict):
                instructions_obj = step_obj.get("instructions", [])
                if isinstance(instructions_obj, list):
                    total_instructions += len(instructions_obj)

    sub_phases_obj = phase.get("sub_phases", [])
    if isinstance(sub_phases_obj, list):
        for sub_phase_obj in sub_phases_obj:
            if isinstance(sub_phase_obj, dict):
                sub_steps, sub_instructions = _count_phase_items(sub_phase_obj)
                total_steps += sub_steps
                total_instructions += sub_instructions

    return total_steps, total_instructions


def validate_ralph_task_file(
    task_file: Path,
    *,
    cwd: Path | None = None,
    schema_path: Path | None = None,
) -> RalphValidationResult:
    active_cwd = task_file.parent.parent.parent if cwd is None else cwd
    resolved_schema_path = resolve_task_schema_path(
        task_file=task_file,
        cwd=active_cwd,
        explicit_schema_path=schema_path,
    )

    output_lines = [f"📄 Loading template: {task_file}"]
    try:
        template = _read_yaml_mapping(task_file)
        if resolved_schema_path is not None:
            output_lines.append(f"📋 Loading schema: {resolved_schema_path}")
            schema = json.loads(resolved_schema_path.read_text(encoding="utf-8"))
        else:
            output_lines.append("📋 Loading schema: bundled Ralph task schema")
            schema = _load_packaged_schema()

        if not isinstance(schema, dict):
            raise ValueError("schema must be a JSON object")

        output_lines.append("🔍 Validating...")
        validate(instance=template, schema=schema)

        task_obj = template.get("task")
        if not isinstance(task_obj, dict):
            raise ValueError("task must be an object")
        phases_obj = task_obj.get("phases")
        if not isinstance(phases_obj, list):
            raise ValueError("task.phases must be a list")

        total_steps = 0
        total_instructions = 0
        for phase_obj in phases_obj:
            if isinstance(phase_obj, dict):
                phase_steps, phase_instructions = _count_phase_items(phase_obj)
                total_steps += phase_steps
                total_instructions += phase_instructions

        output_lines.extend(
            [
                "✅ Template is VALID!",
                "",
                "📊 Template Summary:",
                f"   Task: {task_obj.get('name')}",
                f"   Status: {task_obj.get('status')}",
                f"   Phases: {len(phases_obj)}",
                f"   Steps: {total_steps}",
                f"   Instructions: {total_instructions}",
            ]
        )
        return RalphValidationResult(
            is_valid=True,
            output="\n".join(output_lines).strip() + "\n",
            schema_path=resolved_schema_path,
        )
    except FileNotFoundError as exc:
        output_lines.append(f"❌ File not found: {exc}")
    except yaml.YAMLError as exc:
        output_lines.append(f"❌ YAML parsing error: {exc}")
    except SchemaError as exc:
        output_lines.append(f"❌ Schema error: {exc}")
    except ValidationError as exc:
        output_lines.append("❌ Validation error:")
        path_text = " -> ".join(str(part) for part in exc.path)
        output_lines.append(f"   Path: {path_text}")
        output_lines.append(f"   Message: {exc.message}")
        if exc.context:
            output_lines.append("   Context:")
            for context_error in exc.context:
                output_lines.append(f"     - {context_error.message}")
    except Exception as exc:
        output_lines.append(f"❌ Unexpected error: {exc}")

    return RalphValidationResult(
        is_valid=False,
        output="\n".join(output_lines).strip() + "\n",
        schema_path=resolved_schema_path,
    )


def _count_statuses_in_phase(phase: dict[str, object]) -> dict[str, int]:
    counts = {"pending": 0, "active": 0, "blocked": 0, "done": 0}
    phase_status = phase.get("status", "pending")
    if isinstance(phase_status, str):
        counts[phase_status] = counts.get(phase_status, 0) + 1

    steps_obj = phase.get("steps", [])
    if isinstance(steps_obj, list):
        for step_obj in steps_obj:
            if not isinstance(step_obj, dict):
                continue
            step_status = step_obj.get("status", "pending")
            if isinstance(step_status, str):
                counts[step_status] = counts.get(step_status, 0) + 1
            instructions_obj = step_obj.get("instructions", [])
            if isinstance(instructions_obj, list):
                for instruction_obj in instructions_obj:
                    if not isinstance(instruction_obj, dict):
                        continue
                    instruction_status = instruction_obj.get("status", "pending")
                    if isinstance(instruction_status, str):
                        counts[instruction_status] = (
                            counts.get(instruction_status, 0) + 1
                        )

    sub_phases_obj = phase.get("sub_phases", [])
    if isinstance(sub_phases_obj, list):
        for sub_phase_obj in sub_phases_obj:
            if not isinstance(sub_phase_obj, dict):
                continue
            sub_counts = _count_statuses_in_phase(sub_phase_obj)
            for status_name, count in sub_counts.items():
                counts[status_name] = counts.get(status_name, 0) + count

    return counts


def _append_instruction_lines(
    lines: list[str], instruction: dict[str, object], indent: str
) -> None:
    instruction_status = instruction.get("status", "pending")
    status_icon = STATUS_ICONS.get(str(instruction_status), "❓")
    instruction_id = instruction.get("id", "unknown")
    content = instruction.get("content", "")
    first_line = content.split("\n")[0].strip() if isinstance(content, str) else ""
    if len(first_line) > 60:
        first_line = first_line[:57] + "..."
    lines.append(f"{indent}  {status_icon} {instruction_id}: {first_line}")
    blocked_reason = instruction.get("blocked_reason")
    if instruction.get("status") == "blocked" and isinstance(blocked_reason, str):
        lines.append(f"{indent}     ⚠️  {blocked_reason}")


def _append_step_lines(lines: list[str], step: dict[str, object], indent: str) -> None:
    step_status = step.get("status", "pending")
    status_icon = STATUS_ICONS.get(str(step_status), "❓")
    step_id = step.get("id", "unknown")
    step_name = step.get("name", "Unnamed")
    lines.append(f"{indent}{status_icon} {step_id}: {step_name}")
    blocked_reason = step.get("blocked_reason")
    if step.get("status") == "blocked" and isinstance(blocked_reason, str):
        lines.append(f"{indent}   ⚠️  {blocked_reason}")

    instructions_obj = step.get("instructions", [])
    if isinstance(instructions_obj, list):
        for instruction_obj in instructions_obj:
            if isinstance(instruction_obj, dict):
                _append_instruction_lines(lines, instruction_obj, indent + "  ")


def _append_phase_lines(
    lines: list[str], phase: dict[str, object], indent: str = ""
) -> None:
    phase_status = phase.get("status", "pending")
    status_icon = STATUS_ICONS.get(str(phase_status), "❓")
    phase_id = phase.get("id", "unknown")
    phase_name = phase.get("name", "Unnamed")
    lines.append("")
    lines.append(f"{indent}{status_icon} {phase_id}: {phase_name}")
    blocked_reason = phase.get("blocked_reason")
    if phase.get("status") == "blocked" and isinstance(blocked_reason, str):
        lines.append(f"{indent}   ⚠️  {blocked_reason}")

    steps_obj = phase.get("steps", [])
    if isinstance(steps_obj, list):
        for step_obj in steps_obj:
            if isinstance(step_obj, dict):
                _append_step_lines(lines, step_obj, indent + "  ")

    sub_phases_obj = phase.get("sub_phases", [])
    if isinstance(sub_phases_obj, list):
        for sub_phase_obj in sub_phases_obj:
            if isinstance(sub_phase_obj, dict):
                _append_phase_lines(lines, sub_phase_obj, indent + "  ")


def _instruction_title(instruction: dict[str, object]) -> str:
    content = instruction.get("content", "")
    first_line = content.split("\n")[0].strip() if isinstance(content, str) else ""
    if len(first_line) > 90:
        return first_line[:87] + "..."
    return first_line or "Instruction"


def _build_dashboard_entries_for_step(
    entries: list[RalphDashboardEntry],
    step: dict[str, object],
) -> None:
    step_status = step.get("status", "pending")
    entries.append(
        RalphDashboardEntry(
            kind="Step",
            item_id=str(step.get("id", "unknown")),
            title=str(step.get("name", "Unnamed")),
            status=str(step_status),
            blocked_reason=(
                str(step.get("blocked_reason"))
                if step.get("blocked_reason") is not None
                else None
            ),
        )
    )

    instructions_obj = step.get("instructions", [])
    if isinstance(instructions_obj, list):
        for instruction_obj in instructions_obj:
            if not isinstance(instruction_obj, dict):
                continue
            instruction_status = instruction_obj.get("status", "pending")
            entries.append(
                RalphDashboardEntry(
                    kind="Instruction",
                    item_id=str(instruction_obj.get("id", "unknown")),
                    title=_instruction_title(instruction_obj),
                    status=str(instruction_status),
                    blocked_reason=(
                        str(instruction_obj.get("blocked_reason"))
                        if instruction_obj.get("blocked_reason") is not None
                        else None
                    ),
                )
            )


def _build_dashboard_entries_for_phase(
    entries: list[RalphDashboardEntry],
    phase: dict[str, object],
) -> None:
    phase_status = phase.get("status", "pending")
    entries.append(
        RalphDashboardEntry(
            kind="Phase",
            item_id=str(phase.get("id", "unknown")),
            title=str(phase.get("name", "Unnamed")),
            status=str(phase_status),
            blocked_reason=(
                str(phase.get("blocked_reason"))
                if phase.get("blocked_reason") is not None
                else None
            ),
        )
    )

    steps_obj = phase.get("steps", [])
    if isinstance(steps_obj, list):
        for step_obj in steps_obj:
            if isinstance(step_obj, dict):
                _build_dashboard_entries_for_step(entries, step_obj)

    sub_phases_obj = phase.get("sub_phases", [])
    if isinstance(sub_phases_obj, list):
        for sub_phase_obj in sub_phases_obj:
            if isinstance(sub_phase_obj, dict):
                _build_dashboard_entries_for_phase(entries, sub_phase_obj)


def build_ralph_dashboard_snapshot(task_file: Path) -> RalphDashboardSnapshot:
    data = _read_yaml_mapping(task_file)
    metadata = data.get("metadata", {})
    task_obj = data.get("task", {})
    if not isinstance(metadata, dict) or not isinstance(task_obj, dict):
        raise ValueError(f"invalid Ralph task structure in {task_file}")

    overall_counts = {"pending": 0, "active": 0, "blocked": 0, "done": 0}
    phases_obj = task_obj.get("phases", [])
    if isinstance(phases_obj, list):
        for phase_obj in phases_obj:
            if not isinstance(phase_obj, dict):
                continue
            phase_counts = _count_statuses_in_phase(phase_obj)
            for status_name, count in phase_counts.items():
                overall_counts[status_name] = overall_counts.get(status_name, 0) + count

    entries: list[RalphDashboardEntry] = []
    if isinstance(phases_obj, list):
        for phase_obj in phases_obj:
            if isinstance(phase_obj, dict):
                _build_dashboard_entries_for_phase(entries, phase_obj)

    active_items = tuple(entry for entry in entries if entry.status == "active")
    blocked_items = tuple(entry for entry in entries if entry.status == "blocked")
    up_next_items = tuple(entry for entry in entries if entry.status == "pending")[:5]
    recent_completions = tuple(entry for entry in entries if entry.status == "done")[
        -5:
    ]
    recent_completions = tuple(reversed(recent_completions))

    total_count = sum(overall_counts.values())
    percent_complete = (
        (overall_counts.get("done", 0) / total_count) * 100 if total_count > 0 else 0.0
    )

    return RalphDashboardSnapshot(
        task_name=str(task_obj.get("name", "Unnamed")),
        framework=str(metadata.get("framework", "N/A")),
        task_status=str(task_obj.get("status", "pending")),
        done_count=overall_counts.get("done", 0),
        active_count=overall_counts.get("active", 0),
        blocked_count=overall_counts.get("blocked", 0),
        pending_count=overall_counts.get("pending", 0),
        percent_complete=percent_complete,
        active_items=active_items,
        blocked_items=blocked_items,
        up_next_items=up_next_items,
        recent_completions=recent_completions,
    )


def _entry_markdown_line(entry: RalphDashboardEntry) -> str:
    return f"- **{entry.kind} {entry.item_id}** - {entry.title}"


def render_ralph_dashboard_markdown(task_file: Path) -> str:
    snapshot = build_ralph_dashboard_snapshot(task_file)
    lines = [
        f"# {snapshot.task_name}",
        "",
        "## Overview",
        f"- **Framework:** `{snapshot.framework}`",
        f"- **Task Status:** {STATUS_ICONS.get(snapshot.task_status, '❓')} {STATUS_NAMES.get(snapshot.task_status, snapshot.task_status.upper())}",
        f"- **Progress:** {snapshot.percent_complete:.1f}% complete",
        (
            f"- **Counts:** ✅ {snapshot.done_count} done / 🔵 {snapshot.active_count} active / "
            f"🔴 {snapshot.blocked_count} blocked / ⭕ {snapshot.pending_count} pending"
        ),
        "",
        "## Active Now",
    ]

    if snapshot.active_items:
        lines.extend(_entry_markdown_line(entry) for entry in snapshot.active_items)
    else:
        lines.append("- No active items right now.")

    lines.extend(["", "## Blocked"])
    if snapshot.blocked_items:
        for entry in snapshot.blocked_items:
            lines.append(_entry_markdown_line(entry))
            if entry.blocked_reason:
                lines.append(f"  - Reason: {entry.blocked_reason}")
    else:
        lines.append("- No blocked items.")

    lines.extend(["", "## Up Next"])
    if snapshot.up_next_items:
        lines.extend(_entry_markdown_line(entry) for entry in snapshot.up_next_items)
    else:
        lines.append("- No pending items remain.")

    lines.extend(["", "## Recent Completions"])
    if snapshot.recent_completions:
        lines.extend(
            _entry_markdown_line(entry) for entry in snapshot.recent_completions
        )
    else:
        lines.append("- No completed items yet.")

    return "\n".join(lines).strip() + "\n"


def visualize_ralph_task_file(task_file: Path) -> str:
    data = _read_yaml_mapping(task_file)
    metadata = data.get("metadata", {})
    task_obj = data.get("task", {})
    if not isinstance(metadata, dict) or not isinstance(task_obj, dict):
        raise ValueError(f"invalid Ralph task structure in {task_file}")

    task_status = str(task_obj.get("status", "pending"))
    status_icon = STATUS_ICONS.get(task_status, "❓")

    lines = ["", "=" * 80, "TASK IMPLEMENTATION PLAN - STATUS SUMMARY", "=" * 80]
    lines.extend(
        [
            "",
            "📋 Metadata:",
            f"   Version: {metadata.get('version', 'N/A')}",
            f"   Created: {metadata.get('created_date', 'N/A')}",
            f"   Updated: {metadata.get('last_updated', 'N/A')}",
            f"   Author: {metadata.get('author', 'N/A')}",
            f"   Framework: {metadata.get('framework', 'N/A')}",
        ]
    )
    license_value = metadata.get("license")
    if license_value:
        lines.append(f"   License: {license_value}")

    lines.extend(
        [
            "",
            f"🎯 Task: {task_obj.get('name', 'Unnamed')}",
            f"   Status: {status_icon} {STATUS_NAMES.get(task_status, 'UNKNOWN')}",
        ]
    )
    blocked_reason = task_obj.get("blocked_reason")
    if task_status == "blocked" and isinstance(blocked_reason, str):
        lines.append(f"   ⚠️  Blocked: {blocked_reason}")

    overall_counts = {"pending": 0, "active": 0, "blocked": 0, "done": 0}
    phases_obj = task_obj.get("phases", [])
    if isinstance(phases_obj, list):
        for phase_obj in phases_obj:
            if not isinstance(phase_obj, dict):
                continue
            phase_counts = _count_statuses_in_phase(phase_obj)
            for status_name, count in phase_counts.items():
                overall_counts[status_name] = overall_counts.get(status_name, 0) + count

    total = sum(overall_counts.values())
    if total > 0:
        done = overall_counts.get("done", 0)
        active = overall_counts.get("active", 0)
        blocked = overall_counts.get("blocked", 0)
        done_width = int((done / total) * 50)
        active_width = int((active / total) * 50)
        blocked_width = int((blocked / total) * 50)
        pending_width = 50 - done_width - active_width - blocked_width
        percentage = (done / total) * 100
        bar = (
            "█" * done_width
            + "▓" * active_width
            + "░" * blocked_width
            + "·" * pending_width
        )
        lines.extend(
            [
                "",
                "📊 Overall Progress:",
                f"\n   [{bar}] {percentage:.1f}% complete",
                "   ✅ {done} done  🔵 {active} active  🔴 {blocked} blocked  ⭕ {pending} pending".format(
                    done=done,
                    active=active,
                    blocked=blocked,
                    pending=overall_counts.get("pending", 0),
                ),
            ]
        )

    lines.extend(["", "=" * 80, "PHASE STRUCTURE", "=" * 80])
    if isinstance(phases_obj, list):
        for phase_obj in phases_obj:
            if isinstance(phase_obj, dict):
                _append_phase_lines(lines, phase_obj)

    return "\n".join(lines).rstrip() + "\n"
