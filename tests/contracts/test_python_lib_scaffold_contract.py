from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


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


def run_uv_command(
    *, uv_binary: str, cwd: Path, args: list[str]
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)
    return subprocess.run(
        [uv_binary, *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def test_python_lib_target_scaffolds_workspace_library(tmp_path: Path) -> None:
    """python-lib target should scaffold a reusable Python workspace package."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "python-lib"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "python-lib",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected python-lib scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    library_root = output_dir / "packages" / "python" / "python-lib"
    expected_paths = (
        output_dir / "pyproject.toml",
        library_root / "pyproject.toml",
        library_root / "README.md",
        library_root / "src" / "python_lib" / "__init__.py",
        library_root / "src" / "python_lib" / "core.py",
        library_root / "tests" / "test_core.py",
    )
    for path in expected_paths:
        assert path.exists(), f"Expected scaffolded Python library file: {path}"

    root_pyproject = (output_dir / "pyproject.toml").read_text(encoding="utf-8")
    assert "[tool.uv.workspace]" in root_pyproject
    assert "packages/python/*" in root_pyproject
    assert "apps/python" not in root_pyproject

    library_pyproject = (library_root / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "python-lib"' in library_pyproject
    assert 'requires-python = ">=3.14"' in library_pyproject
    assert 'packages = ["src/python_lib"]' in library_pyproject


def test_python_app_and_library_scaffold_wire_uv_workspace_dependency(
    tmp_path: Path,
) -> None:
    """python + python-lib should wire the app to the generated library through uv workspace sources."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "python-workspace"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "python",
            "--target",
            "python-lib",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected python + python-lib scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    root_pyproject = (output_dir / "pyproject.toml").read_text(encoding="utf-8")
    assert "apps/python/*" in root_pyproject
    assert "packages/python/*" in root_pyproject

    app_pyproject = (
        output_dir / "apps" / "python" / "python-app" / "pyproject.toml"
    ).read_text(encoding="utf-8")
    assert '"python-lib>=0.1.0"' in app_pyproject
    assert "[tool.uv.sources]" in app_pyproject
    assert "python-lib = { workspace = true }" in app_pyproject

    core_text = (
        output_dir / "apps" / "python" / "python-app" / "src" / "python_app" / "core.py"
    ).read_text(encoding="utf-8")
    assert "from python_lib import build_greeting" in core_text


def test_python_app_and_library_workspace_run_together(tmp_path: Path) -> None:
    """Generated Python workspace should sync and run the app against the local library."""

    uv_binary = shutil.which("uv")
    if uv_binary is None:
        pytest.skip("uv executable is required for python library workspace contract")

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "python-workspace-runtime"

    scaffold_result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "python",
            "--target",
            "python-lib",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )
    assert scaffold_result.returncode == 0, (
        "Expected python workspace scaffold to succeed before runtime checks.\n"
        f"stdout:\n{scaffold_result.stdout}\n"
        f"stderr:\n{scaffold_result.stderr}"
    )

    sync_result = run_uv_command(
        uv_binary=uv_binary,
        cwd=output_dir,
        args=["sync", "--package", "python-app", "--group", "dev"],
    )
    assert sync_result.returncode == 0, (
        "Expected `uv sync --package python-app --group dev` to succeed.\n"
        f"stdout:\n{sync_result.stdout}\n"
        f"stderr:\n{sync_result.stderr}"
    )

    cli_result = run_uv_command(
        uv_binary=uv_binary,
        cwd=output_dir,
        args=["run", "--package", "python-app", "python-app", "demo-user"],
    )
    assert cli_result.returncode == 0, (
        "Expected generated python app to run against the workspace library.\n"
        f"stdout:\n{cli_result.stdout}\n"
        f"stderr:\n{cli_result.stderr}"
    )
    assert "demo-user" in f"{cli_result.stdout}\n{cli_result.stderr}"
    assert "python-lib" in f"{cli_result.stdout}\n{cli_result.stderr}"

    for command in (
        [
            "run",
            "--package",
            "python-app",
            "pytest",
            "apps/python/python-app/tests",
        ],
        [
            "run",
            "--package",
            "python-app",
            "ruff",
            "check",
            "apps/python/python-app",
            "packages/python/python-lib",
        ],
        [
            "run",
            "--package",
            "python-app",
            "mypy",
            "apps/python/python-app/src",
            "packages/python/python-lib/src",
        ],
    ):
        command_result = run_uv_command(
            uv_binary=uv_binary,
            cwd=output_dir,
            args=list(command),
        )
        assert command_result.returncode == 0, (
            f"Expected `uv {' '.join(command)}` to succeed for the generated python workspace.\n"
            f"stdout:\n{command_result.stdout}\n"
            f"stderr:\n{command_result.stderr}"
        )
