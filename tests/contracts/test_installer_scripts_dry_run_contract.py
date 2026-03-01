from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def test_update_opencode_script_supports_dry_run_and_lists_turbo() -> None:
    """RED: update-opencode script should expose dry-run with turborepo coverage."""

    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / ".template_scripts" / "update-opencode.sh"

    result = subprocess.run(
        ["sh", str(script_path), "--dry-run"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, (
        "Expected update-opencode dry-run to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "DRY RUN" in combined_output
    assert "DRY-RUN" in combined_output
    assert "turbo" in combined_output


def test_install_script_dry_run_is_non_destructive(tmp_path: Path) -> None:
    """RED: install script dry-run should not mutate repo state."""

    repo_root = Path(__file__).resolve().parents[2]
    sandbox_root = tmp_path / "installer-sandbox"
    sandbox_root.mkdir(parents=True)

    (sandbox_root / ".template_scripts").mkdir()
    shutil.copy2(repo_root / "install.sh", sandbox_root / "install.sh")
    shutil.copy2(
        repo_root / ".template_scripts" / "update-opencode.sh",
        sandbox_root / ".template_scripts" / "update-opencode.sh",
    )
    shutil.copy2(
        repo_root / ".template_scripts" / "update-bmad-method.sh",
        sandbox_root / ".template_scripts" / "update-bmad-method.sh",
    )
    shutil.copytree(repo_root / "src", sandbox_root / "src")

    (sandbox_root / ".git").mkdir()
    (sandbox_root / ".git" / "HEAD").write_text(
        "ref: refs/heads/main\n", encoding="utf-8"
    )

    result = subprocess.run(
        ["sh", "install.sh", "--dry-run"],
        cwd=sandbox_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, (
        "Expected install dry-run to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "DRY RUN" in combined_output
    assert "Scaffold dry-run succeeded" in combined_output
    assert "sh .template_scripts/update-opencode.sh --dry-run" in combined_output
    assert (sandbox_root / ".git").exists(), ".git should remain in dry-run mode"
    assert (sandbox_root / "install.sh").exists(), (
        "install.sh should not be deleted in dry-run"
    )


def test_install_dry_run_accepts_target_and_auth_inputs(tmp_path: Path) -> None:
    """Installer dry-run should forward target/auth options to scaffold planning."""

    repo_root = Path(__file__).resolve().parents[2]
    sandbox_root = tmp_path / "installer-sandbox-target-auth"
    sandbox_root.mkdir(parents=True)

    (sandbox_root / ".template_scripts").mkdir()
    shutil.copy2(repo_root / "install.sh", sandbox_root / "install.sh")
    shutil.copy2(
        repo_root / ".template_scripts" / "update-opencode.sh",
        sandbox_root / ".template_scripts" / "update-opencode.sh",
    )
    shutil.copy2(
        repo_root / ".template_scripts" / "update-bmad-method.sh",
        sandbox_root / ".template_scripts" / "update-bmad-method.sh",
    )
    shutil.copytree(repo_root / "src", sandbox_root / "src")
    (sandbox_root / ".git").mkdir()
    (sandbox_root / ".git" / "HEAD").write_text(
        "ref: refs/heads/main\n", encoding="utf-8"
    )

    result = subprocess.run(
        [
            "sh",
            "install.sh",
            "--dry-run",
            "--target",
            "web",
            "--target",
            "backend",
            "--auth",
            "clerk",
        ],
        cwd=sandbox_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, (
        "Expected install dry-run with target/auth inputs to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "targets: web backend" in combined_output
    assert "auth: clerk" in combined_output
    assert "- targets: web, backend" in combined_output
    assert "- auth: clerk" in combined_output
    assert (sandbox_root / ".git").exists(), ".git should remain in dry-run mode"
