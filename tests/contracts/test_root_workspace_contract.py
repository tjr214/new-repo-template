from __future__ import annotations

import json
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


def _iter_relative_files(root: Path) -> list[Path]:
    return sorted(path.relative_to(root) for path in root.rglob("*") if path.is_file())


def test_foundation_dry_run_reports_workspace_root_config_files(tmp_path: Path) -> None:
    """RED: foundation dry-run should include package.json and turbo.json."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "foundation-workspace-dry-run"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "foundation",
            "--no-interactive",
            "--dry-run",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected foundation dry-run scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    combined_output = f"{result.stdout}\n{result.stderr}"
    expected_markers = [
        "package.json",
        "turbo.json",
        "AGENTS.md",
        "PLAN.md",
        "README.md",
        "ralph.config.yaml",
        "PROGRESS.md",
        ".nurt/repo.json",
        "docs/ARCHITECTURE.md",
        "docs/LIVING_DOCS.md",
        "docs/markdown-templates/",
        "docs/workflows/",
        ".github/workflows/ci.yml",
        ".agent/rules/",
        ".opencode/command/",
        ".opencode/command/repo-gh-make-n-merge-PR.md",
    ]

    for marker in expected_markers:
        assert marker in combined_output, f"Expected dry-run output to mention {marker}"


def test_foundation_scaffold_writes_workspace_config_and_cross_platform_scripts(
    tmp_path: Path,
) -> None:
    """RED: foundation scaffold should include workspace and turbo task wiring."""

    repo_root = Path(__file__).resolve().parents[2]
    output_dir = tmp_path / "foundation-workspace-output"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "foundation",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected foundation scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    root_package_json = output_dir / "package.json"
    root_turbo_json = output_dir / "turbo.json"

    assert root_package_json.exists(), "root package.json must exist"
    assert root_turbo_json.exists(), "root turbo.json must exist"

    package_data = json.loads(root_package_json.read_text(encoding="utf-8"))
    assert package_data.get("private") is True
    assert package_data.get("workspaces") == [
        "apps/*",
        "packages/*",
        "apps/*/*",
        "packages/*/*",
    ]

    scripts = package_data.get("scripts")
    assert isinstance(scripts, dict), "root scripts must be defined"
    assert scripts.get("dev") == "turbo run dev"
    assert scripts.get("build") == "turbo run build"
    assert scripts.get("test") == "turbo run test"
    assert scripts.get("lint") == "turbo run lint"
    assert scripts.get("typecheck") == "turbo run typecheck"

    for script_name in ("dev", "build", "test", "lint", "typecheck"):
        script_value = scripts.get(script_name, "")
        assert ".sh" not in script_value
        assert "powershell" not in script_value.lower()

    turbo_data = json.loads(root_turbo_json.read_text(encoding="utf-8"))
    tasks = turbo_data.get("tasks")
    assert isinstance(tasks, dict), "turbo tasks must be defined"

    for task_name in ("dev", "build", "test", "lint", "typecheck"):
        assert task_name in tasks, f"missing turbo task: {task_name}"

    dev_task = tasks["dev"]
    assert dev_task.get("cache") is False
    assert dev_task.get("persistent") is True


def test_foundation_scaffold_writes_governance_and_agent_assets(tmp_path: Path) -> None:
    """RED: foundation scaffold should include the governance asset baseline."""

    repo_root = Path(__file__).resolve().parents[2]
    source_manifest = json.loads(
        (
            repo_root
            / "src"
            / "new_repo_template"
            / "snapshot_assets"
            / "source_manifest.json"
        ).read_text(encoding="utf-8")
    )
    output_dir = tmp_path / "foundation-governance-output"

    result = run_scaffold_command(
        repo_root=repo_root,
        args=[
            "--target",
            "foundation",
            "--no-interactive",
            "--output",
            str(output_dir),
        ],
    )

    assert result.returncode == 0, (
        "Expected foundation scaffold command to succeed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )

    root_mirrors = (
        (repo_root / "btca.config.jsonc", output_dir / "btca.config.jsonc"),
        (repo_root / "AGENTS.md", output_dir / "AGENTS.md"),
        (
            repo_root / "docs" / "markdown-templates" / "PLAN.template.md",
            output_dir / "PLAN.md",
        ),
        (
            repo_root / "templates-snapshot-files" / "snapshot-readme-md.txt",
            output_dir / "README.md",
        ),
        (repo_root / "README.BMAD-GUIDE.md", output_dir / "README.BMAD-GUIDE.md"),
        (repo_root / "README.RALPH.md", output_dir / "README.RALPH.md"),
        (repo_root / "ralph.config.yaml", output_dir / "ralph.config.yaml"),
        (
            repo_root / "docs" / "markdown-templates" / "PROGRESS.template.md",
            output_dir / "PROGRESS.md",
        ),
        (
            repo_root / "templates-snapshot-files" / "snapshot-nurt-repo-json.txt",
            output_dir / ".nurt" / "repo.json",
        ),
        (
            repo_root / "templates-snapshot-files" / "snapshot-architecture-md.txt",
            output_dir / "docs" / "ARCHITECTURE.md",
        ),
        (
            repo_root / "templates-snapshot-files" / "snapshot-living-docs-md.txt",
            output_dir / "docs" / "LIVING_DOCS.md",
        ),
    )

    for source_path, destination_path in root_mirrors:
        assert destination_path.exists(), (
            f"Expected mirrored file at {destination_path}"
        )
        assert destination_path.read_text(encoding="utf-8") == source_path.read_text(
            encoding="utf-8"
        )

    mirrored_directories = (
        repo_root / "scripts",
        repo_root / "docs" / "markdown-templates",
        repo_root / "docs" / "tasks",
        repo_root / "docs" / "workflows",
        repo_root / ".github" / "workflows",
        repo_root / ".agent" / "rules",
        repo_root / ".agent" / "workflows" / "project",
        repo_root / ".opencode" / "command",
    )

    for source_root in mirrored_directories:
        for relative in _iter_relative_files(source_root):
            source_path = source_root / relative
            destination_path = output_dir / source_path.relative_to(repo_root)
            assert destination_path.exists(), (
                f"Expected mirrored file at {destination_path}"
            )
            assert destination_path.read_text(
                encoding="utf-8"
            ) == source_path.read_text(encoding="utf-8")

    empty_directories = source_manifest.get("empty_directories")
    assert isinstance(empty_directories, list)
    expected_empty_directories = sorted(
        directory.removeprefix("templates/foundation/")
        for directory in empty_directories
        if isinstance(directory, str) and directory.startswith("templates/foundation/")
    )
    assert expected_empty_directories, (
        "source manifest should declare foundation empty directories"
    )

    for relative_directory in expected_empty_directories:
        assert (output_dir / relative_directory).is_dir(), (
            f"Expected empty directory at {output_dir / relative_directory}"
        )

    assert (output_dir / "docs" / "markdown-templates").is_dir()
    assert (output_dir / ".github").is_dir()
    assert (output_dir / ".github" / "workflows").is_dir()
    assert not (output_dir / ".opencode" / "package.json").exists()
    assert not (output_dir / ".opencode" / "bun.lock").exists()
    assert not (output_dir / ".opencode" / "node_modules").exists()
