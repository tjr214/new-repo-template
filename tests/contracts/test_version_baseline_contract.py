from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def run_nurt_command(
    *, cwd: Path, args: list[str], env: dict[str, str] | None = None
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
        env=command_env,
        check=False,
    )


def write_baseline(path: Path, versions: dict[str, str]) -> None:
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "generated_at": "2026-03-01T00:00:00Z",
                "managed_tools": {
                    tool: {"version": version}
                    for tool, version in sorted(versions.items())
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def write_latest_source(path: Path, versions: dict[str, str]) -> None:
    path.write_text(
        json.dumps(versions, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def test_nurt_versions_check_validates_baseline_metadata(tmp_path: Path) -> None:
    """RED: versions check should pass for valid baseline metadata."""

    baseline_path = tmp_path / "version-baseline.json"
    write_baseline(
        baseline_path,
        {
            "bun": "1.0.0",
            "python": "3.14.0",
            "turbo": "2.0.0",
            "typescript": "5.0.0",
        },
    )

    result = run_nurt_command(
        cwd=tmp_path,
        args=["versions", "check", "--baseline-path", str(baseline_path)],
    )

    assert result.returncode == 0, (
        "Expected versions check to pass for valid baseline metadata.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "baseline metadata is valid" in combined_output


def test_nurt_versions_update_from_source_file_writes_new_versions(
    tmp_path: Path,
) -> None:
    """RED: versions update should refresh metadata and print a diff summary."""

    baseline_path = tmp_path / "version-baseline.json"
    source_path = tmp_path / "latest-source.json"
    write_baseline(
        baseline_path,
        {
            "bun": "1.0.0",
            "python": "3.14.0",
            "turbo": "2.0.0",
            "typescript": "5.0.0",
        },
    )
    write_latest_source(
        source_path,
        {
            "bun": "1.3.10",
            "python": "3.14.3",
            "turbo": "2.8.16",
            "typescript": "5.9.3",
        },
    )

    result = run_nurt_command(
        cwd=tmp_path,
        args=[
            "versions",
            "update",
            "--baseline-path",
            str(baseline_path),
            "--source-file",
            str(source_path),
        ],
    )

    assert result.returncode == 0, (
        "Expected versions update to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "Updated version baseline metadata" in combined_output
    assert "bun: 1.0.0 -> 1.3.10" in combined_output
    assert "python: 3.14.0 -> 3.14.3" in combined_output

    updated = json.loads(baseline_path.read_text(encoding="utf-8"))
    managed_tools = updated["managed_tools"]
    assert managed_tools["bun"]["version"] == "1.3.10"
    assert managed_tools["python"]["version"] == "3.14.3"
    assert managed_tools["turbo"]["version"] == "2.8.16"
    assert managed_tools["typescript"]["version"] == "5.9.3"


def test_nurt_versions_check_latest_reports_stale_baseline(tmp_path: Path) -> None:
    """RED: versions check --check-latest should fail when baseline is stale."""

    baseline_path = tmp_path / "version-baseline.json"
    source_path = tmp_path / "latest-source.json"
    write_baseline(
        baseline_path,
        {
            "bun": "1.0.0",
            "python": "3.14.0",
            "turbo": "2.0.0",
            "typescript": "5.0.0",
        },
    )
    write_latest_source(
        source_path,
        {
            "bun": "1.3.10",
            "python": "3.14.3",
            "turbo": "2.8.16",
            "typescript": "5.9.3",
        },
    )

    result = run_nurt_command(
        cwd=tmp_path,
        args=[
            "versions",
            "check",
            "--check-latest",
            "--baseline-path",
            str(baseline_path),
            "--source-file",
            str(source_path),
        ],
    )

    assert result.returncode == 1, (
        "Expected versions check --check-latest to fail for stale baseline.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "Version baseline is out of date" in combined_output
    assert "bun: current=1.0.0 latest=1.3.10" in combined_output


def test_nurt_versions_update_dry_run_does_not_modify_baseline(tmp_path: Path) -> None:
    """RED: dry-run update should report planned changes without writing."""

    baseline_path = tmp_path / "version-baseline.json"
    source_path = tmp_path / "latest-source.json"
    write_baseline(
        baseline_path,
        {
            "bun": "1.0.0",
            "python": "3.14.0",
            "turbo": "2.0.0",
            "typescript": "5.0.0",
        },
    )
    before_text = baseline_path.read_text(encoding="utf-8")

    write_latest_source(
        source_path,
        {
            "bun": "1.3.10",
            "python": "3.14.3",
            "turbo": "2.8.16",
            "typescript": "5.9.3",
        },
    )

    result = run_nurt_command(
        cwd=tmp_path,
        args=[
            "versions",
            "update",
            "--dry-run",
            "--baseline-path",
            str(baseline_path),
            "--source-file",
            str(source_path),
        ],
    )

    assert result.returncode == 0, (
        "Expected versions update --dry-run to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "DRY RUN" in combined_output
    assert "bun: 1.0.0 -> 1.3.10" in combined_output

    after_text = baseline_path.read_text(encoding="utf-8")
    assert before_text == after_text, "dry-run must not modify baseline metadata"


def test_nurt_versions_check_lockfiles_fails_when_uv_lock_missing(
    tmp_path: Path,
) -> None:
    """RED: versions check should fail when required lockfile is missing."""

    baseline_path = tmp_path / "version-baseline.json"
    write_baseline(
        baseline_path,
        {
            "bun": "1.3.10",
            "python": "3.14.3",
            "turbo": "2.8.16",
            "typescript": "5.9.3",
        },
    )
    (tmp_path / "pyproject.toml").write_text(
        """
[build-system]
requires = ["uv_build>=0.10.12,<0.11.0"]
build-backend = "uv_build"

[project]
name = "demo"
version = "0.1.0"
requires-python = ">=3.14"
dependencies = []
""".strip()
        + "\n",
        encoding="utf-8",
    )

    result = run_nurt_command(
        cwd=tmp_path,
        args=[
            "versions",
            "check",
            "--baseline-path",
            str(baseline_path),
            "--check-lockfiles",
        ],
    )

    assert result.returncode == 1, (
        "Expected versions check --check-lockfiles to fail when uv.lock is missing.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "Missing required lockfiles" in combined_output
    assert "uv.lock" in combined_output


def test_nurt_versions_update_regenerates_uv_lockfile_and_reports_summary(
    tmp_path: Path,
) -> None:
    """RED: versions update should regenerate uv.lock and print summary."""

    baseline_path = tmp_path / "version-baseline.json"
    source_path = tmp_path / "latest-source.json"
    write_baseline(
        baseline_path,
        {
            "bun": "1.0.0",
            "python": "3.14.0",
            "turbo": "2.0.0",
            "typescript": "5.0.0",
        },
    )
    write_latest_source(
        source_path,
        {
            "bun": "1.3.10",
            "python": "3.14.3",
            "turbo": "2.8.16",
            "typescript": "5.9.3",
        },
    )
    (tmp_path / "pyproject.toml").write_text(
        """
[build-system]
requires = ["uv_build>=0.10.12,<0.11.0"]
build-backend = "uv_build"

[project]
name = "demo"
version = "0.1.0"
requires-python = ">=3.14"
dependencies = []
""".strip()
        + "\n",
        encoding="utf-8",
    )

    result = run_nurt_command(
        cwd=tmp_path,
        args=[
            "versions",
            "update",
            "--baseline-path",
            str(baseline_path),
            "--source-file",
            str(source_path),
        ],
    )

    assert result.returncode == 0, (
        "Expected versions update to regenerate uv.lock successfully.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "Lockfile regeneration summary" in combined_output
    assert "uv.lock" in combined_output
    assert (tmp_path / "uv.lock").exists(), "versions update should regenerate uv.lock"


def test_nurt_versions_update_dry_run_reports_lockfile_plan_without_writing(
    tmp_path: Path,
) -> None:
    """RED: dry-run update should report lockfile plan without creating lockfiles."""

    baseline_path = tmp_path / "version-baseline.json"
    source_path = tmp_path / "latest-source.json"
    write_baseline(
        baseline_path,
        {
            "bun": "1.0.0",
            "python": "3.14.0",
            "turbo": "2.0.0",
            "typescript": "5.0.0",
        },
    )
    write_latest_source(
        source_path,
        {
            "bun": "1.3.10",
            "python": "3.14.3",
            "turbo": "2.8.16",
            "typescript": "5.9.3",
        },
    )
    (tmp_path / "pyproject.toml").write_text(
        """
[build-system]
requires = ["uv_build>=0.10.12,<0.11.0"]
build-backend = "uv_build"

[project]
name = "demo"
version = "0.1.0"
requires-python = ">=3.14"
dependencies = []
""".strip()
        + "\n",
        encoding="utf-8",
    )

    result = run_nurt_command(
        cwd=tmp_path,
        args=[
            "versions",
            "update",
            "--dry-run",
            "--baseline-path",
            str(baseline_path),
            "--source-file",
            str(source_path),
        ],
    )

    assert result.returncode == 0, (
        "Expected versions update --dry-run lockfile plan to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    combined_output = f"{result.stdout}\n{result.stderr}"
    assert "DRY RUN: lockfile regeneration plan" in combined_output
    assert "uv.lock" in combined_output
    assert not (tmp_path / "uv.lock").exists(), "dry-run must not write uv.lock"
