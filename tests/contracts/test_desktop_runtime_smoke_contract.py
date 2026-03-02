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


def test_desktop_runtime_smoke_commands_and_unsigned_output_paths(
    tmp_path: Path,
) -> None:
    """Desktop target should expose CI-safe Forge smoke commands and artifact paths."""

    bun_binary = shutil.which("bun")
    if bun_binary is None:
        pytest.skip("bun executable is required for desktop runtime smoke contract")

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "desktop-runtime-smokes"

    scaffold_result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "desktop",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )
    assert scaffold_result.returncode == 0, (
        "Expected desktop scaffold command to succeed before runtime smoke checks.\n"
        f"stdout:\n{scaffold_result.stdout}\n"
        f"stderr:\n{scaffold_result.stderr}"
    )

    install_result = run_bun_command(
        bun_binary=bun_binary,
        cwd=output_dir,
        args=["install", "--frozen-lockfile"],
    )
    assert install_result.returncode == 0, (
        "Expected `bun install --frozen-lockfile` to succeed for desktop scaffold.\n"
        f"stdout:\n{install_result.stdout}\n"
        f"stderr:\n{install_result.stderr}"
    )

    desktop_manifest = json.loads(
        (output_dir / "apps" / "desktop" / "package.json").read_text(encoding="utf-8")
    )
    desktop_scripts = desktop_manifest.get("scripts", {})

    assert desktop_scripts.get("desktop:start") == "electron-forge start"
    assert desktop_scripts.get("desktop:package") == (
        "electron-forge package --outDir out/unsigned/package"
    )
    assert desktop_scripts.get("desktop:make") == (
        "electron-forge make --outDir out/unsigned/make"
    )
    assert desktop_scripts.get("desktop:start:smoke") == "electron-forge start --help"
    assert desktop_scripts.get("desktop:package:smoke") == (
        "electron-forge package --help --outDir out/unsigned-smoke/package"
    )
    assert desktop_scripts.get("desktop:make:smoke") == (
        "electron-forge make --help --outDir out/unsigned-smoke/make"
    )

    desktop_dir = output_dir / "apps" / "desktop"
    start_smoke_result = run_bun_command(
        bun_binary=bun_binary,
        cwd=desktop_dir,
        args=["run", "desktop:start:smoke"],
    )
    assert start_smoke_result.returncode == 0, (
        "Expected desktop start smoke command to succeed.\n"
        f"stdout:\n{start_smoke_result.stdout}\n"
        f"stderr:\n{start_smoke_result.stderr}"
    )

    package_smoke_result = run_bun_command(
        bun_binary=bun_binary,
        cwd=desktop_dir,
        args=["run", "desktop:package:smoke"],
    )
    assert package_smoke_result.returncode == 0, (
        "Expected desktop package smoke command to succeed.\n"
        f"stdout:\n{package_smoke_result.stdout}\n"
        f"stderr:\n{package_smoke_result.stderr}"
    )

    root_dev_result = run_bun_command(
        bun_binary=bun_binary,
        cwd=output_dir,
        args=["run", "dev"],
    )
    assert root_dev_result.returncode == 0, (
        "Expected root dev command to pass desktop runtime smoke path.\n"
        f"stdout:\n{root_dev_result.stdout}\n"
        f"stderr:\n{root_dev_result.stderr}"
    )

    root_build_result = run_bun_command(
        bun_binary=bun_binary,
        cwd=output_dir,
        args=["run", "build"],
    )
    assert root_build_result.returncode == 0, (
        "Expected root build command to pass desktop package smoke path.\n"
        f"stdout:\n{root_build_result.stdout}\n"
        f"stderr:\n{root_build_result.stderr}"
    )
