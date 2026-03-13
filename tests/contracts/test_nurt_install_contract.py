from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


def test_readme_documents_git_url_uv_tool_install_command() -> None:
    """README should document the current uv tool install syntax for git sources."""

    repo_root = Path(__file__).resolve().parents[2]
    readme_text = (repo_root / "README.md").read_text(encoding="utf-8")

    assert re.search(
        r"uv tool install git\+https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\.git",
        readme_text,
    )
    assert "<org>/<repo>" not in readme_text
    assert "uv tool install --from" not in readme_text


def test_uv_tool_install_from_local_git_repo_exposes_nurt_executable(
    tmp_path: Path,
) -> None:
    """Local git install smoke should validate the documented uv tool workflow."""

    uv_binary = shutil.which("uv")
    if uv_binary is None:
        pytest.skip("uv executable is required for install workflow contract")

    repo_root = Path(__file__).resolve().parents[2]
    revision_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert revision_result.returncode == 0, (
        "Expected to resolve the repository HEAD revision for uv install smoke.\n"
        f"stdout:\n{revision_result.stdout}\n"
        f"stderr:\n{revision_result.stderr}"
    )
    repo_revision = revision_result.stdout.strip()

    tool_dir = tmp_path / "uv-tools"
    tool_bin_dir = tmp_path / "uv-bin"
    cache_dir = tmp_path / "uv-cache"
    tool_dir.mkdir(parents=True)
    tool_bin_dir.mkdir(parents=True)
    cache_dir.mkdir(parents=True)

    env = os.environ.copy()
    env.update(
        {
            "UV_TOOL_DIR": str(tool_dir),
            "UV_TOOL_BIN_DIR": str(tool_bin_dir),
            "UV_CACHE_DIR": str(cache_dir),
            "PATH": f"{tool_bin_dir}{os.pathsep}{env.get('PATH', '')}",
            "NURT_UPDATE_CHECK_SIMULATE": "none",
        }
    )

    install_result = subprocess.run(
        [
            uv_binary,
            "tool",
            "install",
            "--python",
            sys.executable,
            "--force",
            f"git+file://{repo_root}@{repo_revision}",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert install_result.returncode == 0, (
        "Expected local git uv tool install to succeed.\n"
        f"stdout:\n{install_result.stdout}\n"
        f"stderr:\n{install_result.stderr}"
    )

    nurt_binary = shutil.which("nurt", path=str(tool_bin_dir))
    assert nurt_binary is not None, "uv tool install should expose a nurt executable"

    run_result = subprocess.run(
        [nurt_binary, "new", "demo-installed", "--dry-run", "--no-interactive"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert run_result.returncode == 0, (
        "Expected installed nurt executable to run successfully.\n"
        f"stdout:\n{run_result.stdout}\n"
        f"stderr:\n{run_result.stderr}"
    )

    combined_output = f"{run_result.stdout}\n{run_result.stderr}"
    assert "Resolved scaffold plan:" in combined_output
    assert "- targets: foundation" in combined_output
