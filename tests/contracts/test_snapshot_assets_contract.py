from __future__ import annotations

import json
from pathlib import Path

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
