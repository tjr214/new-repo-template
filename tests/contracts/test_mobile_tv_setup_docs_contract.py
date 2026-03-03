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

    readme_path = output_dir / "apps" / "mobile" / "README.md"
    assert readme_path.exists(), f"Expected mobile setup README at {readme_path}"

    readme_text = readme_path.read_text(encoding="utf-8")
    assert "Mobile Setup" in readme_text
    assert "expo lint" in readme_text
    assert "tsc --noEmit" in readme_text
    assert "--non-interactive" in readme_text


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

    tv_root = output_dir / "apps" / "tv"
    readme_path = tv_root / "README.md"
    assert readme_path.exists(), f"Expected TV setup README at {readme_path}"

    readme_text = readme_path.read_text(encoding="utf-8")
    assert "TV Setup" in readme_text
    assert "Android TV Emulator" in readme_text
    assert "NVIDIA Shield" in readme_text
    assert "remote-primary" in readme_text

    checklist_text = (tv_root / "TV_INPUT_CHECKLIST.md").read_text(encoding="utf-8")
    assert "Android TV Emulator" in checklist_text
    assert "Shield" in checklist_text
    assert "keyboard" in checklist_text
    assert "mouse" in checklist_text
    assert "gamepad" in checklist_text


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
    assert "apps/mobile/README.md" in combined_output
    assert "apps/tv/README.md" in combined_output
    assert not output_dir.exists(), "--dry-run should not write scaffold output"
