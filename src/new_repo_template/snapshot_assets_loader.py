from __future__ import annotations

import json
from importlib.resources import files


ASSET_PACKAGE = "new_repo_template.snapshot_assets"


def load_snapshot_manifest() -> dict[str, object]:
    manifest_path = files(ASSET_PACKAGE).joinpath("manifest.json")
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def load_source_manifest() -> dict[str, object]:
    manifest_path = files(ASSET_PACKAGE).joinpath("source_manifest.json")
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def load_template_text(relative_path: str) -> str:
    template_path = files(f"{ASSET_PACKAGE}.templates").joinpath(relative_path)
    return template_path.read_text(encoding="utf-8")
