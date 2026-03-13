from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from rich.console import Group, RenderableType
from rich.padding import Padding
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from new_repo_template.bmad_runner import run_bmad_sync
from new_repo_template.sync_ops import run_tools_sync
from new_repo_template.version_baseline import generate_project_lockfiles


def render_post_create_plan(
    *,
    project_root: Path,
    install_bmad: bool,
    install_core_tools: bool,
) -> str:
    lines = [
        "Post-create automation plan:",
        f"- project root: {project_root}",
        f"- BMAD Method: {'yes' if install_bmad else 'no'}",
        f"- Core tools updater: {'yes' if install_core_tools else 'no'}",
        "- lifecycle:",
        "  - scaffold output already planned/generated",
        (
            "  - optional BMAD Method install/update before lockfiles"
            if install_bmad
            else "  - skip BMAD Method install/update"
        ),
        "  - lockfiles/revalidation via project metadata",
        '  - git init -> git add . -> git commit -m "Initial Commit"',
        (
            "  - optional core-tools updater after initial commit"
            if install_core_tools
            else "  - skip core-tools updater"
        ),
    ]
    return "\n".join(lines)


def render_completion_overview(
    *,
    project_root: Path,
    targets: tuple[str, ...],
    auth: str | None,
    install_bmad: bool,
    install_core_tools: bool,
) -> RenderableType:
    project_name = project_root.name
    target_label = ", ".join(targets)

    details_table = Table.grid(expand=True, padding=(0, 1))
    details_table.add_column(style="bold #95dbe8", ratio=1)
    details_table.add_column(style="#edf6f7", ratio=3)
    details_table.add_row("Project", project_name)
    details_table.add_row("Location", str(project_root))
    details_table.add_row("Targets", target_label)
    details_table.add_row("Auth", auth or "Not required")

    accomplished_table = Table.grid(expand=True, padding=(0, 1))
    accomplished_table.add_column(style="bold #79e0d4", ratio=1)
    accomplished_table.add_column(style="#edf6f7", ratio=3)
    accomplished_table.add_row(
        "Scaffold", "Generated the project files and workspace baseline."
    )
    accomplished_table.add_row(
        "Lockfiles", "Created or revalidated managed lockfiles for the new project."
    )
    accomplished_table.add_row(
        "Git", "Initialized a repository and created `Initial Commit`."
    )
    accomplished_table.add_row(
        "BMAD",
        "Installed the BMAD Method during project bootstrap."
        if install_bmad
        else "Skipped BMAD Method installation for this run.",
    )
    accomplished_table.add_row(
        "Core tools",
        "Installed or updated the managed core toolchain."
        if install_core_tools
        else "Skipped the optional core-tools updater.",
    )

    handoff = Group(
        Text("Changing into the project directory now.", style="bold #f5cf85"),
        Padding(Text(f"cd {project_name}", style="bold #79e0d4"), (1, 0, 0, 2)),
    )

    content = Group(
        Text("nurt new finished successfully", style="bold #79e0d4"),
        Text(
            "The project is scaffolded, initialized, and ready for the next command.",
            style="#d7e7ec",
        ),
        Rule(style="#2b6674"),
        details_table,
        Rule(style="#2b6674"),
        accomplished_table,
        Rule(style="#2b6674"),
        handoff,
    )

    return Panel(
        Padding(content, (0, 1)),
        title="Setup Complete",
        subtitle=project_name,
        border_style="#3f9cae",
        expand=False,
    )


def _git_identity_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("GIT_AUTHOR_NAME", "nurt")
    env.setdefault("GIT_AUTHOR_EMAIL", "nurt@example.invalid")
    env.setdefault("GIT_COMMITTER_NAME", "nurt")
    env.setdefault("GIT_COMMITTER_EMAIL", "nurt@example.invalid")
    return env


def _run_git_command(
    project_root: Path, command: list[str], *, env: dict[str, str] | None = None
) -> int:
    try:
        result = subprocess.run(
            command,
            cwd=project_root,
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
    except FileNotFoundError:
        print(
            "Error: git is required for post-create repository setup.", file=sys.stderr
        )
        return 1

    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)

    if result.returncode != 0:
        return result.returncode or 1
    return 0


def initialize_git_repository(*, project_root: Path) -> int:
    print(f"Initializing git repository in `{project_root}`...")
    return _run_git_command(project_root, ["git", "init"])


def create_initial_commit(*, project_root: Path) -> int:
    print("Creating initial git commit...")
    status = _run_git_command(project_root, ["git", "add", "."])
    if status != 0:
        return status

    return _run_git_command(
        project_root,
        ["git", "commit", "-m", "Initial Commit"],
        env=_git_identity_env(),
    )


def run_post_create_pipeline(
    *,
    project_root: Path,
    install_bmad: bool,
    install_core_tools: bool,
    use_tui: bool = False,
) -> int:
    if install_bmad:
        if run_bmad_sync(project_root=project_root, dry_run=False) != 0:
            return 1

    lockfile_status = generate_project_lockfiles(project_root=project_root)
    if lockfile_status != 0:
        return lockfile_status

    git_init_status = initialize_git_repository(project_root=project_root)
    if git_init_status != 0:
        return git_init_status

    commit_status = create_initial_commit(project_root=project_root)
    if commit_status != 0:
        return commit_status

    if install_core_tools:
        return run_tools_sync(dry_run=False, cwd=project_root, use_tui=use_tui)

    return 0
