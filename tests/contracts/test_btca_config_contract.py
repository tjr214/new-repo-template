from __future__ import annotations

import json

from new_repo_template import btca_config_manager


def _resource_names(config_text: str) -> list[str]:
    payload = json.loads(config_text)
    return [resource["name"] for resource in payload["resources"]]


def _resource_by_name(config_text: str, resource_name: str) -> dict[str, object]:
    payload = json.loads(config_text)
    for resource in payload["resources"]:
        if resource["name"] == resource_name:
            return resource
    raise AssertionError(f"resource {resource_name!r} not found")


def _managed_names(sidecar_text: str) -> list[str]:
    payload = json.loads(sidecar_text)
    return [record["name"] for record in payload["managed_resources"]]


def test_generate_scaffold_btca_files_for_foundation_only() -> None:
    generated = btca_config_manager.generate_scaffold_btca_files(())

    assert _resource_names(generated.config_text) == ["turborepo", "bun"]
    assert _managed_names(generated.sidecar_text) == ["turborepo", "bun"]
    assert "<name>turborepo</name>" in generated.docs_text
    assert "<name>bun</name>" in generated.docs_text
    assert "<name>textual</name>" not in generated.docs_text


def test_generate_scaffold_btca_files_covers_direct_target_frameworks_and_tools() -> (
    None
):
    generated = btca_config_manager.generate_scaffold_btca_files(
        (
            btca_config_manager.ProjectContext(kind="python"),
            btca_config_manager.ProjectContext(kind="web"),
            btca_config_manager.ProjectContext(kind="backend", auth="clerk"),
            btca_config_manager.ProjectContext(kind="desktop"),
            btca_config_manager.ProjectContext(kind="mobile"),
            btca_config_manager.ProjectContext(kind="tv"),
            btca_config_manager.ProjectContext(kind="typescript-cli"),
            btca_config_manager.ProjectContext(kind="python-lib"),
        )
    )

    assert _resource_names(generated.config_text) == [
        "turborepo",
        "bun",
        "tanstack-router-start",
        "clerk-docs",
        "expo-docs",
        "react-native-tvos",
        "expo-tv-config",
        "convex-docs",
        "textual",
        "rich-docs",
        "uv",
        "react-docs",
        "react-native-docs",
        "vite",
        "electron-forge",
        "electron",
        "typescript-docs",
        "pytest",
        "ruff",
        "mypy",
        "react-native-qrcode-svg",
        "react-native-svg",
    ]


def test_generate_scaffold_btca_files_keeps_qr_resources_out_of_tv_only() -> None:
    generated = btca_config_manager.generate_scaffold_btca_files(
        (btca_config_manager.ProjectContext(kind="tv"),)
    )

    resource_names = _resource_names(generated.config_text)
    assert "react-native-qrcode-svg" not in resource_names
    assert "react-native-svg" not in resource_names


def test_merge_add_mode_btca_files_preserves_user_resource_and_adds_new_managed_ones() -> (
    None
):
    foundation = btca_config_manager.generate_scaffold_btca_files(())
    existing_payload = json.loads(foundation.config_text)
    existing_resources = list(existing_payload["resources"])
    existing_resources.append(
        {
            "type": "git",
            "name": "custom-docs",
            "url": "https://example.com/custom-docs",
            "branch": "main",
        }
    )
    existing_payload["resources"] = existing_resources

    merged = btca_config_manager.merge_add_mode_btca_files(
        existing_config_text=json.dumps(existing_payload, indent=2) + "\n",
        existing_sidecar_text=foundation.sidecar_text,
        projects=(btca_config_manager.ProjectContext(kind="desktop"),),
    )

    assert _resource_names(merged.config_text) == [
        "turborepo",
        "bun",
        "custom-docs",
        "electron-forge",
        "electron",
        "typescript-docs",
    ]
    assert _resource_by_name(merged.config_text, "custom-docs") == {
        "type": "git",
        "name": "custom-docs",
        "url": "https://example.com/custom-docs",
        "branch": "main",
    }
    assert _managed_names(merged.sidecar_text) == [
        "turborepo",
        "bun",
        "electron-forge",
        "electron",
        "typescript-docs",
    ]
    assert merged.warnings == ()


def test_merge_add_mode_btca_files_preserves_drifted_managed_resource_and_warns() -> (
    None
):
    foundation = btca_config_manager.generate_scaffold_btca_files(())
    existing_payload = json.loads(foundation.config_text)
    existing_payload["resources"][1]["url"] = "https://example.com/custom-bun-docs"

    merged = btca_config_manager.merge_add_mode_btca_files(
        existing_config_text=json.dumps(existing_payload, indent=2) + "\n",
        existing_sidecar_text=foundation.sidecar_text,
        projects=(btca_config_manager.ProjectContext(kind="desktop"),),
    )

    assert _resource_by_name(merged.config_text, "bun")["url"] == (
        "https://example.com/custom-bun-docs"
    )
    assert any("bun" in warning for warning in merged.warnings)


def test_generate_scaffold_btca_files_includes_better_auth_resources() -> None:
    generated = btca_config_manager.generate_scaffold_btca_files(
        (btca_config_manager.ProjectContext(kind="backend", auth="better-auth"),)
    )

    assert _resource_names(generated.config_text) == [
        "turborepo",
        "bun",
        "convex-better-auth",
        "better-auth-core",
        "convex-docs",
        "typescript-docs",
    ]
