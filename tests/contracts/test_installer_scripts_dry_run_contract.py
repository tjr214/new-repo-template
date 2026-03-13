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


def test_legacy_install_script_is_absent_from_repo_root() -> None:
    """The root repo should no longer carry the removed legacy install script."""

    repo_root = Path(__file__).resolve().parents[2]
    assert not (repo_root / "install.sh").exists()


def test_branch_protection_script_lives_under_scripts_directory() -> None:
    """Branch-protection automation should live in `scripts/`, not `.template_scripts/`."""

    repo_root = Path(__file__).resolve().parents[2]
    assert (repo_root / "scripts" / "configure-repo-protections.sh").exists()
    assert not (
        repo_root / ".template_scripts" / "configure-repo-protections.sh"
    ).exists()


def test_configure_repo_protections_script_dry_run_reports_actions() -> None:
    """RED: protections script dry-run should show branch-protection + dependabot actions."""

    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "scripts" / "configure-repo-protections.sh"

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
    assert "- required approvals: 0" in combined_output
    assert "Tests (ubuntu-latest)" in combined_output


def test_configure_repo_protections_defaults_branch_and_auto_detects_repo(
    tmp_path: Path,
) -> None:
    """Protections script should auto-detect repo and default branch to main."""

    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "scripts" / "configure-repo-protections.sh"

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
    assert "- required approvals: 0" in combined_output


def test_configure_repo_protections_allows_explicit_required_approvals() -> None:
    """Dry-run output should reflect non-default approval requirements."""

    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "scripts" / "configure-repo-protections.sh"

    shell = _resolve_posix_shell()
    result = subprocess.run(
        [
            shell,
            str(script_path),
            "--dry-run",
            "--repo",
            "example-org/example-repo",
            "--required-approvals",
            "2",
            "--required-check",
            "Tests (ubuntu-latest)",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, (
        "Expected protections script dry-run with explicit approvals to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "- required approvals: 2" in combined_output
    assert '"required_approving_review_count": 2' in combined_output
