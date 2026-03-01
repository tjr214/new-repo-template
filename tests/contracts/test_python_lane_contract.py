from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


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
