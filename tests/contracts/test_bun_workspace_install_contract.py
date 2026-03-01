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


def test_web_backend_dry_run_reports_workspace_package_manifests(
    tmp_path: Path,
) -> None:
    """RED: dry-run should expose JS workspace package manifests."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "web-backend-dry-run"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "web",
            "--target",
            "backend",
            "--auth",
            "clerk",
            "--no-interactive",
            "--dry-run",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected web+backend dry-run scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "package.json" in combined_output
    assert "apps/web/package.json" in combined_output
    assert "apps/backend/package.json" in combined_output


def test_generated_web_backend_workspace_supports_bun_install(tmp_path: Path) -> None:
    """RED: generated JS workspace should be installable with bun."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "web-backend-install"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "web",
            "--target",
            "backend",
            "--auth",
            "better-auth",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected web+backend scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    root_manifest = output_dir / "package.json"
    web_manifest = output_dir / "apps" / "web" / "package.json"
    backend_manifest = output_dir / "apps" / "backend" / "package.json"

    assert root_manifest.exists(), "root package.json must exist"
    assert web_manifest.exists(), "web workspace package.json must exist"
    assert backend_manifest.exists(), "backend workspace package.json must exist"

    root_data = json.loads(root_manifest.read_text(encoding="utf-8"))
    assert root_data.get("workspaces") == ["apps/*", "packages/*"]

    for manifest_path in (web_manifest, backend_manifest):
        package_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        scripts = package_data.get("scripts")
        assert isinstance(scripts, dict)
        for script_name in ("dev", "build", "test", "lint", "typecheck"):
            script_value = scripts.get(script_name)
            assert isinstance(script_value, str) and script_value != ""

    bun_binary = shutil.which("bun")
    if bun_binary is None:
        pytest.skip("bun executable is required for workspace install viability check")

    install_result = subprocess.run(
        [bun_binary, "install"],
        cwd=output_dir,
        capture_output=True,
        text=True,
        env=os.environ.copy(),
        check=False,
    )
    assert install_result.returncode == 0, (
        "Expected `bun install` to succeed for generated workspace.\n"
        f"stdout:\n{install_result.stdout}\n"
        f"stderr:\n{install_result.stderr}"
    )

    assert (output_dir / "bun.lock").exists() or (output_dir / "bun.lockb").exists(), (
        "bun install should create a root lockfile"
    )

    frozen_result = subprocess.run(
        [bun_binary, "install", "--frozen-lockfile"],
        cwd=output_dir,
        capture_output=True,
        text=True,
        env=os.environ.copy(),
        check=False,
    )
    assert frozen_result.returncode == 0, (
        "Expected `bun install --frozen-lockfile` to succeed after lockfile creation.\n"
        f"stdout:\n{frozen_result.stdout}\n"
        f"stderr:\n{frozen_result.stderr}"
    )
