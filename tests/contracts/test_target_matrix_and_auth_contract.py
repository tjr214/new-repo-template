from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


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


def test_web_backend_requires_explicit_auth_in_non_interactive_mode(
    tmp_path: Path,
) -> None:
    """RED: web+backend without auth should fail deterministically."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "web-backend-no-auth"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "web",
            "--target",
            "backend",
            "--no-interactive",
            "--dry-run",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 2
    assert (
        "auth option is required when both web and backend targets are selected"
        in result.stderr
    )


def test_web_backend_with_auth_succeeds_and_is_dry_run_only(tmp_path: Path) -> None:
    """RED: web+backend with auth should resolve and avoid writes in dry-run."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "web-backend-with-auth"

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
        "Expected web+backend dry-run to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "apps/web/" in combined_output
    assert "apps/backend/" in combined_output
    assert not output_dir.exists(), "--dry-run should not write scaffold output"


def test_foundation_target_cannot_be_combined_with_other_targets(
    tmp_path: Path,
) -> None:
    """RED: foundation must be standalone and fail when mixed."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "foundation-plus-python"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "foundation",
            "--target",
            "python",
            "--no-interactive",
            "--dry-run",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 2
    assert "foundation target cannot be combined with other targets" in result.stderr


def test_mobile_and_tv_targets_create_distinct_apps(tmp_path: Path) -> None:
    """RED: selecting mobile+tv should scaffold both separate app directories."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "mobile-tv-output"

    result = run_scaffold_command(
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

    assert result.returncode == 0, (
        "Expected mobile+tv scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    assert (output_dir / "pyproject.toml").exists()
    assert (output_dir / "apps" / "mobile").exists()
    assert (output_dir / "apps" / "tv").exists()


def test_tv_only_scaffold_keeps_root_pyproject_invariant(tmp_path: Path) -> None:
    """TV-only scaffold still requires root pyproject.toml."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "tv-only-output"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "tv",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected tv-only scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    assert (output_dir / "pyproject.toml").exists()
    assert (output_dir / "apps" / "tv").exists()


def test_web_only_scaffold_keeps_root_pyproject_invariant(tmp_path: Path) -> None:
    """JS-only web scaffold still requires root pyproject.toml."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "web-only-output"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "web",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected web-only scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    assert (output_dir / "pyproject.toml").exists()
    assert (output_dir / "apps" / "web").exists()
