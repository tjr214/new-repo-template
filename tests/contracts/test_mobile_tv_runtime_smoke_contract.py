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


def test_mobile_tv_lint_typecheck_test_baseline_scripts_run_in_ci_safe_mode(
    tmp_path: Path,
) -> None:
    """Generated mobile/tv apps should run lint/typecheck/test baseline scripts."""

    bun_binary = shutil.which("bun")
    if bun_binary is None:
        pytest.skip("bun executable is required for mobile/tv runtime smoke contract")

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "mobile-tv-runtime-smokes"

    scaffold_result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "mobile",
            "--target",
            "tv",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )
    assert scaffold_result.returncode == 0, (
        "Expected mobile+tv scaffold command to succeed before runtime smoke checks.\n"
        f"stdout:\n{scaffold_result.stdout}\n"
        f"stderr:\n{scaffold_result.stderr}"
    )

    install_result = run_bun_command(
        bun_binary=bun_binary,
        cwd=output_dir,
        args=["install", "--frozen-lockfile"],
    )
    assert install_result.returncode == 0, (
        "Expected `bun install --frozen-lockfile` to succeed for mobile+tv scaffold.\n"
        f"stdout:\n{install_result.stdout}\n"
        f"stderr:\n{install_result.stderr}"
    )

    mobile_manifest = json.loads(
        (output_dir / "apps" / "mobile" / "mobile" / "package.json").read_text(
            encoding="utf-8"
        )
    )
    mobile_scripts = mobile_manifest.get("scripts", {})
    assert mobile_scripts.get("lint") == "bun run mobile:lint:smoke"
    assert mobile_scripts.get("typecheck") == "bun run mobile:typecheck:smoke"
    assert mobile_scripts.get("test") == "bun run mobile:test:smoke"

    tv_manifest = json.loads(
        (output_dir / "apps" / "tv" / "tv" / "package.json").read_text(encoding="utf-8")
    )
    tv_scripts = tv_manifest.get("scripts", {})
    assert tv_scripts.get("lint") == "bun run tv:lint:smoke"
    assert tv_scripts.get("typecheck") == "bun run tv:typecheck:smoke"
    assert tv_scripts.get("test") == "bun run tv:test:smoke"

    mobile_dir = output_dir / "apps" / "mobile" / "mobile"
    tv_dir = output_dir / "apps" / "tv" / "tv"

    for script_name in ("lint", "typecheck", "test"):
        mobile_result = run_bun_command(
            bun_binary=bun_binary,
            cwd=mobile_dir,
            args=["run", script_name],
        )
        assert mobile_result.returncode == 0, (
            f"Expected mobile `{script_name}` script to succeed.\n"
            f"stdout:\n{mobile_result.stdout}\n"
            f"stderr:\n{mobile_result.stderr}"
        )

        tv_result = run_bun_command(
            bun_binary=bun_binary,
            cwd=tv_dir,
            args=["run", script_name],
        )
        assert tv_result.returncode == 0, (
            f"Expected tv `{script_name}` script to succeed.\n"
            f"stdout:\n{tv_result.stdout}\n"
            f"stderr:\n{tv_result.stderr}"
        )
