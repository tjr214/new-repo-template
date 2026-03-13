from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def run_scaffold_command(
    *, repo_root: Path, args: list[str]
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "src")
    return subprocess.run(
        [sys.executable, "-m", "new_repo_template.scaffold", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def test_foundation_dry_run_reports_workspace_root_config_files(tmp_path: Path) -> None:
    """RED: foundation dry-run should include package.json and turbo.json."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "foundation-workspace-dry-run"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "foundation",
            "--no-interactive",
            "--dry-run",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected foundation dry-run scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "package.json" in combined_output
    assert "turbo.json" in combined_output
    assert "btca.config.jsonc" in combined_output
    assert "AGENTS.md" in combined_output
    assert "PLAN.md" in combined_output
    assert "README.md" in combined_output
    assert "README.BMAD-GUIDE.md" in combined_output
    assert "README.RALPH.md" in combined_output
    assert "PROGRESS.md" in combined_output
    assert "scripts/RALPH.sh" in combined_output
    assert "scripts/configure-repo-protections.sh" in combined_output
    assert "scripts/synthetic-quotas.sh" in combined_output
    assert "scripts/task-template-schema.json" in combined_output
    assert "scripts/validate_template.py" in combined_output
    assert "scripts/visualize_plan.py" in combined_output
    assert "docs/archive/" in combined_output
    assert "docs/archive/plans/" in combined_output
    assert "docs/archive/progress/" in combined_output
    assert "docs/ARCHITECTURE.md" in combined_output
    assert "docs/LIVING_DOCS.md" in combined_output
    assert "docs/markdown-templates/" in combined_output
    assert "docs/markdown-templates/PLAN.template.md" in combined_output
    assert "docs/markdown-templates/PROGRESS.template.md" in combined_output
    assert "docs/session-summaries/" in combined_output
    assert "docs/tasks/task-template.yaml" in combined_output
    assert "docs/workflows/export-to-ralph/workflow.md" in combined_output
    assert ".github/" in combined_output
    assert ".github/workflows/" in combined_output
    assert ".github/workflows/ci.yml" in combined_output
    assert ".github/workflows/release.yml" in combined_output
    assert ".agent/rules/general-rules.md" in combined_output
    assert ".opencode/command/project-export-bmad-to-ralph.md" in combined_output


def test_foundation_scaffold_writes_workspace_config_and_cross_platform_scripts(
    tmp_path: Path,
) -> None:
    """RED: foundation scaffold should include workspace and turbo task wiring."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "foundation-workspace-output"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "foundation",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected foundation scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    root_package_json = output_dir / "package.json"
    root_turbo_json = output_dir / "turbo.json"

    assert root_package_json.exists(), "root package.json must exist"
    assert root_turbo_json.exists(), "root turbo.json must exist"

    package_data = json.loads(root_package_json.read_text(encoding="utf-8"))
    assert package_data.get("private") is True
    assert package_data.get("workspaces") == ["apps/*", "packages/*"]

    scripts = package_data.get("scripts")
    assert isinstance(scripts, dict), "root scripts must be defined"
    assert scripts.get("dev") == "turbo run dev"
    assert scripts.get("build") == "turbo run build"
    assert scripts.get("test") == "turbo run test"
    assert scripts.get("lint") == "turbo run lint"
    assert scripts.get("typecheck") == "turbo run typecheck"

    for script_name in ("dev", "build", "test", "lint", "typecheck"):
        script_value = scripts.get(script_name, "")
        assert ".sh" not in script_value
        assert "powershell" not in script_value.lower()

    turbo_data = json.loads(root_turbo_json.read_text(encoding="utf-8"))
    tasks = turbo_data.get("tasks")
    assert isinstance(tasks, dict), "turbo tasks must be defined"

    for task_name in ("dev", "build", "test", "lint", "typecheck"):
        assert task_name in tasks, f"missing turbo task: {task_name}"

    dev_task = tasks["dev"]
    assert dev_task.get("cache") is False
    assert dev_task.get("persistent") is True


def test_foundation_scaffold_writes_governance_and_agent_assets(tmp_path: Path) -> None:
    """RED: foundation scaffold should include the governance asset baseline."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "foundation-governance-output"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "foundation",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected foundation scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    mirrored_files = (
        (repo_root / "btca.config.jsonc", output_dir / "btca.config.jsonc"),
        (repo_root / "AGENTS.md", output_dir / "AGENTS.md"),
        (
            repo_root / "docs" / "markdown-templates" / "PLAN.template.md",
            output_dir / "PLAN.md",
        ),
        (
            repo_root / "templates-snapshot-files" / "snapshot-readme-md.txt",
            output_dir / "README.md",
        ),
        (
            repo_root / "README.BMAD-GUIDE.md",
            output_dir / "README.BMAD-GUIDE.md",
        ),
        (repo_root / "README.RALPH.md", output_dir / "README.RALPH.md"),
        (
            repo_root / "docs" / "markdown-templates" / "PROGRESS.template.md",
            output_dir / "PROGRESS.md",
        ),
        (repo_root / "scripts" / "RALPH.sh", output_dir / "scripts" / "RALPH.sh"),
        (
            repo_root / "scripts" / "configure-repo-protections.sh",
            output_dir / "scripts" / "configure-repo-protections.sh",
        ),
        (
            repo_root / "scripts" / "synthetic-quotas.sh",
            output_dir / "scripts" / "synthetic-quotas.sh",
        ),
        (
            repo_root / "scripts" / "task-template-schema.json",
            output_dir / "scripts" / "task-template-schema.json",
        ),
        (
            repo_root / "scripts" / "validate_template.py",
            output_dir / "scripts" / "validate_template.py",
        ),
        (
            repo_root / "scripts" / "visualize_plan.py",
            output_dir / "scripts" / "visualize_plan.py",
        ),
        (
            repo_root / "templates-snapshot-files" / "snapshot-architecture-md.txt",
            output_dir / "docs" / "ARCHITECTURE.md",
        ),
        (
            repo_root / "templates-snapshot-files" / "snapshot-living-docs-md.txt",
            output_dir / "docs" / "LIVING_DOCS.md",
        ),
        (
            repo_root / "docs" / "markdown-templates" / "PLAN.template.md",
            output_dir / "docs" / "markdown-templates" / "PLAN.template.md",
        ),
        (
            repo_root / "docs" / "markdown-templates" / "PROGRESS.template.md",
            output_dir / "docs" / "markdown-templates" / "PROGRESS.template.md",
        ),
        (
            repo_root / "docs" / "tasks" / "task-template.yaml",
            output_dir / "docs" / "tasks" / "task-template.yaml",
        ),
        (
            repo_root / "docs" / "tasks" / "task-template-example.yaml",
            output_dir / "docs" / "tasks" / "task-template-example.yaml",
        ),
        (
            repo_root / "docs" / "workflows" / "export-to-ralph" / "workflow.md",
            output_dir / "docs" / "workflows" / "export-to-ralph" / "workflow.md",
        ),
        (
            repo_root / ".github" / "workflows" / "ci.yml",
            output_dir / ".github" / "workflows" / "ci.yml",
        ),
        (
            repo_root / ".github" / "workflows" / "release.yml",
            output_dir / ".github" / "workflows" / "release.yml",
        ),
        (
            repo_root / ".agent" / "rules" / "general-rules.md",
            output_dir / ".agent" / "rules" / "general-rules.md",
        ),
        (
            repo_root
            / ".agent"
            / "workflows"
            / "project"
            / "project-export-bmad-to-ralph.md",
            output_dir
            / ".agent"
            / "workflows"
            / "project"
            / "project-export-bmad-to-ralph.md",
        ),
        (
            repo_root
            / ".opencode"
            / "command"
            / "project-save-progress-to-checkpoint.md",
            output_dir
            / ".opencode"
            / "command"
            / "project-save-progress-to-checkpoint.md",
        ),
    )

    for source_path, destination_path in mirrored_files:
        assert destination_path.exists(), (
            f"Expected mirrored file at {destination_path}"
        )
        assert destination_path.read_text(encoding="utf-8") == source_path.read_text(
            encoding="utf-8"
        )

    workflow_files = sorted((repo_root / "docs" / "workflows").rglob("*.md"))
    for source_path in workflow_files:
        relative = source_path.relative_to(repo_root)
        assert (output_dir / relative).exists(), f"Expected workflow file at {relative}"

    github_files = sorted((repo_root / ".github").rglob("*"))
    for source_path in github_files:
        relative = source_path.relative_to(repo_root)
        destination_path = output_dir / relative
        if source_path.is_dir():
            assert destination_path.is_dir(), f"Expected github directory at {relative}"
        else:
            assert destination_path.exists(), f"Expected github file at {relative}"

    opencode_command_files = sorted((repo_root / ".opencode" / "command").glob("*.md"))
    for source_path in opencode_command_files:
        relative = source_path.relative_to(repo_root)
        assert (output_dir / relative).exists(), (
            f"Expected opencode command file at {relative}"
        )

    assert (output_dir / "docs" / "archive").is_dir()
    assert (output_dir / "docs" / "archive" / "plans").is_dir()
    assert (output_dir / "docs" / "archive" / "progress").is_dir()
    assert (output_dir / "docs" / "markdown-templates").is_dir()
    assert (output_dir / "docs" / "session-summaries").is_dir()
    assert (output_dir / ".github").is_dir()
    assert (output_dir / ".github" / "workflows").is_dir()
    assert not (output_dir / ".opencode" / "package.json").exists()
    assert not (output_dir / ".opencode" / "bun.lock").exists()
    assert not (output_dir / ".opencode" / "node_modules").exists()
