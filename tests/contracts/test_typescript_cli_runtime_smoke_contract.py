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


def test_typescript_cli_runtime_scripts_install_and_run(tmp_path: Path) -> None:
    """Generated TypeScript CLI app should install and run Bun-native baseline scripts."""

    bun_binary = shutil.which("bun")
    if bun_binary is None:
        pytest.skip(
            "bun executable is required for typescript-cli runtime smoke contract"
        )

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "typescript-cli-runtime"

    scaffold_result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "typescript-cli",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )
    assert scaffold_result.returncode == 0, (
        "Expected typescript-cli scaffold command to succeed before runtime smoke checks.\n"
        f"stdout:\n{scaffold_result.stdout}\n"
        f"stderr:\n{scaffold_result.stderr}"
    )

    install_result = run_bun_command(
        bun_binary=bun_binary,
        cwd=output_dir,
        args=["install", "--frozen-lockfile"],
    )
    assert install_result.returncode == 0, (
        "Expected `bun install --frozen-lockfile` to succeed for typescript-cli scaffold.\n"
        f"stdout:\n{install_result.stdout}\n"
        f"stderr:\n{install_result.stderr}"
    )

    cli_root = output_dir / "apps" / "typescript-cli" / "typescript-cli"
    manifest = json.loads((cli_root / "package.json").read_text(encoding="utf-8"))
    scripts = manifest.get("scripts", {})
    assert scripts.get("dev") == "bun run ./src/cli.ts"
    assert scripts.get("start") == "bun run ./src/cli.ts"
    assert (
        scripts.get("build")
        == "bun build ./src/cli.ts --outfile ./dist/cli.js --target bun"
    )
    assert scripts.get("test") == "bun test"
    assert scripts.get("lint") == "bun --version"
    assert scripts.get("typecheck") == "tsc --noEmit"

    dev_result = run_bun_command(
        bun_binary=bun_binary,
        cwd=cli_root,
        args=["run", "dev", "--", "--help"],
    )
    assert dev_result.returncode == 0, (
        "Expected TypeScript CLI `dev` script to succeed.\n"
        f"stdout:\n{dev_result.stdout}\n"
        f"stderr:\n{dev_result.stderr}"
    )
    assert "Usage:" in f"{dev_result.stdout}\n{dev_result.stderr}"

    for script_name in ("build", "test", "lint", "typecheck"):
        script_result = run_bun_command(
            bun_binary=bun_binary,
            cwd=cli_root,
            args=["run", script_name],
        )
        assert script_result.returncode == 0, (
            f"Expected TypeScript CLI `{script_name}` script to succeed.\n"
            f"stdout:\n{script_result.stdout}\n"
            f"stderr:\n{script_result.stderr}"
        )

    assert (cli_root / "dist" / "cli.js").exists(), (
        "Expected build script to emit a runnable dist/cli.js artifact"
    )
