from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest


def _resolve_posix_shell() -> str:
    """Return a usable POSIX shell executable for script contract tests."""

    if sys.platform == "win32":
        pytest.skip(
            "installer shell-script dry-run contracts are validated on POSIX runners"
        )

    bash_path = shutil.which("bash")
    if bash_path is not None:
        return bash_path

    sh_path = shutil.which("sh")
    if sh_path is not None:
        return sh_path

    pytest.skip("POSIX shell executable not available for installer script contract")


def test_update_opencode_script_supports_dry_run_and_lists_turbo_and_gh() -> None:
    """RED: update-opencode dry-run should include turborepo and gh coverage."""

    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / ".template_scripts" / "update-opencode.sh"

    shell = _resolve_posix_shell()
    result = subprocess.run(
        [shell, str(script_path), "--dry-run"],
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
    assert "gh" in combined_output


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

    shell = _resolve_posix_shell()
    result = subprocess.run(
        [shell, "install.sh", "--dry-run"],
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

    shell = _resolve_posix_shell()
    result = subprocess.run(
        [
            shell,
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
