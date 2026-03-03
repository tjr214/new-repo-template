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


def run_lane_command(
    *, lane_root: Path, args: list[str], uv_binary: str
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)

    return subprocess.run(
        [uv_binary, *args],
        cwd=lane_root,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def test_python_target_dry_run_reports_root_and_lane_pyproject(tmp_path: Path) -> None:
    """RED: Python target dry-run should report root and lane-local pyproject files."""

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
    assert "apps/python/pyproject.toml" in combined_output
    assert not output_dir.exists(), "--dry-run should not write scaffold output"


def test_python_target_scaffold_creates_root_and_lane_pyproject(tmp_path: Path) -> None:
    """RED: Python target scaffold should create root + lane pyproject separation."""

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

    root_pyproject = output_dir / "pyproject.toml"
    lane_pyproject = output_dir / "apps" / "python" / "pyproject.toml"

    assert root_pyproject.exists(), "root pyproject.toml must always exist"
    assert lane_pyproject.exists(), "python lane requires an app-local pyproject.toml"

    root_content = root_pyproject.read_text(encoding="utf-8")
    lane_content = lane_pyproject.read_text(encoding="utf-8")

    assert "[build-system]" in root_content
    assert "[tool.uv.workspace]" in root_content
    assert "apps/python" in root_content
    assert "[project]" in lane_content
    assert 'requires-python = ">=3.14"' in lane_content


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

    lane_root = output_dir / "apps" / "python"

    sync_result = run_lane_command(
        lane_root=lane_root,
        uv_binary=uv_binary,
        args=["sync", "--group", "dev"],
    )
    assert sync_result.returncode == 0, (
        "Expected `uv sync --group dev` to succeed for generated python lane.\n"
        f"stdout:\n{sync_result.stdout}\n"
        f"stderr:\n{sync_result.stderr}"
    )

    commands: tuple[list[str], ...] = (
        ["run", "pytest"],
        ["run", "ruff", "check", "."],
        ["run", "mypy", "src"],
    )

    for command in commands:
        command_result = run_lane_command(
            lane_root=lane_root,
            uv_binary=uv_binary,
            args=command,
        )
        assert command_result.returncode == 0, (
            f"Expected `uv {' '.join(command)}` to succeed for generated python lane.\n"
            f"stdout:\n{command_result.stdout}\n"
            f"stderr:\n{command_result.stderr}"
        )
