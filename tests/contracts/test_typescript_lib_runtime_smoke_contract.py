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


def test_typescript_lib_runtime_scripts_install_and_run(tmp_path: Path) -> None:
    """Generated TypeScript library should install and run baseline package scripts."""

    bun_binary = shutil.which("bun")
    if bun_binary is None:
        pytest.skip(
            "bun executable is required for typescript-lib runtime smoke contract"
        )

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "typescript-lib-runtime"

    scaffold_result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "typescript-lib",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )
    assert scaffold_result.returncode == 0, (
        "Expected typescript-lib scaffold command to succeed before runtime smoke checks.\n"
        f"stdout:\n{scaffold_result.stdout}\n"
        f"stderr:\n{scaffold_result.stderr}"
    )

    install_result = run_bun_command(
        bun_binary=bun_binary,
        cwd=output_dir,
        args=["install", "--frozen-lockfile"],
    )
    assert install_result.returncode == 0, (
        "Expected `bun install --frozen-lockfile` to succeed for typescript-lib scaffold.\n"
        f"stdout:\n{install_result.stdout}\n"
        f"stderr:\n{install_result.stderr}"
    )

    library_root = output_dir / "packages" / "typescript" / "typescript-lib"
    manifest = json.loads((library_root / "package.json").read_text(encoding="utf-8"))
    scripts = manifest.get("scripts", {})
    assert scripts.get("build") == "tsc -p tsconfig.json"
    assert scripts.get("test") == "bun test"
    assert scripts.get("lint") == "bun --version"
    assert scripts.get("typecheck") == "tsc --noEmit"

    for script_name in ("build", "test", "lint", "typecheck"):
        script_result = run_bun_command(
            bun_binary=bun_binary,
            cwd=library_root,
            args=["run", script_name],
        )
        assert script_result.returncode == 0, (
            f"Expected TypeScript library `{script_name}` script to succeed.\n"
            f"stdout:\n{script_result.stdout}\n"
            f"stderr:\n{script_result.stderr}"
        )

    assert (library_root / "dist" / "index.js").exists(), (
        "Expected build script to emit dist/index.js for the generated TypeScript library"
    )
