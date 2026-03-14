from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _assert_text_has_terms(text: str, *terms: str) -> None:
    normalized = text.lower()
    for term in terms:
        assert term.lower() in normalized


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


def test_mobile_scaffold_includes_setup_and_validation_readme(tmp_path: Path) -> None:
    """Mobile target should scaffold setup docs with CI-safe validation commands."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "mobile-setup-docs"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "mobile",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected mobile-only scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    readme_path = output_dir / "apps" / "mobile" / "mobile" / "README.md"
    assert readme_path.exists(), f"Expected mobile setup README at {readme_path}"

    readme_text = readme_path.read_text(encoding="utf-8")
    _assert_text_has_terms(
        readme_text,
        "Mobile Setup",
        "CI-Safe Validation Commands",
        "lint",
        "typecheck",
        "test",
        "device-free",
    )


def test_tv_scaffold_includes_emulator_and_shield_validation_docs(
    tmp_path: Path,
) -> None:
    """TV target should scaffold AndroidTV emulator and Shield validation guidance."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "tv-setup-docs"

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

    tv_root = output_dir / "apps" / "tv" / "tv"
    readme_path = tv_root / "README.md"
    assert readme_path.exists(), f"Expected TV setup README at {readme_path}"

    readme_text = readme_path.read_text(encoding="utf-8")
    _assert_text_has_terms(
        readme_text,
        "TV Setup",
        "Validation Flow",
        "Android TV Emulator",
        "NVIDIA Shield",
        "remote-primary",
        "TV_INPUT_CHECKLIST.md",
        "TV_VALIDATION_LOG.md",
    )

    checklist_text = (tv_root / "TV_INPUT_CHECKLIST.md").read_text(encoding="utf-8")
    _assert_text_has_terms(
        checklist_text,
        "Android TV Emulator",
        "NVIDIA Shield",
        "remote-primary",
        "keyboard",
        "mouse",
        "gamepad",
    )

    validation_log_text = (tv_root / "TV_VALIDATION_LOG.md").read_text(encoding="utf-8")
    _assert_text_has_terms(
        validation_log_text,
        "Run Metadata",
        "Android TV Emulator Pass",
        "NVIDIA Shield Pass",
        "remote-primary",
        "keyboard",
        "mouse",
        "gamepad",
    )


def test_mobile_tv_dry_run_reports_setup_docs_paths(tmp_path: Path) -> None:
    """Dry-run for mobile+tv should report setup/validation README paths."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "mobile-tv-setup-docs-dry-run"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "mobile",
            "--target",
            "tv",
            "--no-interactive",
            "--dry-run",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected mobile+tv dry-run scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "apps/mobile/mobile/README.md" in combined_output
    assert "apps/tv/tv/README.md" in combined_output
    assert "apps/tv/tv/TV_VALIDATION_LOG.md" in combined_output
    assert not output_dir.exists(), "--dry-run should not write scaffold output"
