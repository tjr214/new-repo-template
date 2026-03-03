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


def run_bun_command(
    *, bun_binary: str, cwd: Path, args: list[str]
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["TURBO_TELEMETRY_DISABLED"] = "1"
    return subprocess.run(
        [bun_binary, *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def test_minimal_js_preset_turbo_commands_smoke(tmp_path: Path) -> None:
    """RED: selected minimal JS preset should pass root Turbo command scripts."""

    bun_binary = shutil.which("bun")
    if bun_binary is None:
        pytest.skip("bun executable is required for turbo command smoke contract")

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "minimal-js-preset"

    scaffold_result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "web",
            "--target",
            "backend",
            "--auth",
            "clerk",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )
    assert scaffold_result.returncode == 0, (
        "Expected minimal JS preset scaffold to succeed.\n"
        f"stdout:\n{scaffold_result.stdout}\n"
        f"stderr:\n{scaffold_result.stderr}"
    )

    install_result = run_bun_command(
        bun_binary=bun_binary,
        cwd=output_dir,
        args=["install", "--frozen-lockfile"],
    )
    assert install_result.returncode == 0, (
        "Expected `bun install --frozen-lockfile` to succeed.\n"
        f"stdout:\n{install_result.stdout}\n"
        f"stderr:\n{install_result.stderr}"
    )

    for command in ("dev", "build", "test", "lint", "typecheck"):
        command_result = run_bun_command(
            bun_binary=bun_binary,
            cwd=output_dir,
            args=["run", command],
        )
        assert command_result.returncode == 0, (
            f"Expected `bun run {command}` to succeed for minimal JS preset.\n"
            f"stdout:\n{command_result.stdout}\n"
            f"stderr:\n{command_result.stderr}"
        )
