#!/usr/bin/env python3
"""
Visualize the structure and status of a task implementation plan.

Usage:
    python visualize_plan.py task-template.yaml
    python visualize_plan.py task-template-example.yaml
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, Any


# Status icons and colors
STATUS_ICONS = {"pending": "⭕", "active": "🔵", "blocked": "🔴", "done": "✅"}

STATUS_NAMES = {
    "pending": "PENDING",
    "active": "ACTIVE",
    "blocked": "BLOCKED",
    "done": "DONE",
}


def load_yaml(filepath: str) -> dict:
    """Load YAML file and return as dict."""
    with open(filepath, "r") as f:
        return yaml.safe_load(f)


def print_status_summary(data: dict):
    """Print overall status summary."""
    print("\n" + "=" * 80)
    print("TASK IMPLEMENTATION PLAN - STATUS SUMMARY")
    print("=" * 80)

    # Metadata
    metadata = data.get("metadata", {})
    print(f"\n📋 Metadata:")
    print(f"   Version: {metadata.get('version', 'N/A')}")
    print(f"   Created: {metadata.get('created_date', 'N/A')}")
    print(f"   Updated: {metadata.get('last_updated', 'N/A')}")
    print(f"   Author: {metadata.get('author', 'N/A')}")
    if metadata.get("license"):
        print(f"   License: {metadata['license']}")

    # Task
    task = data.get("task", {})
    status_icon = STATUS_ICONS.get(task.get("status", "pending"), "❓")
    print(f"\n🎯 Task: {task.get('name', 'Unnamed')}")
    print(
        f"   Status: {status_icon} {STATUS_NAMES.get(task.get('status', 'pending'), 'UNKNOWN')}"
    )
    if task.get("status") == "blocked":
        print(f"   ⚠️  Blocked: {task.get('blocked_reason', 'No reason provided')}")


def count_statuses_in_phase(phase: dict) -> Dict[str, int]:
    """Recursively count statuses in a phase and its children."""
    counts = {"pending": 0, "active": 0, "blocked": 0, "done": 0}

    # Count this phase
    status = phase.get("status", "pending")
    counts[status] = counts.get(status, 0) + 1

    # Count steps
    for step in phase.get("steps", []):
        step_status = step.get("status", "pending")
        counts[step_status] = counts.get(step_status, 0) + 1

        # Count instructions
        for instr in step.get("instructions", []):
            instr_status = instr.get("status", "pending")
            counts[instr_status] = counts.get(instr_status, 0) + 1

    # Count sub-phases recursively
    for sub_phase in phase.get("sub_phases", []):
        sub_counts = count_statuses_in_phase(sub_phase)
        for status, count in sub_counts.items():
            counts[status] = counts.get(status, 0) + count

    return counts


def print_progress_bar(counts: Dict[str, int], width: int = 50):
    """Print a progress bar based on status counts."""
    total = sum(counts.values())
    if total == 0:
        return

    done = counts.get("done", 0)
    active = counts.get("active", 0)
    blocked = counts.get("blocked", 0)
    pending = counts.get("pending", 0)

    done_width = int((done / total) * width)
    active_width = int((active / total) * width)
    blocked_width = int((blocked / total) * width)
    pending_width = width - done_width - active_width - blocked_width

    bar = (
        "█" * done_width
        + "▓" * active_width
        + "░" * blocked_width
        + "·" * pending_width
    )

    percentage = (done / total) * 100

    print(f"\n   [{bar}] {percentage:.1f}% complete")
    print(
        f"   ✅ {done} done  🔵 {active} active  🔴 {blocked} blocked  ⭕ {pending} pending"
    )


def print_instruction(instr: dict, indent: str):
    """Print instruction details."""
    status_icon = STATUS_ICONS.get(instr.get("status", "pending"), "❓")
    instr_id = instr.get("id", "unknown")

    # Truncate content to first line
    content = instr.get("content", "")
    first_line = content.split("\n")[0].strip()
    if len(first_line) > 60:
        first_line = first_line[:57] + "..."

    print(f"{indent}  {status_icon} {instr_id}: {first_line}")

    if instr.get("status") == "blocked":
        reason = instr.get("blocked_reason", "No reason provided")
        print(f"{indent}     ⚠️  {reason}")


def print_step(step: dict, indent: str):
    """Print step details."""
    status_icon = STATUS_ICONS.get(step.get("status", "pending"), "❓")
    step_id = step.get("id", "unknown")
    step_name = step.get("name", "Unnamed")

    print(f"{indent}{status_icon} {step_id}: {step_name}")

    if step.get("status") == "blocked":
        reason = step.get("blocked_reason", "No reason provided")
        print(f"{indent}   ⚠️  {reason}")

    # Print instructions
    for instr in step.get("instructions", []):
        print_instruction(instr, indent + "  ")


def print_phase(phase: dict, indent: str = ""):
    """Recursively print phase structure."""
    status_icon = STATUS_ICONS.get(phase.get("status", "pending"), "❓")
    phase_id = phase.get("id", "unknown")
    phase_name = phase.get("name", "Unnamed")

    print(f"\n{indent}{status_icon} {phase_id}: {phase_name}")

    if phase.get("status") == "blocked":
        reason = phase.get("blocked_reason", "No reason provided")
        print(f"{indent}   ⚠️  {reason}")

    # Print steps
    for step in phase.get("steps", []):
        print_step(step, indent + "  ")

    # Print sub-phases recursively
    for sub_phase in phase.get("sub_phases", []):
        print_phase(sub_phase, indent + "  ")


def visualize_plan(filepath: str):
    """Load and visualize a task implementation plan."""
    try:
        data = load_yaml(filepath)

        # Print summary
        print_status_summary(data)

        # Calculate overall progress
        task = data.get("task", {})
        overall_counts = {"pending": 0, "active": 0, "blocked": 0, "done": 0}

        for phase in task.get("phases", []):
            phase_counts = count_statuses_in_phase(phase)
            for status, count in phase_counts.items():
                overall_counts[status] = overall_counts.get(status, 0) + count

        print("\n📊 Overall Progress:")
        print_progress_bar(overall_counts)

        # Print phase structure
        print("\n" + "=" * 80)
        print("PHASE STRUCTURE")
        print("=" * 80)

        for phase in task.get("phases", []):
            print_phase(phase)

        print("\n" + "=" * 80)
        print("\n✨ Visualization complete!\n")

    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"❌ YAML parsing error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python visualize_plan.py <task-template.yaml>")
        sys.exit(1)

    template_path = sys.argv[1]

    if not Path(template_path).exists():
        print(f"❌ Template file not found: {template_path}")
        sys.exit(1)

    visualize_plan(template_path)
