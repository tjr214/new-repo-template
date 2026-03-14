from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


def run_scaffold_command(
    *, repo_root: Path, output_dir: Path, dry_run: bool
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "src")

    command = [
        sys.executable,
        "-m",
        "new_repo_template.scaffold",
        "--target",
        "python",
        "--no-interactive",
        "--output",
        str(output_dir),
    ]
    if dry_run:
        command.append("--dry-run")

    return subprocess.run(
        command,
        cwd=repo_root,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def run_workspace_command(
    *, workspace_root: Path, args: list[str], uv_binary: str
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)

    return subprocess.run(
        [uv_binary, *args],
        cwd=workspace_root,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def test_python_target_dry_run_reports_lane_python_files_only(tmp_path: Path) -> None:
    """RED: Python target dry-run should report Python metadata only inside the lane."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "python-output-dry-run"

    result = run_scaffold_command(
        repo_root=repo_root, output_dir=output_dir, dry_run=True
    )

    assert result.returncode == 0, (
        "Expected python dry-run scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "pyproject.toml" in combined_output
    assert "apps/python/python-app/pyproject.toml" in combined_output
    assert "apps/python/python-app/.python-version" in combined_output
    assert "apps/python/python-app/src/python_app/cli.py" in combined_output
    assert "apps/python/python-app/src/python_app/tui.py" in combined_output
    assert "apps/python/python-app/src/python_app/entry_points.py" in combined_output
    assert "apps/python/python-app/src/python_app/app.tcss" in combined_output
    assert "  - .python-version" not in combined_output
    assert not output_dir.exists(), "--dry-run should not write scaffold output"


def test_python_target_scaffold_creates_lane_python_files_only(tmp_path: Path) -> None:
    """RED: Python target scaffold should keep Python metadata only in the lane."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "python-output"

    result = run_scaffold_command(
        repo_root=repo_root, output_dir=output_dir, dry_run=False
    )

    assert result.returncode == 0, (
        "Expected python scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    lane_root = output_dir / "apps" / "python" / "python-app"
    lane_pyproject = lane_root / "pyproject.toml"
    lane_python_version = lane_root / ".python-version"
    expected_lane_files = (
        lane_root / "src" / "python_app" / "__init__.py",
        lane_root / "src" / "python_app" / "core.py",
        lane_root / "src" / "python_app" / "cli.py",
        lane_root / "src" / "python_app" / "tui.py",
        lane_root / "src" / "python_app" / "entry_points.py",
        lane_root / "src" / "python_app" / "app.tcss",
        lane_root / "tests" / "test_core.py",
    )

    root_pyproject = output_dir / "pyproject.toml"
    assert root_pyproject.exists(), (
        "root pyproject.toml must exist for uv workspace wiring"
    )
    assert not (output_dir / ".python-version").exists(), (
        "root .python-version must not exist when Python metadata lives in the lane"
    )
    assert lane_pyproject.exists(), "python lane requires an app-local pyproject.toml"
    assert lane_python_version.exists(), "python lane .python-version must exist"
    assert not lane_python_version.is_symlink(), (
        "python lane .python-version must be a real file, not a symlink"
    )
    for path in expected_lane_files:
        assert path.exists(), f"Expected scaffolded python lane file: {path}"

    lane_content = lane_pyproject.read_text(encoding="utf-8")
    root_pyproject_content = root_pyproject.read_text(encoding="utf-8")
    lane_python_version_content = lane_python_version.read_text(encoding="utf-8")

    assert lane_python_version_content == (repo_root / ".python-version").read_text(
        encoding="utf-8"
    )
    assert "[tool.uv.workspace]" in root_pyproject_content
    assert "apps/python/*" in root_pyproject_content
    assert "packages/python" not in root_pyproject_content
    assert "[project]" in lane_content
    assert 'requires-python = ">=3.14"' in lane_content
    assert "rich>=14.3.3" in lane_content
    assert "textual>=8.0.1" in lane_content
    assert "[project.scripts]" in lane_content
    assert 'python-app = "python_app.entry_points:run_cli"' in lane_content
    assert 'python-app-tui = "python_app.entry_points:run_tui"' in lane_content


def test_python_target_scaffold_runs_baseline_commands(tmp_path: Path) -> None:
    """Python lane scaffold should execute baseline uv/pytest/ruff/mypy commands."""

    uv_binary = shutil.which("uv")
    if uv_binary is None:
        pytest.skip("uv executable is required for python lane command contract")

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "python-output-commands"

    scaffold_result = run_scaffold_command(
        repo_root=repo_root, output_dir=output_dir, dry_run=False
    )
    assert scaffold_result.returncode == 0, (
        "Expected python scaffold command to succeed before baseline command checks.\n"
        f"stdout:\n{scaffold_result.stdout}\n"
        f"stderr:\n{scaffold_result.stderr}"
    )

    sync_result = run_workspace_command(
        workspace_root=output_dir,
        uv_binary=uv_binary,
        args=["sync", "--package", "python-app", "--group", "dev"],
    )
    assert sync_result.returncode == 0, (
        "Expected `uv sync --package python-app --group dev` to succeed for generated python lane.\n"
        f"stdout:\n{sync_result.stdout}\n"
        f"stderr:\n{sync_result.stderr}"
    )

    cli_result = run_workspace_command(
        workspace_root=output_dir,
        uv_binary=uv_binary,
        args=["run", "--package", "python-app", "python-app", "demo-user"],
    )
    assert cli_result.returncode == 0, (
        "Expected `uv run --package python-app python-app demo-user` to succeed for generated python lane.\n"
        f"stdout:\n{cli_result.stdout}\n"
        f"stderr:\n{cli_result.stderr}"
    )
    assert "demo-user" in f"{cli_result.stdout}\n{cli_result.stderr}"

    tui_help_result = run_workspace_command(
        workspace_root=output_dir,
        uv_binary=uv_binary,
        args=["run", "--package", "python-app", "python-app-tui", "--help"],
    )
    assert tui_help_result.returncode == 0, (
        "Expected `uv run --package python-app python-app-tui --help` to succeed for generated python lane.\n"
        f"stdout:\n{tui_help_result.stdout}\n"
        f"stderr:\n{tui_help_result.stderr}"
    )
    assert "Launch the Textual starter app" in tui_help_result.stdout

    commands: tuple[list[str], ...] = (
        ["run", "--package", "python-app", "pytest", "apps/python/python-app/tests"],
        ["run", "--package", "python-app", "ruff", "check", "apps/python/python-app"],
        ["run", "--package", "python-app", "mypy", "apps/python/python-app/src"],
    )

    for command in commands:
        command_result = run_workspace_command(
            workspace_root=output_dir,
            uv_binary=uv_binary,
            args=command,
        )
        assert command_result.returncode == 0, (
            f"Expected `uv {' '.join(command)}` to succeed for generated python lane.\n"
            f"stdout:\n{command_result.stdout}\n"
            f"stderr:\n{command_result.stderr}"
        )


def test_python_target_scaffold_supports_legacy_extra_dev_sync_compatibility(
    tmp_path: Path,
) -> None:
    """Python lane should tolerate legacy `uv sync --extra dev` flows."""

    uv_binary = shutil.which("uv")
    if uv_binary is None:
        pytest.skip("uv executable is required for python lane command contract")

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "python-output-extra-dev"

    scaffold_result = run_scaffold_command(
        repo_root=repo_root, output_dir=output_dir, dry_run=False
    )
    assert scaffold_result.returncode == 0, (
        "Expected python scaffold command to succeed before legacy sync checks.\n"
        f"stdout:\n{scaffold_result.stdout}\n"
        f"stderr:\n{scaffold_result.stderr}"
    )

    sync_result = run_workspace_command(
        workspace_root=output_dir,
        uv_binary=uv_binary,
        args=["sync", "--package", "python-app", "--extra", "dev"],
    )
    assert sync_result.returncode == 0, (
        "Expected `uv sync --package python-app --extra dev` to succeed for generated python lane.\n"
        f"stdout:\n{sync_result.stdout}\n"
        f"stderr:\n{sync_result.stderr}"
    )

    pytest_result = run_workspace_command(
        workspace_root=output_dir,
        uv_binary=uv_binary,
        args=[
            "run",
            "--package",
            "python-app",
            "pytest",
            "apps/python/python-app/tests",
        ],
    )
    assert pytest_result.returncode == 0, (
        "Expected `uv run --package python-app pytest apps/python/python-app/tests` to succeed after `uv sync --package python-app --extra dev`.\n"
        f"stdout:\n{pytest_result.stdout}\n"
        f"stderr:\n{pytest_result.stderr}"
    )
