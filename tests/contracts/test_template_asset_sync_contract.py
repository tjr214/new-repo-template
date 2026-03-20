from __future__ import annotations

import subprocess
from pathlib import Path

from new_repo_template.foundation_manifest import (
    get_foundation_sync_template_file_pairs,
)
from new_repo_template.repo_identity import render_repo_marker
from new_repo_template.snapshot_assets_loader import load_template_text
from new_repo_template.sync_ops import run_template_assets_sync


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _run_git(project_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )


def _init_committed_repo(project_root: Path) -> None:
    init_result = _run_git(project_root, "init")
    assert init_result.returncode == 0, (
        "Expected git init to succeed in test fixture.\n"
        f"stdout:\n{init_result.stdout}\n"
        f"stderr:\n{init_result.stderr}"
    )

    add_result = _run_git(project_root, "add", ".")
    assert add_result.returncode == 0, (
        "Expected git add to succeed in test fixture.\n"
        f"stdout:\n{add_result.stdout}\n"
        f"stderr:\n{add_result.stderr}"
    )

    commit_result = _run_git(
        project_root,
        "-c",
        "user.name=Test User",
        "-c",
        "user.email=test@example.com",
        "commit",
        "-m",
        "Initial commit",
    )
    assert commit_result.returncode == 0, (
        "Expected git commit to succeed in test fixture.\n"
        f"stdout:\n{commit_result.stdout}\n"
        f"stderr:\n{commit_result.stderr}"
    )


def _seed_repo_marker(project_root: Path) -> None:
    _write(project_root / ".nurt" / "repo.json", render_repo_marker())


def test_template_assets_sync_updates_manifest_managed_files_from_bundled_assets(
    tmp_path: Path,
) -> None:
    """RED: template sync should replace only manifest-managed files from bundled assets."""

    project_root = tmp_path / "project"
    project_root.mkdir(parents=True)
    _seed_repo_marker(project_root)

    sync_pairs = get_foundation_sync_template_file_pairs()
    assert sync_pairs, "expected manifest-derived sync targets"

    for destination, _template in sync_pairs:
        _write(project_root / destination, f"stale content for {destination}\n")

    _write(project_root / ".opencode" / "command" / "custom-command.md", "# custom\n")
    _write(project_root / ".agent" / "rules" / "custom-rule.md", "# custom rule\n")
    _write(
        project_root / "docs" / "workflows" / "custom" / "custom-workflow.md",
        "# custom workflow\n",
    )
    _write(project_root / "README.md", "# custom readme\n")
    _init_committed_repo(project_root)

    result = run_template_assets_sync(dry_run=False, project_root=project_root)

    assert result == 0
    for destination, template_relative in sync_pairs:
        assert (project_root / destination).read_text(
            encoding="utf-8"
        ) == load_template_text(template_relative)

    assert (project_root / ".opencode" / "command" / "custom-command.md").read_text(
        encoding="utf-8"
    ) == "# custom\n"
    assert (project_root / ".agent" / "rules" / "custom-rule.md").read_text(
        encoding="utf-8"
    ) == "# custom rule\n"
    assert (
        project_root / "docs" / "workflows" / "custom" / "custom-workflow.md"
    ).read_text(encoding="utf-8") == "# custom workflow\n"
    assert (project_root / "README.md").read_text(
        encoding="utf-8"
    ) == "# custom readme\n"


def test_template_assets_sync_does_not_delete_unlisted_files_or_create_empty_namespaces(
    tmp_path: Path,
) -> None:
    """RED: template sync should preserve unlisted files and avoid empty namespace creation."""

    project_root = tmp_path / "project"
    project_root.mkdir(parents=True)
    _seed_repo_marker(project_root)

    _write(project_root / "README.md", "# custom readme\n")
    _write(project_root / "PLAN.md", "# custom plan\n")
    _write(project_root / "PROGRESS.md", "# custom progress\n")
    _write(project_root / ".opencode" / "command" / "custom-only.md", "# custom\n")
    _write(project_root / ".agent" / "workflows" / "custom" / "note.md", "# note\n")
    _write(project_root / "docs" / "workflows" / "custom" / "note.md", "# note\n")
    _init_committed_repo(project_root)

    result = run_template_assets_sync(dry_run=False, project_root=project_root)

    assert result == 0
    assert (project_root / "README.md").read_text(
        encoding="utf-8"
    ) == "# custom readme\n"
    assert (project_root / "PLAN.md").read_text(encoding="utf-8") == "# custom plan\n"
    assert (project_root / "PROGRESS.md").read_text(
        encoding="utf-8"
    ) == "# custom progress\n"
    assert (project_root / ".opencode" / "command" / "custom-only.md").read_text(
        encoding="utf-8"
    ) == "# custom\n"
    assert (project_root / ".agent" / "workflows" / "custom" / "note.md").read_text(
        encoding="utf-8"
    ) == "# note\n"
    assert (project_root / "docs" / "workflows" / "custom" / "note.md").read_text(
        encoding="utf-8"
    ) == "# note\n"
    assert not (project_root / ".opencode" / "agent").exists()
    assert not (project_root / ".template_scripts").exists()
