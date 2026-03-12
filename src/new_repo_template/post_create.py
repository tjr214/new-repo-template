from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

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
