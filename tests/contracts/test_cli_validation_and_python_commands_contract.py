from __future__ import annotations

import os
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


def test_auth_without_web_backend_fails_with_deterministic_error(
    tmp_path: Path,
) -> None:
    """RED: auth flag without backend must fail with deterministic message."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "foundation-auth-output"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "foundation",
            "--no-interactive",
            "--dry-run",
            "--output",
            str(output_dir),
            "--auth",
            "clerk",
        ],
    )

    assert result.returncode == 2
    assert "auth option is only valid when backend target is selected" in result.stderr


def test_missing_no_interactive_fails_with_clear_error(tmp_path: Path) -> None:
    """CLI should fail clearly when non-interactive flag is omitted."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "foundation-interactive-output"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "foundation",
            "--dry-run",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 2
    assert (
        "interactive mode is not implemented yet; use --no-interactive" in result.stderr
    )


@pytest.mark.parametrize(
    ("target_args", "output_name"),
    [
        (["--target", "foundation"], "foundation-no-interactive"),
        (["--target", "python"], "python-no-interactive"),
        (["--target", "typescript-cli"], "typescript-cli-no-interactive"),
        (["--target", "python-lib"], "python-lib-no-interactive"),
        (["--target", "typescript-lib"], "typescript-lib-no-interactive"),
        (
            [
                "--target",
                "web",
                "--target",
                "backend",
                "--auth",
                "clerk",
            ],
            "web-backend-no-interactive",
        ),
        (["--target", "mobile", "--target", "tv"], "mobile-tv-no-interactive"),
    ],
)
def test_missing_no_interactive_fails_across_target_modes(
    tmp_path: Path,
    target_args: list[str],
    output_name: str,
) -> None:
    """Non-interactive flag omission should fail consistently for all target modes."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / output_name

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            *target_args,
            "--dry-run",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 2
    assert (
        "interactive mode is not implemented yet; use --no-interactive" in result.stderr
    )


def test_missing_required_target_fails_with_deterministic_error(tmp_path: Path) -> None:
    """Missing --target should fail clearly in non-interactive mode."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "missing-target-output"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--no-interactive",
            "--dry-run",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 2
    assert "the following arguments are required: --target" in result.stderr


def test_missing_required_output_fails_with_deterministic_error() -> None:
    """Missing --output should fail clearly in non-interactive mode."""

    repo_root = Path(__file__).resolve().parents[2]

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "foundation",
            "--no-interactive",
            "--dry-run",
        ],
    )

    assert result.returncode == 2
    assert "the following arguments are required: --output" in result.stderr


def test_invalid_target_choice_fails_with_deterministic_error(tmp_path: Path) -> None:
    """Invalid target values should fail with argparse choice guidance."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "invalid-target-output"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "invalid",
            "--no-interactive",
            "--dry-run",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 2
    assert "argument --target: invalid choice: 'invalid'" in result.stderr


def test_invalid_auth_choice_fails_with_deterministic_error(tmp_path: Path) -> None:
    """Invalid auth values should fail with argparse choice guidance."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "invalid-auth-output"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "web",
            "--target",
            "backend",
            "--auth",
            "invalid",
            "--no-interactive",
            "--dry-run",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 2
    assert "argument --auth: invalid choice: 'invalid'" in result.stderr


def test_python_scaffold_includes_baseline_uv_commands(tmp_path: Path) -> None:
    """RED: Python lane should include baseline uv setup/check commands."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "python-command-output"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "python",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected python scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    command_doc = output_dir / "apps" / "python" / "README.md"
    assert command_doc.exists(), "Python lane should include command documentation"

    command_doc_text = command_doc.read_text(encoding="utf-8")
    assert "Python Lane" in command_doc_text
    assert "Baseline developer commands" in command_doc_text
    assert "uv sync" in command_doc_text
    assert "python-app" in command_doc_text
    assert "python-app-tui" in command_doc_text
    assert "pytest" in command_doc_text
    assert "ruff" in command_doc_text
    assert "mypy" in command_doc_text
