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


def test_legacy_template_update_script_is_absent() -> None:
    """Feature 5.0 retires the old template sync shell script entirely."""

    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / ".template_scripts" / "update-template-from-git.sh"
    assert not script_path.exists()


def test_legacy_install_script_is_absent_from_repo_root() -> None:
    """The root repo should no longer carry the removed legacy install script."""

    repo_root = Path(__file__).resolve().parents[2]
    assert not (repo_root / "install.sh").exists()


def test_branch_protection_shell_script_is_absent_from_repo_and_snapshot_assets() -> (
    None
):
    """Feature 8.0 removes the old shell entrypoint immediately."""

    repo_root = Path(__file__).resolve().parents[2]
    assert not (repo_root / "scripts" / "configure-repo-protections.sh").exists()
    assert not (
        repo_root
        / "src"
        / "new_repo_template"
        / "snapshot_assets"
        / "templates"
        / "foundation"
        / "scripts"
        / "configure-repo-protections.sh"
    ).exists()


def test_nurt_secure_repo_dry_run_reports_actions() -> None:
    """The native secure-repo command should show the planned protections clearly."""

    repo_root = Path(__file__).resolve().parents[2]
    result = run_nurt_command(
        cwd=repo_root,
        args=[
            "secure-repo",
            "--dry-run",
            "--repo",
            "example-org/example-repo",
            "--branch",
            "main",
            "--required-check",
            "Tests (ubuntu-latest)",
            "--required-check",
            "Preset Regression Suite",
            "--no-interactive",
        ],
    )

    assert result.returncode == 0, (
        "Expected nurt secure-repo dry-run to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "DRY RUN" in combined_output
    assert "dependabot_security_updates" in combined_output
    assert "Require a pull request before merging" in combined_output
    assert "- required approvals: 0" in combined_output
    assert "Tests (ubuntu-latest)" in combined_output
    assert "scripts/configure-repo-protections.sh" not in combined_output


def test_nurt_secure_repo_defaults_branch_and_auto_detects_repo(tmp_path: Path) -> None:
    """The native command should keep branch and repo detection parity."""

    repo_root = Path(__file__).resolve().parents[2]
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

    result = run_nurt_command(
        cwd=repo_root,
        args=[
            "secure-repo",
            "--dry-run",
            "--required-check",
            "Tests (ubuntu-latest)",
            "--no-interactive",
        ],
        env=env,
    )

    assert result.returncode == 0, (
        "Expected secure-repo defaults dry-run to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "- repo: fake-owner/fake-repo" in combined_output
    assert "- branch: main" in combined_output
    assert "- required approvals: 0" in combined_output


def test_nurt_secure_repo_interactively_prompts_for_required_approvals() -> None:
    """Interactive secure-repo runs should ask for required approvals and default to 0."""

    repo_root = Path(__file__).resolve().parents[2]
    result = run_nurt_command(
        cwd=repo_root,
        args=[
            "secure-repo",
            "--dry-run",
            "--repo",
            "example-org/example-repo",
            "--required-check",
            "Tests (ubuntu-latest)",
        ],
        env={"NURT_UI_MODE": "plain"},
        input_text="\n",
    )

    assert result.returncode == 0, (
        "Expected interactive secure-repo dry-run to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "Repository approval policy" in combined_output
    assert "Required approvals [0]:" in combined_output
    assert "- required approvals: 0" in combined_output


def test_nurt_secure_repo_allows_explicit_required_approvals() -> None:
    """Explicit approval counts should flow through the dry-run payload."""

    repo_root = Path(__file__).resolve().parents[2]
    result = run_nurt_command(
        cwd=repo_root,
        args=[
            "secure-repo",
            "--dry-run",
            "--repo",
            "example-org/example-repo",
            "--required-approvals",
            "2",
            "--required-check",
            "Tests (ubuntu-latest)",
            "--no-interactive",
        ],
    )

    assert result.returncode == 0, (
        "Expected secure-repo dry-run with explicit approvals to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "- required approvals: 2" in combined_output
    assert '"required_approving_review_count": 2' in combined_output
