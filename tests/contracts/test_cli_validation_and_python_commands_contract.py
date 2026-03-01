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


def test_auth_without_web_backend_fails_with_deterministic_error(
    tmp_path: Path,
) -> None:
    """RED: auth flag without web+backend must fail with deterministic message."""

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
    assert (
        "auth option is only valid when both web and backend targets are selected"
        in result.stderr
    )


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
    assert "uv sync --group dev" in command_doc_text
    assert "uv run pytest" in command_doc_text
    assert "uv run ruff check ." in command_doc_text
    assert "uv run mypy src" in command_doc_text
