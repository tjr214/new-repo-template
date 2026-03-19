from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath

from new_repo_template.snapshot_assets_loader import load_source_manifest


TEMPLATES_PREFIX = "templates/"
FOUNDATION_PREFIX = "templates/foundation/"


@dataclass(frozen=True)
class SourceManifestManagement:
    scaffold: bool = True
    sync: bool = False


@dataclass(frozen=True)
class SourceManifestEntry:
    source: str
    destination: str
    management: SourceManifestManagement


def _normalize_relative_path(path: str) -> str:
    normalized = str(PurePosixPath(path))
    pure_path = PurePosixPath(normalized)
    if normalized in {"", "."}:
        raise ValueError(f"manifest path must not be empty: {path!r}")
    if pure_path.is_absolute():
        raise ValueError(f"manifest path must be relative: {path!r}")
    if any(part == ".." for part in pure_path.parts):
        raise ValueError(f"manifest path must not escape its root: {path!r}")
    return normalized


def _parse_management(entry_obj: dict[str, object]) -> SourceManifestManagement:
    management_obj = entry_obj.get("management")
    if management_obj is None:
        return SourceManifestManagement()
    if not isinstance(management_obj, dict):
        raise ValueError("source manifest entry management must be an object")

    scaffold = management_obj.get("scaffold", True)
    sync = management_obj.get("sync", False)
    if not isinstance(scaffold, bool) or not isinstance(sync, bool):
        raise ValueError("source manifest entry management flags must be booleans")

    return SourceManifestManagement(scaffold=scaffold, sync=sync)


def get_source_manifest_entries(
    source_manifest: dict[str, object] | None = None,
) -> tuple[SourceManifestEntry, ...]:
    manifest = load_source_manifest() if source_manifest is None else source_manifest
    entries_obj = manifest.get("entries")
    if not isinstance(entries_obj, list):
        raise ValueError("source manifest must contain list field 'entries'")

    entries: list[SourceManifestEntry] = []
    for entry_obj in entries_obj:
        if not isinstance(entry_obj, dict):
            raise ValueError("source manifest entries must be objects")
        source = entry_obj.get("source")
        destination = entry_obj.get("destination")
        if not isinstance(source, str) or not isinstance(destination, str):
            raise ValueError(
                "source manifest entries require string source and destination"
            )
        entries.append(
            SourceManifestEntry(
                source=_normalize_relative_path(source),
                destination=_normalize_relative_path(destination),
                management=_parse_management(entry_obj),
            )
        )

    return tuple(entries)


def get_source_manifest_empty_directories(
    source_manifest: dict[str, object] | None = None,
) -> tuple[str, ...]:
    manifest = load_source_manifest() if source_manifest is None else source_manifest
    empty_directories_obj = manifest.get("empty_directories", [])
    if not isinstance(empty_directories_obj, list):
        raise ValueError("source manifest must contain list field 'empty_directories'")

    empty_directories: list[str] = []
    for directory_obj in empty_directories_obj:
        if not isinstance(directory_obj, str):
            raise ValueError("source manifest empty directories must be strings")
        empty_directories.append(_normalize_relative_path(directory_obj))

    return tuple(empty_directories)


def _strip_prefix(*, path: str, prefix: str) -> str:
    if not path.startswith(prefix):
        raise ValueError(f"manifest path {path!r} does not start with {prefix!r}")
    return path.removeprefix(prefix)


def _iter_parent_directories(path: str) -> tuple[str, ...]:
    parents: list[str] = []
    current = PurePosixPath(path).parent
    lineage: list[str] = []
    while str(current) != ".":
        lineage.append(str(current))
        current = current.parent
    parents.extend(reversed(lineage))
    return tuple(parents)


def get_foundation_template_file_pairs(
    source_manifest: dict[str, object] | None = None,
) -> tuple[tuple[str, str], ...]:
    pairs = [
        (
            _strip_prefix(path=entry.destination, prefix=FOUNDATION_PREFIX),
            _strip_prefix(path=entry.destination, prefix=TEMPLATES_PREFIX),
        )
        for entry in get_source_manifest_entries(source_manifest)
        if entry.management.scaffold and entry.destination.startswith(FOUNDATION_PREFIX)
    ]
    return tuple(sorted(pairs, key=lambda item: item[0]))


def get_foundation_sync_template_file_pairs(
    source_manifest: dict[str, object] | None = None,
) -> tuple[tuple[str, str], ...]:
    pairs = [
        (
            _strip_prefix(path=entry.destination, prefix=FOUNDATION_PREFIX),
            _strip_prefix(path=entry.destination, prefix=TEMPLATES_PREFIX),
        )
        for entry in get_source_manifest_entries(source_manifest)
        if entry.management.sync and entry.destination.startswith(FOUNDATION_PREFIX)
    ]

    return tuple(sorted(pairs, key=lambda item: item[0]))


def get_foundation_empty_directories(
    source_manifest: dict[str, object] | None = None,
) -> tuple[str, ...]:
    directories = [
        _strip_prefix(path=directory, prefix=FOUNDATION_PREFIX)
        for directory in get_source_manifest_empty_directories(source_manifest)
        if directory.startswith(FOUNDATION_PREFIX)
    ]
    return tuple(sorted(directories))


def get_foundation_scaffold_paths(
    source_manifest: dict[str, object] | None = None,
) -> tuple[str, ...]:
    directories: set[str] = set()
    files: set[str] = set()

    for destination_relative, _template_relative in get_foundation_template_file_pairs(
        source_manifest
    ):
        files.add(destination_relative)
        directories.update(_iter_parent_directories(destination_relative))

    for directory_relative in get_foundation_empty_directories(source_manifest):
        directories.add(directory_relative)
        directories.update(_iter_parent_directories(directory_relative))

    ordered_directories = sorted(
        directories,
        key=lambda path: (len(PurePosixPath(path).parts), path),
    )
    ordered_files = sorted(files)

    return tuple([*(f"{path}/" for path in ordered_directories), *ordered_files])


def build_runtime_snapshot_manifest(
    source_manifest: dict[str, object] | None = None,
) -> dict[str, object]:
    templates = sorted(
        _strip_prefix(path=entry.destination, prefix=TEMPLATES_PREFIX)
        for entry in get_source_manifest_entries(source_manifest)
        if entry.management.scaffold
    )
    return {
        "version": 1,
        "templates": templates,
    }
