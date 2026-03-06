from __future__ import annotations

from pathlib import Path

from new_repo_template.sync_ops import _apply_template_sync


def _removed_root_doc_name() -> str:
    return "CLAUDE" + ".md"


def _removed_config_dir_name() -> str:
    return "." + "claude"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_apply_template_sync_excludes_removed_assistant_assets(tmp_path: Path) -> None:
    """RED: native template sync should not copy removed assistant assets."""

    clone_root = tmp_path / "clone"
    project_root = tmp_path / "project"
    project_root.mkdir(parents=True)

    _write(clone_root / "AGENTS.md", "# agents\n")
    removed_root_doc = _removed_root_doc_name()
    removed_config_dir = _removed_config_dir_name()

    _write(clone_root / removed_root_doc, "# assistant\n")
    _write(clone_root / removed_config_dir / "settings.json", "{}\n")
    _write(clone_root / removed_config_dir / "statusline-script.sh", "#!/bin/sh\n")
    _write(
        clone_root / removed_config_dir / "commands" / "repo" / "merge.md",
        "# merge\n",
    )
    _write(
        clone_root / ".template_scripts" / "update-template-from-git.sh", "#!/bin/sh\n"
    )
    _write(clone_root / ".opencode" / "command" / "example.md", "# opencode\n")
    _write(
        clone_root / ".agent" / "workflows" / "project" / "example.md", "# workflow\n"
    )
    _write(clone_root / ".agent" / "rules" / "example.md", "# rule\n")
    _write(clone_root / "docs" / "tasks" / "task-template.yaml", "name: task\n")
    _write(
        clone_root / "docs" / "tasks" / "task-template-example.yaml",
        "name: example\n",
    )
    _write(clone_root / "docs" / "workflows" / "guide.md", "# workflow doc\n")

    _apply_template_sync(clone_root, project_root)

    assert (project_root / "AGENTS.md").exists()
    assert (project_root / ".template_scripts" / "update-template-from-git.sh").exists()
    assert (project_root / ".opencode" / "command" / "example.md").exists()
    assert (project_root / ".agent" / "workflows" / "project" / "example.md").exists()
    assert (project_root / ".agent" / "rules" / "example.md").exists()
    assert (project_root / "docs" / "tasks" / "task-template.yaml").exists()
    assert (project_root / "docs" / "workflows" / "guide.md").exists()

    assert not (project_root / removed_root_doc).exists()
    assert not (project_root / removed_config_dir).exists()
