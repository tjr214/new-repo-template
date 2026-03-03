from __future__ import annotations

import json
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


def test_generated_backend_supports_credentialless_convex_cli_help_smokes(
    tmp_path: Path,
) -> None:
    """RED: generated backend should provide CI-safe Convex CLI smoke commands."""

    bun_binary = shutil.which("bun")
    if bun_binary is None:
        pytest.skip("bun executable is required for Convex backend smoke contract")

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "convex-backend-smokes"

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
        "Expected web+backend scaffold command to succeed before Convex smoke checks.\n"
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

    backend_package_json_path = output_dir / "apps" / "backend" / "package.json"
    backend_package_json = json.loads(
        backend_package_json_path.read_text(encoding="utf-8")
    )
    backend_scripts = backend_package_json.get("scripts", {})

    assert backend_scripts.get("convex:dev") == "convex dev"
    assert backend_scripts.get("convex:codegen") == "convex codegen"
    assert backend_scripts.get("convex:dev:smoke") == "convex dev --help"
    assert backend_scripts.get("convex:codegen:smoke") == "convex codegen --help"

    backend_readme_path = output_dir / "apps" / "backend" / "README.md"
    assert backend_readme_path.exists(), (
        "Backend README should define local cloud-dev flow"
    )
    backend_readme = backend_readme_path.read_text(encoding="utf-8")
    assert "bun run convex:dev" in backend_readme
    assert "AUTH_PROVIDER" in backend_readme
    assert "Clerk" in backend_readme
    assert "Better Auth" in backend_readme

    codegen_help_result = run_bun_command(
        bun_binary=bun_binary,
        cwd=output_dir / "apps" / "backend",
        args=["run", "convex:codegen:smoke"],
    )
    assert codegen_help_result.returncode == 0, (
        "Expected backend Convex codegen smoke command to succeed.\n"
        f"stdout:\n{codegen_help_result.stdout}\n"
        f"stderr:\n{codegen_help_result.stderr}"
    )

    dev_help_result = run_bun_command(
        bun_binary=bun_binary,
        cwd=output_dir / "apps" / "backend",
        args=["run", "convex:dev:smoke"],
    )
    assert dev_help_result.returncode == 0, (
        "Expected backend Convex dev smoke command to succeed.\n"
        f"stdout:\n{dev_help_result.stdout}\n"
        f"stderr:\n{dev_help_result.stderr}"
    )

    codegen_output = f"{codegen_help_result.stdout}\n{codegen_help_result.stderr}"
    dev_output = f"{dev_help_result.stdout}\n{dev_help_result.stderr}"
    assert "codegen" in codegen_output.lower()
    assert "dev" in dev_output.lower()

    backend_dev_result = run_bun_command(
        bun_binary=bun_binary,
        cwd=output_dir / "apps" / "backend",
        args=["run", "dev"],
    )
    assert backend_dev_result.returncode == 0, (
        "Expected backend dev command to succeed in CI-safe mode.\n"
        f"stdout:\n{backend_dev_result.stdout}\n"
        f"stderr:\n{backend_dev_result.stderr}"
    )

    backend_test_result = run_bun_command(
        bun_binary=bun_binary,
        cwd=output_dir / "apps" / "backend",
        args=["run", "test"],
    )
    assert backend_test_result.returncode == 0, (
        "Expected backend test command to succeed in CI-safe mode.\n"
        f"stdout:\n{backend_test_result.stdout}\n"
        f"stderr:\n{backend_test_result.stderr}"
    )
