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


def test_tv_scaffold_includes_input_hid_checklist(tmp_path: Path) -> None:
    """TV scaffold should include remote-first HID checklist guidance."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "tv-input-checklist"

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

    checklist_path = output_dir / "apps" / "tv" / "TV_INPUT_CHECKLIST.md"
    assert checklist_path.exists(), f"Expected TV input checklist at {checklist_path}"

    checklist_text = checklist_path.read_text(encoding="utf-8")
    assert "remote-primary" in checklist_text
    assert "focus" in checklist_text
    assert "navigation" in checklist_text
    assert "keyboard" in checklist_text
    assert "mouse" in checklist_text
    assert "gamepad" in checklist_text


def test_tv_app_baseline_includes_remote_primary_focus_wiring(tmp_path: Path) -> None:
    """TV App baseline should scaffold deterministic remote-first focus wiring."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "tv-input-app"

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

    app_tsx = (output_dir / "apps" / "tv" / "App.tsx").read_text(encoding="utf-8")
    assert "useTVEventHandler" in app_tsx
    assert "hasTVPreferredFocus" in app_tsx
    assert "onFocus" in app_tsx
    assert "remote-primary" in app_tsx


def test_tv_dry_run_reports_input_hid_checklist_path(tmp_path: Path) -> None:
    """Dry-run should report TV HID checklist output path."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "tv-input-dry-run"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "tv",
            "--no-interactive",
            "--dry-run",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected tv-only dry-run scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "apps/tv/TV_INPUT_CHECKLIST.md" in combined_output
    assert not output_dir.exists(), "--dry-run should not write scaffold output"
