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
