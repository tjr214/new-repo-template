from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from new_repo_template.snapshot_assets_loader import load_source_manifest


FORBIDDEN_SEGMENTS = {".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache"}


@dataclass(frozen=True)
class SnapshotResult:
    copied_files: tuple[str, ...]
    metadata_path: Path | None


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _nurt_version() -> str:
    try:
        return version("nurt-ai")
    except PackageNotFoundError:
        return "0.0.0-dev"


def _git_commit(source_root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=source_root,
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except FileNotFoundError, subprocess.TimeoutExpired:
        return "unknown"

    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip() or "unknown"


def _is_forbidden_source_path(source_relative_path: str) -> bool:
    path_parts = Path(source_relative_path).parts
    return any(part in FORBIDDEN_SEGMENTS for part in path_parts)


def build_snapshot_assets(
    *,
    source_root: Path,
    output_root: Path,
    dry_run: bool,
    generated_at_iso: str | None = None,
    source_commit: str | None = None,
) -> SnapshotResult:
    manifest = load_source_manifest()
    entries_obj = manifest.get("entries")
    if not isinstance(entries_obj, list):
        raise ValueError("source manifest must contain list field 'entries'")

    copied_files: list[str] = []
    metadata_files: list[dict[str, str]] = []

    for entry in sorted(entries_obj, key=lambda item: str(item.get("destination", ""))):
        if not isinstance(entry, dict):
            raise ValueError("source manifest entries must be objects")

        source_relative = entry.get("source")
        destination_relative = entry.get("destination")
        if not isinstance(source_relative, str) or not isinstance(
            destination_relative, str
        ):
            raise ValueError(
                "source manifest entries require string source and destination"
            )

        if _is_forbidden_source_path(source_relative):
            raise ValueError(
                f"forbidden source path in snapshot manifest: {source_relative}"
            )

        source_path = (source_root / source_relative).resolve()
        if not source_path.exists() or not source_path.is_file():
            raise FileNotFoundError(f"snapshot source missing: {source_path}")

        destination_path = (output_root / destination_relative).resolve()
        if (
            output_root.resolve() not in destination_path.parents
            and destination_path != output_root.resolve()
        ):
            raise ValueError(
                f"snapshot destination escapes output root: {destination_relative}"
            )

        file_text = source_path.read_text(encoding="utf-8")
        metadata_files.append(
            {
                "destination": destination_relative,
                "sha256": _sha256_text(file_text),
            }
        )
        copied_files.append(destination_relative)

        if not dry_run:
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            destination_path.write_text(file_text, encoding="utf-8")

    metadata_time = generated_at_iso or datetime.now(timezone.utc).isoformat()
    commit = source_commit or _git_commit(source_root)
    metadata = {
        "generated_at": metadata_time,
        "source_commit": commit,
        "nurt_version": _nurt_version(),
        "file_count": len(metadata_files),
        "files": metadata_files,
    }

    metadata_path: Path | None = None
    if not dry_run:
        metadata_path = output_root / "metadata.json"
        metadata_path.write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    return SnapshotResult(copied_files=tuple(copied_files), metadata_path=metadata_path)
