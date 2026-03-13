from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


def _removed_root_doc_name() -> str:
    return "CLAUDE" + ".md"


def _removed_config_dir_name() -> str:
    return "." + "claude"


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


def test_legacy_template_update_script_excludes_removed_assistant_assets() -> None:
    """RED: legacy template sync script should not manage removed assistant assets."""

    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / ".template_scripts" / "update-template-from-git.sh"
    script_text = script_path.read_text(encoding="utf-8")

    assert _removed_root_doc_name() not in script_text
    assert _removed_config_dir_name() not in script_text


def test_install_script_dry_run_is_non_destructive(tmp_path: Path) -> None:
    """RED: install script dry-run should not mutate repo state."""

    repo_root = Path(__file__).resolve().parents[2]
    sandbox_root = tmp_path / "installer-sandbox"
    sandbox_root.mkdir(parents=True)

    (sandbox_root / ".template_scripts").mkdir()
    shutil.copy2(repo_root / "install.sh", sandbox_root / "install.sh")
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
    assert "nurt sync bmad --dry-run" in combined_output
    assert "nurt sync tools --dry-run" in combined_output
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


def test_configure_repo_protections_script_dry_run_reports_actions() -> None:
    """RED: protections script dry-run should show branch-protection + dependabot actions."""

    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / ".template_scripts" / "configure-repo-protections.sh"

    shell = _resolve_posix_shell()
    result = subprocess.run(
        [
            shell,
            str(script_path),
            "--dry-run",
            "--repo",
            "example-org/example-repo",
            "--branch",
            "main",
            "--required-check",
            "Tests (ubuntu-latest)",
            "--required-check",
            "Preset Regression Suite",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, (
        "Expected protections script dry-run to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "DRY RUN" in combined_output
    assert "dependabot_security_updates" in combined_output
    assert "Require a pull request before merging" in combined_output
    assert "Tests (ubuntu-latest)" in combined_output


def test_configure_repo_protections_defaults_branch_and_auto_detects_repo(
    tmp_path: Path,
) -> None:
    """Protections script should auto-detect repo and default branch to main."""

    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / ".template_scripts" / "configure-repo-protections.sh"

    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir(parents=True)
    fake_gh = fake_bin / "gh"
    fake_gh.write_text(
        """#!/bin/sh
if [ "$1" = "repo" ] && [ "$2" = "view" ] && [ "$3" = "--json" ] && [ "$4" = "nameWithOwner" ]; then
    printf "fake-owner/fake-repo\\n"
    exit 0
fi

printf "unexpected gh invocation: %s\\n" "$*" >&2
exit 9
""",
        encoding="utf-8",
    )
    fake_gh.chmod(0o755)

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}{os.pathsep}{env.get('PATH', '')}"

    shell = _resolve_posix_shell()
    result = subprocess.run(
        [
            shell,
            str(script_path),
            "--dry-run",
            "--required-check",
            "Tests (ubuntu-latest)",
        ],
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, (
        "Expected protections script dry-run defaults to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "- repo: fake-owner/fake-repo" in combined_output
    assert "- branch: main" in combined_output
