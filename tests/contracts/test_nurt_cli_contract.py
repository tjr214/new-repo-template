from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def run_nurt_command(
    *,
    cwd: Path,
    args: list[str],
    env: dict[str, str] | None = None,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    command_env = os.environ.copy()
    repo_root = Path(__file__).resolve().parents[2]
    command_env["PYTHONPATH"] = str(repo_root / "src")
    command_env.setdefault("NURT_UPDATE_CHECK_SIMULATE", "none")
    if env is not None:
        command_env.update(env)

    return subprocess.run(
        [sys.executable, "-m", "new_repo_template.nurt_cli", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        input=input_text,
        env=command_env,
        check=False,
    )


def test_nurt_new_dry_run_generates_scaffold_plan_without_writing(
    tmp_path: Path,
) -> None:
    """RED: nurt new dry-run should route into scaffold plan generation."""

    output_dir = tmp_path / "demo-web-backend"
    result = run_nurt_command(
        cwd=tmp_path,
        args=[
            "new",
            output_dir.name,
            "--target",
            "web",
            "--target",
            "backend",
            "--auth",
            "clerk",
            "--dry-run",
        ],
    )

    assert result.returncode == 0, (
        "Expected nurt new --dry-run to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "Resolved scaffold plan:" in combined_output
    assert "- targets: web, backend" in combined_output
    assert not output_dir.exists(), "dry-run should not create project directory"


def test_nurt_new_defaults_to_foundation_when_targets_omitted(tmp_path: Path) -> None:
    """RED: nurt new should default to foundation in non-interactive mode."""

    output_dir = tmp_path / "demo-foundation"
    result = run_nurt_command(
        cwd=tmp_path,
        args=["new", output_dir.name, "--dry-run", "--no-interactive"],
    )

    assert result.returncode == 0, (
        "Expected default nurt new dry-run to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "- targets: foundation" in combined_output
    assert not output_dir.exists(), "dry-run should not create project directory"


def test_nurt_new_interactive_wizard_resolves_web_backend_with_prompted_auth(
    tmp_path: Path,
) -> None:
    """Interactive wizard should resolve targets and auth without explicit flags."""

    output_dir = tmp_path / "demo-interactive"
    result = run_nurt_command(
        cwd=tmp_path,
        args=["new", output_dir.name, "--dry-run"],
        input_text="3,4\n2\n",
    )

    assert result.returncode == 0, (
        "Expected interactive nurt new dry-run to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "nurt new interactive mode" in combined_output
    assert "- targets: web, backend" in combined_output
    assert "- auth: better-auth" in combined_output
    assert not output_dir.exists(), "dry-run should not create project directory"


def test_nurt_update_dry_run_prints_upgrade_command(tmp_path: Path) -> None:
    """RED: nurt update dry-run should be non-destructive and explicit."""

    result = run_nurt_command(cwd=tmp_path, args=["update", "--dry-run"])

    assert result.returncode == 0, (
        "Expected nurt update --dry-run to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "DRY RUN" in combined_output
    assert "uv tool upgrade nurt" in combined_output


def test_nurt_startup_update_check_notice_appears_when_update_available(
    tmp_path: Path,
) -> None:
    """RED: every nurt invocation should run update-check and notify when update exists."""

    result = run_nurt_command(
        cwd=tmp_path,
        args=["new", "demo-update-notice", "--dry-run", "--no-interactive"],
        env={"NURT_UPDATE_CHECK_SIMULATE": "9.9.9"},
    )

    assert result.returncode == 0, (
        "Expected nurt command to succeed with simulated update notice.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    assert "Update available for nurt: 9.9.9" in result.stderr


def test_nurt_template_assets_sync_dry_run_reports_action(tmp_path: Path) -> None:
    """RED: template-assets sync dry-run should report non-destructive action plan."""

    result = run_nurt_command(
        cwd=tmp_path, args=["template-assets", "sync", "--dry-run"]
    )

    assert result.returncode == 0, (
        "Expected nurt template-assets sync --dry-run to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "DRY RUN" in combined_output
    assert "template-assets sync" in combined_output


def test_nurt_tools_sync_dry_run_reports_action(tmp_path: Path) -> None:
    """RED: tools sync dry-run should report non-destructive action plan."""

    result = run_nurt_command(cwd=tmp_path, args=["tools", "sync", "--dry-run"])

    assert result.returncode == 0, (
        "Expected nurt tools sync --dry-run to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "DRY RUN" in combined_output
    assert "update-opencode.sh --dry-run" in combined_output


def test_nurt_template_assets_snapshot_dry_run_reports_action(tmp_path: Path) -> None:
    """template-assets snapshot dry-run should report snapshot planning details."""

    (tmp_path / ".gitignore").write_text(".env\n", encoding="utf-8")

    result = run_nurt_command(
        cwd=tmp_path,
        args=[
            "template-assets",
            "snapshot",
            "--dry-run",
            "--source-root",
            str(tmp_path),
        ],
    )

    assert result.returncode == 0, (
        "Expected template-assets snapshot dry-run to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "DRY RUN" in combined_output
    assert "would copy: templates/root_gitignore.txt" in combined_output
