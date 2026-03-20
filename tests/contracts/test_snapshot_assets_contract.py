from __future__ import annotations

import json
from pathlib import Path

from new_repo_template.foundation_manifest import (
    build_runtime_snapshot_manifest,
    get_foundation_sync_template_file_pairs,
    get_source_manifest_entries,
)
from new_repo_template.snapshot_assets_loader import (
    load_source_manifest,
    load_snapshot_manifest,
    load_template_text,
)
from new_repo_template.snapshot_builder import build_snapshot_assets


def test_packaged_snapshot_templates_are_loadable() -> None:
    """RED: packaged snapshot templates should all be available at runtime."""

    manifest = load_snapshot_manifest()
    templates = manifest.get("templates")
    assert isinstance(templates, list)
    assert templates, "snapshot manifest should include at least one template"

    for template_path in templates:
        assert isinstance(template_path, str)
        template_text = load_template_text(template_path)
        assert template_text != ""


def test_snapshot_builder_writes_deterministic_metadata(tmp_path: Path) -> None:
    """RED: snapshot generation should produce deterministic metadata for same inputs."""

    source_root = tmp_path / "source"
    source_root.mkdir(parents=True)
    source_manifest = load_source_manifest()
    entries = source_manifest.get("entries")
    assert isinstance(entries, list)

    for index, entry in enumerate(entries, start=1):
        assert isinstance(entry, dict)
        source_relative = entry.get("source")
        assert isinstance(source_relative, str)
        source_path = source_root / source_relative
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(
            f"snapshot fixture {index}: {source_relative}\n",
            encoding="utf-8",
        )

    output_a = tmp_path / "snapshot-a"
    output_b = tmp_path / "snapshot-b"
    fixed_time = "2026-03-01T00:00:00+00:00"
    fixed_commit = "abc123"

    result_a = build_snapshot_assets(
        source_root=source_root,
        output_root=output_a,
        dry_run=False,
        generated_at_iso=fixed_time,
        source_commit=fixed_commit,
    )
    result_b = build_snapshot_assets(
        source_root=source_root,
        output_root=output_b,
        dry_run=False,
        generated_at_iso=fixed_time,
        source_commit=fixed_commit,
    )

    assert result_a.metadata_path is not None
    assert result_b.metadata_path is not None

    metadata_a = json.loads(result_a.metadata_path.read_text(encoding="utf-8"))
    metadata_b = json.loads(result_b.metadata_path.read_text(encoding="utf-8"))

    assert metadata_a == metadata_b
    assert metadata_a["source_commit"] == fixed_commit
    assert metadata_a["generated_at"] == fixed_time

    manifest_a = json.loads((output_a / "manifest.json").read_text(encoding="utf-8"))
    manifest_b = json.loads((output_b / "manifest.json").read_text(encoding="utf-8"))
    assert manifest_a == manifest_b


def test_snapshot_builder_generates_runtime_manifest_from_source_entries(
    tmp_path: Path,
) -> None:
    """RED: template-assets validate should regenerate runtime manifest from source entries."""

    source_root = tmp_path / "source"
    source_root.mkdir(parents=True)
    source_manifest = load_source_manifest()
    entries = source_manifest.get("entries")
    assert isinstance(entries, list)

    for index, entry in enumerate(entries, start=1):
        assert isinstance(entry, dict)
        source_relative = entry.get("source")
        assert isinstance(source_relative, str)
        source_path = source_root / source_relative
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(
            f"snapshot fixture {index}: {source_relative}\n",
            encoding="utf-8",
        )

    output_root = tmp_path / "snapshot-output"
    result = build_snapshot_assets(
        source_root=source_root,
        output_root=output_root,
        dry_run=False,
        generated_at_iso="2026-03-01T00:00:00+00:00",
        source_commit="abc123",
    )

    assert result.metadata_path is not None

    manifest_path = output_root / "manifest.json"
    assert manifest_path.exists(), "runtime manifest should be written"
    runtime_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected_templates = sorted(
        entry["destination"].removeprefix("templates/")
        for entry in entries
        if isinstance(entry, dict) and isinstance(entry.get("destination"), str)
    )
    assert runtime_manifest == {"version": 1, "templates": expected_templates}


def test_snapshot_manifest_includes_foundation_opencode_commands_from_source_manifest() -> (
    None
):
    """RED: packaged snapshot manifest should include all foundation OpenCode command assets."""

    source_manifest = load_source_manifest()
    entries = source_manifest.get("entries")
    assert isinstance(entries, list)

    expected_templates = sorted(
        entry["destination"].removeprefix("templates/")
        for entry in entries
        if isinstance(entry, dict)
        and isinstance(entry.get("destination"), str)
        and entry["destination"].startswith("templates/foundation/.opencode/command/")
    )

    snapshot_manifest = load_snapshot_manifest()
    templates = snapshot_manifest.get("templates")
    assert isinstance(templates, list)

    actual_templates = sorted(
        template
        for template in templates
        if isinstance(template, str)
        and template.startswith("foundation/.opencode/command/")
    )

    assert actual_templates == expected_templates


def test_source_manifest_supports_management_metadata_without_breaking_runtime_manifest() -> (
    None
):
    """RED: source-manifest entries should support management metadata safely."""

    source_manifest = load_source_manifest()
    entries = get_source_manifest_entries(source_manifest)

    assert any(entry.management.sync for entry in entries)

    runtime_manifest = build_runtime_snapshot_manifest(source_manifest)
    expected_templates = sorted(
        entry.destination.removeprefix("templates/")
        for entry in entries
        if entry.management.scaffold
    )
    assert runtime_manifest == {"version": 1, "templates": expected_templates}


def test_source_manifest_derives_exact_foundation_sync_allowlist() -> None:
    """RED: foundation sync targets should come from manifest metadata only."""

    source_manifest = load_source_manifest()
    entries = get_source_manifest_entries(source_manifest)
    sync_pairs = get_foundation_sync_template_file_pairs(source_manifest)
    sync_destinations = {destination for destination, _template in sync_pairs}
    expected_sync_destinations = {
        entry.destination.removeprefix("templates/foundation/")
        for entry in entries
        if entry.management.sync
        and entry.destination.startswith("templates/foundation/")
    }

    assert sync_destinations == expected_sync_destinations
    assert ".opencode/command/project-archive-plan.md" in sync_destinations
    assert ".opencode/command/project-save-discussion-as-plan.md" in sync_destinations
    assert ".opencode/command/project-read-todo-features.md" in sync_destinations
    assert "docs/markdown-templates/PLAN.template.md" in sync_destinations
    assert "docs/markdown-templates/PROGRESS.template.md" in sync_destinations
    assert "docs/tasks/task-template.yaml" in sync_destinations
    assert "README.md" not in sync_destinations
    assert "PLAN.md" not in sync_destinations
    assert "PROGRESS.md" not in sync_destinations
