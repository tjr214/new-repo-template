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


def test_foundation_preset_install_lint_typecheck_and_test_commands_succeed(
    tmp_path: Path,
) -> None:
    """Foundation preset should support install, lint, typecheck, and test baseline commands."""

    bun_binary = shutil.which("bun")
    if bun_binary is None:
        pytest.skip("bun executable is required for foundation runtime smoke contract")

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "foundation-runtime"

    scaffold_result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "foundation",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )
    assert scaffold_result.returncode == 0, (
        "Expected foundation scaffold command to succeed before runtime smoke checks.\n"
        f"stdout:\n{scaffold_result.stdout}\n"
        f"stderr:\n{scaffold_result.stderr}"
    )

    lockfile_result = run_bun_command(
        bun_binary=bun_binary,
        cwd=output_dir,
        args=[
            "install",
            "--save-text-lockfile",
            "--frozen-lockfile",
            "--lockfile-only",
        ],
    )
    assert lockfile_result.returncode == 0, (
        "Expected foundation lockfile generation to succeed.\n"
        f"stdout:\n{lockfile_result.stdout}\n"
        f"stderr:\n{lockfile_result.stderr}"
    )

    install_result = run_bun_command(
        bun_binary=bun_binary,
        cwd=output_dir,
        args=["install", "--frozen-lockfile"],
    )
    assert install_result.returncode == 0, (
        "Expected `bun install --frozen-lockfile` to succeed for foundation scaffold.\n"
        f"stdout:\n{install_result.stdout}\n"
        f"stderr:\n{install_result.stderr}"
    )

    for command in ("lint", "typecheck", "test"):
        command_result = run_bun_command(
            bun_binary=bun_binary,
            cwd=output_dir,
            args=["run", command],
        )
        assert command_result.returncode == 0, (
            f"Expected `bun run {command}` to succeed for foundation scaffold.\n"
            f"stdout:\n{command_result.stdout}\n"
            f"stderr:\n{command_result.stderr}"
        )
